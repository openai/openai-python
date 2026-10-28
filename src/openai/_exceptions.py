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
            code = body.get("code")
            self.code = str(code) if code is not None else None
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
    status_code: Literal[400] = 400


class AuthenticationError(APIStatusError):
    status_code: Literal[401] = 401


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
    status_code: Literal[403] = 403


class NotFoundError(APIStatusError):
    status_code: Literal[404] = 404


class ConflictError(APIStatusError):
    status_code: Literal[409] = 409


class UnprocessableEntityError(APIStatusError):
    status_code: Literal[422] = 422


class RateLimitError(APIStatusError):
    status_code: Literal[429] = 429


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
    completion: ChatCompletion | None
    """The completion that caused this error, if provided.

    When streaming, this is the accumulated completion and may not include usage.
    """

    def __init__(self, *, completion: ChatCompletion | None = None) -> None:
        super().__init__(
            "Could not parse response content as the request was rejected by the content filter",
        )
        self.completion = completion


class InvalidWebhookSignatureError(ValueError):
    """Raised when a webhook signature is invalid, meaning the computed signature does not match the expected signature."""


class _WebSocketRecoveryData:
    __slots__ = ("frames", "messages")

    def __init__(self, frames: list[str] | list[str | bytes], messages: list[str]) -> None:
        self.frames = frames
        self.messages = messages

    @override
    def __repr__(self) -> str:
        return "<redacted WebSocket recovery data>"


class WebSocketConnectionClosedError(OpenAIError):
    """Raised when a WebSocket connection closes with unsent messages.

    `unsent_frames` preserves the text and binary frames in their original order.
    `unsent_messages` retains the text messages, including UTF-8 binary frames
    represented as text for compatibility.
    """

    def __init__(self, message: str, *, unsent_messages: list[str] | list[str | bytes]) -> None:
        super().__init__(message)
        messages: list[str]
        if all(isinstance(data, str) for data in unsent_messages):
            messages = cast("list[str]", unsent_messages)
        else:
            messages = []
            for data in unsent_messages:
                if isinstance(data, str):
                    messages.append(data)
                else:
                    try:
                        messages.append(data.decode("utf-8"))
                    except UnicodeDecodeError:
                        # Opaque binary remains available in unsent_frames.
                        pass
        # Keep raw lists out of ordinary exception-attribute snapshots.
        # Explicit recovery access remains available through the properties.
        self._recovery = _WebSocketRecoveryData(unsent_messages, messages)

    @property
    def unsent_messages(self) -> list[str]:
        return self._recovery.messages

    @unsent_messages.setter
    def unsent_messages(self, messages: list[str]) -> None:
        if hasattr(self, "_recovery"):
            self._recovery.messages = messages
        else:
            # Subclasses could assign the original writable field before super().__init__.
            self._recovery = _WebSocketRecoveryData([], messages)

    @property
    def unsent_frames(self) -> list[str] | list[str | bytes]:
        return self._recovery.frames

    @unsent_frames.setter
    def unsent_frames(self, frames: list[str] | list[str | bytes]) -> None:
        self._recovery.frames = frames


class WebSocketQueueFullError(OpenAIError):
    """Raised when the outgoing WebSocket message queue exceeds its byte-size limit."""

    pass
