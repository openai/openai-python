from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, cast
from typing_extensions import Literal, override

import httpx2

from ._utils import is_dict
from ._models import construct_type
from .types.shared.oauth_error_code import OAuthErrorCode

if TYPE_CHECKING:
    from .types.chat import ChatCompletion

__all__ = [
    "BadRequestError",
    "AuthenticationError",
    "OAuthError",
    "PermissionDeniedError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    "LengthFinishReasonError",
    "ContentFilterFinishReasonError",
    "InvalidWebhookSignatureError",
    "SubjectTokenProviderError",
    "WebSocketConnectionClosedError",
    "WebSocketQueueFullError",
]

_RequestSnapshot = tuple[str, str, list[tuple[bytes, bytes]], bytes | None]
_ResponseSnapshot = tuple[int, list[tuple[bytes, bytes]], bytes | None, _RequestSnapshot | None]


class OpenAIError(Exception):
    @override
    def __reduce__(self) -> tuple[object, tuple[object, ...]]:
        state = self.__dict__.copy()

        request_snapshot: _RequestSnapshot | None = None
        request = state.get("request")
        if isinstance(request, httpx2.Request):
            request_snapshot = _snapshot_request(request)
            del state["request"]

        response_snapshot: _ResponseSnapshot | None = None
        response = state.get("response")
        if isinstance(response, httpx2.Response):
            response_snapshot = _snapshot_response(response)
            del state["response"]

        return (
            _reconstruct_openai_error,
            (type(self), self.args, state, request_snapshot, response_snapshot),
        )


def _snapshot_request(request: httpx2.Request) -> _RequestSnapshot:
    try:
        content = request.content
    except httpx2.RequestNotRead:
        content = None

    return (request.method, str(request.url), list(request.headers.raw), content)


def _restore_request(snapshot: _RequestSnapshot) -> httpx2.Request:
    method, url, headers, content = snapshot
    if content is None:
        return httpx2.Request(method, url, headers=headers)
    return httpx2.Request(method, url, headers=headers, content=content)


def _snapshot_response(response: httpx2.Response) -> _ResponseSnapshot:
    try:
        content = response.content
    except httpx2.ResponseNotRead:
        content = None

    try:
        request_snapshot = _snapshot_request(response.request)
    except RuntimeError:
        request_snapshot = None

    return (response.status_code, list(response.headers.raw), content, request_snapshot)


def _restore_response(
    snapshot: _ResponseSnapshot,
    *,
    request: httpx2.Request | None,
) -> httpx2.Response:
    status_code, headers, content, response_request_snapshot = snapshot
    if request is None and response_request_snapshot is not None:
        request = _restore_request(response_request_snapshot)

    kwargs: dict[str, Any] = {"headers": headers}
    if content is not None:
        kwargs["content"] = content
    if request is not None:
        kwargs["request"] = request

    return httpx2.Response(status_code, **kwargs)


def _reconstruct_openai_error(
    error_type: type[OpenAIError],
    args: tuple[object, ...],
    state: dict[str, Any],
    request_snapshot: _RequestSnapshot | None,
    response_snapshot: _ResponseSnapshot | None,
) -> OpenAIError:
    error = Exception.__new__(error_type)
    Exception.__init__(error, *args)
    error.__dict__.update(state)

    request = _restore_request(request_snapshot) if request_snapshot is not None else None
    if request is not None:
        error.__dict__["request"] = request
    if response_snapshot is not None:
        error.__dict__["response"] = _restore_response(response_snapshot, request=request)

    return error


class SubjectTokenProviderError(OpenAIError):
    response: httpx2.Response | None

    def __init__(self, message: str, *, response: httpx2.Response | None = None) -> None:
        super().__init__(message)
        self.response = response


class APIError(OpenAIError):
    message: str
    request: httpx2.Request

    body: object | None
    """The API response body.

    If the API responded with a valid JSON structure then this property will be the
    decoded result.

    If it isn't a valid JSON structure then this will be the raw response.

    If there was no response associated with this error then it will be `None`.
    """

    code: Optional[str] = None
    param: Optional[str] = None
    type: Optional[str]

    def __init__(self, message: str, request: httpx2.Request, *, body: object | None) -> None:
        super().__init__(message)
        self.request = request
        self.message = message
        self.body = body

        if is_dict(body):
            self.code = cast(Any, construct_type(type_=Optional[str], value=body.get("code")))
            self.param = cast(Any, construct_type(type_=Optional[str], value=body.get("param")))
            self.type = cast(Any, construct_type(type_=str, value=body.get("type")))
        else:
            self.code = None
            self.param = None
            self.type = None


class APIResponseValidationError(APIError):
    response: httpx2.Response
    status_code: int

    def __init__(self, response: httpx2.Response, body: object | None, *, message: str | None = None) -> None:
        super().__init__(message or "Data returned by API invalid for expected schema.", response.request, body=body)
        self.response = response
        self.status_code = response.status_code


class APIStatusError(APIError):
    """Raised when an API response has a status code of 4xx or 5xx."""

    response: httpx2.Response
    status_code: int
    request_id: str | None

    def __init__(self, message: str, *, response: httpx2.Response, body: object | None) -> None:
        super().__init__(message, response.request, body=body)
        self.response = response
        self.status_code = response.status_code
        self.request_id = response.headers.get("x-request-id")


class APIConnectionError(APIError):
    def __init__(self, *, message: str = "Connection error.", request: httpx2.Request) -> None:
        super().__init__(message, request, body=None)


class APITimeoutError(APIConnectionError):
    def __init__(self, request: httpx2.Request) -> None:
        super().__init__(message="Request timed out.", request=request)


class BadRequestError(APIStatusError):
    status_code: Literal[400] = 400  # pyright: ignore[reportIncompatibleVariableOverride]


class AuthenticationError(APIStatusError):
    status_code: Literal[401] = 401  # pyright: ignore[reportIncompatibleVariableOverride]


class OAuthError(AuthenticationError):
    error: Optional[OAuthErrorCode]

    def __init__(self, *, response: httpx2.Response, body: object | None) -> None:
        message = "OAuth authentication error."
        error = None

        if is_dict(body):
            error = body.get("error")
            description = body.get("error_description")
            if description and isinstance(description, str):
                message = description

        super().__init__(message, response=response, body=body)
        self.error = cast(Optional[OAuthErrorCode], error)


class PermissionDeniedError(APIStatusError):
    status_code: Literal[403] = 403  # pyright: ignore[reportIncompatibleVariableOverride]


class NotFoundError(APIStatusError):
    status_code: Literal[404] = 404  # pyright: ignore[reportIncompatibleVariableOverride]


class ConflictError(APIStatusError):
    status_code: Literal[409] = 409  # pyright: ignore[reportIncompatibleVariableOverride]


class UnprocessableEntityError(APIStatusError):
    status_code: Literal[422] = 422  # pyright: ignore[reportIncompatibleVariableOverride]


class RateLimitError(APIStatusError):
    status_code: Literal[429] = 429  # pyright: ignore[reportIncompatibleVariableOverride]


class InternalServerError(APIStatusError):
    pass


class LengthFinishReasonError(OpenAIError):
    completion: ChatCompletion
    """The completion that caused this error.

    Note: this will *not* be a complete `ChatCompletion` object when streaming as `usage`
          will not be included.
    """

    def __init__(self, *, completion: ChatCompletion) -> None:
        msg = "Could not parse response content as the length limit was reached"
        if completion.usage:
            msg += f" - {completion.usage}"

        super().__init__(msg)
        self.completion = completion


class ContentFilterFinishReasonError(OpenAIError):
    def __init__(self) -> None:
        super().__init__(
            f"Could not parse response content as the request was rejected by the content filter",
        )


class InvalidWebhookSignatureError(ValueError):
    """Raised when a webhook signature is invalid, meaning the computed signature does not match the expected signature."""


class WebSocketConnectionClosedError(OpenAIError):
    """Raised when a WebSocket connection closes with unsent messages."""

    unsent_messages: list[str]

    def __init__(self, message: str, *, unsent_messages: list[str]) -> None:
        super().__init__(message)
        self.unsent_messages = unsent_messages


class WebSocketQueueFullError(OpenAIError):
    """Raised when the outgoing WebSocket message queue exceeds its byte-size limit."""

    pass
