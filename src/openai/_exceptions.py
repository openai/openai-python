# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Optional, cast
from typing_extensions import Literal

import httpx

from ._utils import is_dict
from ._models import construct_type

if TYPE_CHECKING:
    from .types.chat import ChatCompletion

__all__ = [
    "BadRequestError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    "LengthFinishReasonError",
    "ContentFilterFinishReasonError",
    "ContentFormatError",
    "InvalidWebhookSignatureError",
]


class OpenAIError(Exception):
    pass


class APIError(OpenAIError):
    message: str
    request: httpx.Request

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

    def __init__(self, message: str, request: httpx.Request, *, body: object | None) -> None:
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
    response: httpx.Response
    status_code: int

    def __init__(self, response: httpx.Response, body: object | None, *, message: str | None = None) -> None:
        super().__init__(message or "Data returned by API invalid for expected schema.", response.request, body=body)
        self.response = response
        self.status_code = response.status_code


class APIStatusError(APIError):
    """Raised when an API response has a status code of 4xx or 5xx."""

    response: httpx.Response
    status_code: int
    request_id: str | None

    def __init__(self, message: str, *, response: httpx.Response, body: object | None) -> None:
        super().__init__(message, response.request, body=body)
        self.response = response
        self.status_code = response.status_code
        self.request_id = response.headers.get("x-request-id")


class APIConnectionError(APIError):
    def __init__(self, *, message: str = "Connection error.", request: httpx.Request) -> None:
        super().__init__(message, request, body=None)


class APITimeoutError(APIConnectionError):
    def __init__(self, request: httpx.Request) -> None:
        super().__init__(message="Request timed out.", request=request)


class BadRequestError(APIStatusError):
    status_code: Literal[400] = 400  # pyright: ignore[reportIncompatibleVariableOverride]


class AuthenticationError(APIStatusError):
    status_code: Literal[401] = 401  # pyright: ignore[reportIncompatibleVariableOverride]


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


class ContentFormatError(OpenAIError):
    """Raised when the API returns content that cannot be parsed into the expected response format.

    This typically happens when the model returns malformed or truncated JSON that
    does not match the expected schema for the response type (for example, a Pydantic
    model or dataclass validated via `pydantic.TypeAdapter`).
    """

    raw_content: str
    """The raw content string returned by the API that failed to parse."""

    def __init__(self, *, raw_content: str, error: Exception, response_format: object | None = None) -> None:
        expected_response_format = _response_format_name(response_format)
        expected_details = (
            f" Expected response format: {expected_response_format}." if expected_response_format is not None else ""
        )
        truncated_content = raw_content[:200] + "..." if len(raw_content) > 200 else raw_content
        super().__init__(
            f"Could not parse response content as the response did not match the expected format."
            f"{expected_details} Raw content: {truncated_content!r}."
            f" Validation error: {_format_parse_error(error)}."
        )
        self.raw_content = raw_content
        self.expected_response_format = expected_response_format
        self.error = error


def _response_format_name(response_format: object | None) -> str | None:
    if response_format is None:
        return None
    return cast(
        str,
        getattr(response_format, "__name__", None)
        or getattr(response_format, "__qualname__", None)
        or repr(response_format),
    )


def _format_parse_error(error: Exception) -> str:
    if isinstance(error, json.JSONDecodeError):
        return f"{error.msg} (line {error.lineno}, column {error.colno})"

    errors_fn = getattr(error, "errors", None)
    if callable(errors_fn):
        try:
            return repr(errors_fn(include_input=False))
        except TypeError:
            return repr(errors_fn())

    return str(error)


class InvalidWebhookSignatureError(ValueError):
    """Raised when a webhook signature is invalid, meaning the computed signature does not match the expected signature."""
