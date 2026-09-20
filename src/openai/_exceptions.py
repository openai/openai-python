from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, cast
from typing_extensions import Literal

import httpx2

from ._utils import is_dict
from ._models import construct_type
from .types.shared.oauth_error_code import OAuthErrorCode

if TYPE_CHECKING:
    from .types.chat import ChatCompletion
    from .types.responses.response import Response

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
    "ResponseNotCompletedError",
    "ResponseFailedError",
    "ResponseIncompleteError",
    "InvalidWebhookSignatureError",
    "SubjectTokenProviderError",
    "WebSocketConnectionClosedError",
    "WebSocketQueueFullError",
]


class OpenAIError(Exception):
    pass


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


class ResponseNotCompletedError(OpenAIError):
    """A Response reached a final state other than `completed`.

    Carries no HTTP status code: the request that surfaced the failure succeeded.
    """

    response: Response

    retryable: bool
    """Whether submitting a new `create()` call is worth trying.

    Never means re-`retrieve()`ing this id, which is immutable once terminal.
    """

    def __init__(self, message: str, *, response: Response, retryable: bool) -> None:
        super().__init__(message)
        self.response = response
        self.retryable = retryable

    @property
    def request_id(self) -> str | None:
        return getattr(self.response, "_request_id", None)


class ResponseFailedError(ResponseNotCompletedError):
    """A Response finished with `status="failed"`."""

    code: Optional[str]
    """`response.error.code`, or `None` when the API reported no error object."""

    def __init__(self, message: str, *, response: Response, code: Optional[str], retryable: bool) -> None:
        super().__init__(message, response=response, retryable=retryable)
        self.code = code


class ResponseIncompleteError(ResponseNotCompletedError):
    """A Response finished with `status="incomplete"`.

    Not necessarily a failure: a run that stopped at `max_output_tokens` still
    produced output on `.response.output`.
    """

    reason: Optional[str]
    """`response.incomplete_details.reason`, or `None` when the API reported no reason."""

    def __init__(self, message: str, *, response: Response, reason: Optional[str], retryable: bool) -> None:
        super().__init__(message, response=response, retryable=retryable)
        self.reason = reason


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
