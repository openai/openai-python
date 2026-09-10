from __future__ import annotations

from typing import Any, cast
from unittest import mock
from typing_extensions import TypeAlias

import httpx2
import pytest

from openai import BadRequestError, InternalServerError
from openai._models import construct_type_unchecked
from openai.lib._responses import (
    RESPONSE_ERROR_CODE_TO_EXCEPTION,
    INCOMPLETE_DETAILS_REASON_TO_EXCEPTION,
    exception_for_background_failure,
)
from openai.types.responses.response import Response
from openai.resources.responses.responses import Responses, AsyncResponses

ResponsesResource: TypeAlias = Responses | AsyncResponses
RESPONSE_ID = "resp-synthetic"

ALL_ERROR_CODES = sorted(RESPONSE_ERROR_CODE_TO_EXCEPTION)
ALL_INCOMPLETE_REASONS = sorted(INCOMPLETE_DETAILS_REASON_TO_EXCEPTION)


@pytest.fixture(params=[Responses, AsyncResponses])
def resource(request: pytest.FixtureRequest) -> ResponsesResource:
    resource_type = cast("type[ResponsesResource]", request.param)
    return resource_type(cast(Any, mock.Mock()))


def make_response(
    status: str,
    *,
    error: dict[str, Any] | None = None,
    incomplete_details: dict[str, Any] | None = None,
) -> Response:
    return construct_type_unchecked(
        type_=Response,
        value={"id": RESPONSE_ID, "status": status, "error": error, "incomplete_details": incomplete_details},
    )


def raw_response(*args: Any, **kwargs: Any) -> mock.Mock:
    http_response = httpx2.Response(
        200, request=httpx2.Request("GET", f"https://api.openai.com/v1/responses/{RESPONSE_ID}")
    )
    return mock.Mock(http_response=http_response, parse=mock.Mock(return_value=make_response(*args, **kwargs)))


def patch_get(resource: ResponsesResource, result: mock.Mock) -> mock._patch[Any]:
    if isinstance(resource, AsyncResponses):
        return mock.patch.object(resource, "_get", new=mock.AsyncMock(return_value=result))
    return mock.patch.object(resource, "_get", return_value=result)


async def retrieve(resource: ResponsesResource, **kwargs: Any) -> Response:
    if isinstance(resource, AsyncResponses):
        return cast(Response, await resource.retrieve(RESPONSE_ID, **kwargs))
    return cast(Response, resource.retrieve(RESPONSE_ID, **kwargs))


def test_every_error_code_is_covered() -> None:
    assert set(RESPONSE_ERROR_CODE_TO_EXCEPTION) == {
        "server_error",
        "rate_limit_exceeded",
        "invalid_prompt",
        "data_residency_mismatch",
        "bio_policy",
        "vector_store_timeout",
        "invalid_image",
        "invalid_image_format",
        "invalid_base64_image",
        "invalid_image_url",
        "image_too_large",
        "image_too_small",
        "image_parse_error",
        "image_content_policy_violation",
        "invalid_image_mode",
        "image_file_too_large",
        "unsupported_image_media_type",
        "empty_image_file",
        "failed_to_download_image",
        "image_file_not_found",
    }


def test_every_incomplete_reason_is_covered() -> None:
    assert set(INCOMPLETE_DETAILS_REASON_TO_EXCEPTION) == {"max_output_tokens", "content_filter"}


@pytest.mark.parametrize("code", ALL_ERROR_CODES)
def test_every_mapped_error_code_raises_its_class(code: str) -> None:
    mapping = RESPONSE_ERROR_CODE_TO_EXCEPTION[code]
    response = make_response("failed", error={"code": code, "message": f"synthetic failure for {code}"})

    exc = exception_for_background_failure(raw_response("failed"), response)

    assert exc is not None
    assert type(exc) is mapping.exception_class
    assert getattr(exc, "retryable", None) is mapping.retryable
    assert exc.message == f"synthetic failure for {code}"


@pytest.mark.parametrize("reason", ALL_INCOMPLETE_REASONS)
def test_every_mapped_incomplete_reason(reason: str) -> None:
    mapping = INCOMPLETE_DETAILS_REASON_TO_EXCEPTION[reason]
    response = make_response("incomplete", incomplete_details={"reason": reason})

    exc = exception_for_background_failure(raw_response("incomplete"), response)

    if mapping.exception_class is None:
        assert exc is None
    else:
        assert exc is not None
        assert type(exc) is mapping.exception_class
        assert getattr(exc, "retryable", None) is mapping.retryable


def test_unmapped_failure_code_falls_back_to_internal_server_error() -> None:
    response = make_response("failed", error={"code": "a_future_code_the_sdk_does_not_know_yet", "message": "mystery"})

    exc = exception_for_background_failure(raw_response("failed"), response)

    assert isinstance(exc, InternalServerError)
    assert getattr(exc, "retryable", None) is True


def test_unmapped_incomplete_reason_does_not_raise() -> None:
    response = make_response("incomplete", incomplete_details={"reason": "a_future_reason_the_sdk_does_not_know_yet"})

    assert exception_for_background_failure(raw_response("incomplete"), response) is None


def test_failed_without_error_object_does_not_raise() -> None:
    response = make_response("failed", error=None)

    assert exception_for_background_failure(raw_response("failed"), response) is None


def test_incomplete_without_details_does_not_raise() -> None:
    response = make_response("incomplete", incomplete_details=None)

    assert exception_for_background_failure(raw_response("incomplete"), response) is None


def test_incomplete_with_empty_reason_does_not_raise() -> None:
    response = make_response("incomplete", incomplete_details={"reason": None})

    assert exception_for_background_failure(raw_response("incomplete"), response) is None


@pytest.mark.parametrize("status", ["completed", "cancelled", "queued", "in_progress"])
def test_non_failure_statuses_do_not_raise(status: str) -> None:
    assert exception_for_background_failure(raw_response(status), make_response(status)) is None


# ---------------------------------------------------------------------------
# Responses.retrieve() / AsyncResponses.retrieve() wiring
# ---------------------------------------------------------------------------


async def test_completed_run_returns_normally(resource: ResponsesResource) -> None:
    terminal = raw_response("completed")
    with patch_get(resource, terminal):
        assert await retrieve(resource) is terminal.parse.return_value


async def test_cancelled_run_returns_normally(resource: ResponsesResource) -> None:
    terminal = raw_response("cancelled")
    with patch_get(resource, terminal):
        assert await retrieve(resource) is terminal.parse.return_value


async def test_incomplete_max_output_tokens_returns_normally(resource: ResponsesResource) -> None:
    terminal = raw_response("incomplete", incomplete_details={"reason": "max_output_tokens"})
    with patch_get(resource, terminal):
        assert await retrieve(resource) is terminal.parse.return_value


async def test_incomplete_content_filter_raises(resource: ResponsesResource) -> None:
    terminal = raw_response("incomplete", incomplete_details={"reason": "content_filter"})
    with patch_get(resource, terminal):
        with pytest.raises(BadRequestError):
            await retrieve(resource)


@pytest.mark.parametrize("code", ALL_ERROR_CODES)
async def test_failed_run_raises_mapped_exception(resource: ResponsesResource, code: str) -> None:
    mapping = RESPONSE_ERROR_CODE_TO_EXCEPTION[code]
    assert mapping.exception_class is not None  # every entry in this table maps to a real exception
    terminal = raw_response("failed", error={"code": code, "message": f"synthetic failure for {code}"})

    with patch_get(resource, terminal):
        with pytest.raises(mapping.exception_class):
            await retrieve(resource)


async def test_failed_run_with_unmapped_code_raises_internal_server_error(resource: ResponsesResource) -> None:
    terminal = raw_response("failed", error={"code": "a_future_code_the_sdk_does_not_know_yet", "message": "mystery"})

    with patch_get(resource, terminal):
        with pytest.raises(InternalServerError) as excinfo:
            await retrieve(resource)
    assert getattr(excinfo.value, "retryable", None) is True
