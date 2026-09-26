from __future__ import annotations

import json
from typing import Any, cast
from typing_extensions import Literal, TypeAlias, get_args

import httpx2
import pytest

from openai import (
    OpenAI,
    AsyncOpenAI,
    OpenAIError,
    APIStatusError,
    ResponseFailedError,
    ResponseIncompleteError,
    ResponseNotCompletedError,
)
from openai.lib import raise_for_status
from tests.respx2 import MockRouter
from openai._models import add_request_id, construct_type_unchecked
from openai.types.responses.response import Response, IncompleteDetails
from openai.types.responses.response_error import ResponseError
from openai.types.responses.response_status import ResponseStatus

from ..conftest import base_url

RESPONSE_ID = "resp_synthetic"
RETRIEVE_PATH = f"{str(base_url).rstrip('/')}/responses/{RESPONSE_ID}"

# Pulled from the generated models so that a spec change shows up here as a test
# failure rather than as silently unclassified behaviour.
ERROR_CODES: tuple[str, ...] = get_args(ResponseError.model_fields["code"].annotation)
INCOMPLETE_REASONS: tuple[str, ...] = tuple(
    arg for arg in get_args(get_args(IncompleteDetails.model_fields["reason"].annotation)[0]) if isinstance(arg, str)
)
ALL_STATUSES: tuple[str, ...] = get_args(ResponseStatus)

# The only codes where creating the run again is worth trying. Spelled out here
# rather than imported so this file pins the contract instead of mirroring it.
RETRYABLE_CODES = frozenset({"server_error", "rate_limit_exceeded", "vector_store_timeout"})

UNKNOWN_ERROR_CODE = "a_future_code_the_sdk_does_not_know_yet"
UNKNOWN_INCOMPLETE_REASON = "a_future_reason_the_sdk_does_not_know_yet"


def response_body(
    status: str,
    *,
    error: dict[str, Any] | None = None,
    incomplete_details: dict[str, Any] | None = None,
    background: bool = True,
) -> dict[str, Any]:
    """A wire-shaped `Response` payload, valid under strict response validation."""
    return {
        "id": RESPONSE_ID,
        "object": "response",
        "created_at": 1754925861,
        "model": "gpt-5",
        "output": [],
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
        "status": status,
        "background": background,
        "error": error,
        "incomplete_details": incomplete_details,
    }


def make_response(status: str, **kwargs: Any) -> Response:
    # `construct_type_unchecked` so tests can build values the current spec does
    # not declare, e.g. an error code the SDK has never seen.
    return construct_type_unchecked(type_=Response, value=response_body(status, **kwargs))


def failure(code: str, message: str = "synthetic failure") -> Response:
    return make_response("failed", error={"code": code, "message": message})


# ---------------------------------------------------------------------------
# Statuses that must never raise
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status", [s for s in ALL_STATUSES if s not in ("failed", "incomplete")])
def test_non_failure_statuses_never_raise(status: str) -> None:
    """`completed`, `cancelled`, `queued` and `in_progress` are not failures.

    `cancelled` in particular is caller-initiated, so it stays a normal return.
    """
    raise_for_status(make_response(status), raise_on_incomplete=True)


def test_status_none_does_not_raise() -> None:
    """`Response.status` is optional; a payload without one is not a failure."""
    raise_for_status(construct_type_unchecked(type_=Response, value={"id": RESPONSE_ID}), raise_on_incomplete=True)


def test_status_is_the_authority_not_the_error_field() -> None:
    """A stale `error` object on a non-failed response must not trigger a raise."""
    completed = make_response("completed", error={"code": "server_error", "message": "stale"})

    raise_for_status(completed, raise_on_incomplete=True)


def test_unknown_future_status_does_not_raise() -> None:
    """Only the two statuses the helper documents are classified."""
    raise_for_status(make_response("a_future_status"), raise_on_incomplete=True)


# ---------------------------------------------------------------------------
# status="failed"
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("code", ERROR_CODES)
def test_every_declared_error_code_raises(code: str) -> None:
    """Every code the spec declares produces `ResponseFailedError` with `.code` intact."""
    response = failure(code, message=f"synthetic failure for {code}")

    with pytest.raises(ResponseFailedError) as excinfo:
        raise_for_status(response)

    exc = excinfo.value
    assert exc.code == code
    assert str(exc) == f"synthetic failure for {code}"
    assert exc.response is response


@pytest.mark.parametrize("code", ERROR_CODES)
def test_declared_error_code_retryability(code: str) -> None:
    """Retryability is exactly the documented set — transient codes only."""
    with pytest.raises(ResponseFailedError) as excinfo:
        raise_for_status(failure(code))

    assert excinfo.value.retryable is (code in RETRYABLE_CODES)


def test_retryable_codes_are_all_real_codes() -> None:
    """Guards against a typo or a removed code leaving a dead entry in the table."""
    assert RETRYABLE_CODES <= set(ERROR_CODES)


def test_unknown_future_error_code_is_not_retryable() -> None:
    """Justin's point 3: an unrecognised code must not be guessed as transient.

    A future validation, policy or quota code defaults to non-retryable rather
    than being treated as a retryable server error.
    """
    with pytest.raises(ResponseFailedError) as excinfo:
        raise_for_status(failure(UNKNOWN_ERROR_CODE, message="mystery"))

    exc = excinfo.value
    assert exc.code == UNKNOWN_ERROR_CODE
    assert exc.retryable is False
    assert str(exc) == "mystery"


def test_failed_without_error_object_still_raises() -> None:
    """The gap the original issue called out: `failed` with no `error` must not pass silently."""
    response = make_response("failed", error=None)

    with pytest.raises(ResponseFailedError) as excinfo:
        raise_for_status(response)

    exc = excinfo.value
    assert exc.code is None
    assert exc.retryable is False
    assert str(exc)  # a usable message even with nothing to describe
    assert exc.response is response


def test_failed_raises_regardless_of_raise_on_incomplete() -> None:
    """`raise_on_incomplete` gates only `incomplete`; it never suppresses a failure."""
    for opt_in in (False, True):
        with pytest.raises(ResponseFailedError):
            raise_for_status(failure("server_error"), raise_on_incomplete=opt_in)


@pytest.mark.parametrize("background", [True, False])
def test_background_and_foreground_are_classified_identically(background: bool) -> None:
    """Classification keys off `status`, not `background`.

    The earlier implementation ignored `response.background` by accident; here it
    is ignored deliberately, since a foreground failure is the same failure.
    """
    response = construct_type_unchecked(
        type_=Response,
        value=response_body("failed", error={"code": "server_error", "message": "boom"}, background=background),
    )

    with pytest.raises(ResponseFailedError) as excinfo:
        raise_for_status(response)

    assert excinfo.value.code == "server_error"


# ---------------------------------------------------------------------------
# status="incomplete"
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("reason", [*INCOMPLETE_REASONS, UNKNOWN_INCOMPLETE_REASON, None])
def test_incomplete_does_not_raise_by_default(reason: str | None) -> None:
    """Default is resource-returning: an incomplete run still has usable output."""
    raise_for_status(make_response("incomplete", incomplete_details={"reason": reason}))


def test_incomplete_without_details_does_not_raise_by_default() -> None:
    raise_for_status(make_response("incomplete", incomplete_details=None))


@pytest.mark.parametrize("reason", INCOMPLETE_REASONS)
def test_every_declared_incomplete_reason_raises_when_opted_in(reason: str) -> None:
    """Opting in raises for each reason the spec declares, `.reason` preserved."""
    response = make_response("incomplete", incomplete_details={"reason": reason})

    with pytest.raises(ResponseIncompleteError) as excinfo:
        raise_for_status(response, raise_on_incomplete=True)

    exc = excinfo.value
    assert exc.reason == reason
    assert exc.response is response
    assert reason in str(exc)


def test_unknown_future_incomplete_reason_raises_when_opted_in() -> None:
    """An unrecognised reason is surfaced verbatim, not dropped."""
    with pytest.raises(ResponseIncompleteError) as excinfo:
        raise_for_status(
            make_response("incomplete", incomplete_details={"reason": UNKNOWN_INCOMPLETE_REASON}),
            raise_on_incomplete=True,
        )

    assert excinfo.value.reason == UNKNOWN_INCOMPLETE_REASON


@pytest.mark.parametrize(
    "incomplete_details",
    [None, {"reason": None}, {}],
    ids=["no-details", "null-reason", "empty-details"],
)
def test_incomplete_without_a_reason_raises_when_opted_in(incomplete_details: dict[str, Any] | None) -> None:
    """Missing reason data still raises when opted in, with `.reason` as `None`."""
    with pytest.raises(ResponseIncompleteError) as excinfo:
        raise_for_status(
            make_response("incomplete", incomplete_details=incomplete_details),
            raise_on_incomplete=True,
        )

    exc = excinfo.value
    assert exc.reason is None
    assert str(exc)  # still a usable message


@pytest.mark.parametrize("reason", [*INCOMPLETE_REASONS, None])
def test_incomplete_is_never_retryable(reason: str | None) -> None:
    """Re-running is the caller's judgement call; the SDK does not advertise it."""
    with pytest.raises(ResponseIncompleteError) as excinfo:
        raise_for_status(make_response("incomplete", incomplete_details={"reason": reason}), raise_on_incomplete=True)

    assert excinfo.value.retryable is False


def test_incomplete_response_keeps_its_output() -> None:
    """The parsed resource stays reachable, which is the reason raising is opt-in."""
    response = make_response("incomplete", incomplete_details={"reason": "max_output_tokens"})

    with pytest.raises(ResponseIncompleteError) as excinfo:
        raise_for_status(response, raise_on_incomplete=True)

    assert excinfo.value.response.output == []
    assert excinfo.value.response.id == RESPONSE_ID


# ---------------------------------------------------------------------------
# Exception surface
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "response",
    [failure("server_error"), make_response("incomplete", incomplete_details={"reason": "content_filter"})],
    ids=["failed", "incomplete"],
)
def test_exceptions_carry_no_http_status(response: Response) -> None:
    """Justin's point 2: nothing may advertise a status the poll did not return.

    The poll itself was a `200 OK`, so these are plain `OpenAIError`s rather than
    `APIStatusError` subclasses with a fabricated 400/429/500.
    """
    with pytest.raises(ResponseNotCompletedError) as excinfo:
        raise_for_status(response, raise_on_incomplete=True)

    exc = excinfo.value
    assert isinstance(exc, OpenAIError)
    assert APIStatusError not in type(exc).__mro__
    assert not hasattr(exc, "status_code")
    # `.response` is the parsed `Response` resource, not an HTTP response object
    assert exc.response is response


def test_exception_hierarchy() -> None:
    """Both concrete types share a base callers can catch in one `except`."""
    assert issubclass(ResponseFailedError, ResponseNotCompletedError)
    assert issubclass(ResponseIncompleteError, ResponseNotCompletedError)
    assert issubclass(ResponseNotCompletedError, OpenAIError)
    assert not issubclass(ResponseFailedError, ResponseIncompleteError)
    assert not issubclass(ResponseIncompleteError, ResponseFailedError)


def test_exception_exposes_request_id() -> None:
    """The request id from the poll survives onto the exception for bug reports."""
    response = failure("server_error")
    add_request_id(response, "req_abc123")

    with pytest.raises(ResponseFailedError) as excinfo:
        raise_for_status(response)

    assert excinfo.value.request_id == "req_abc123"


def test_request_id_is_none_when_unset() -> None:
    """A hand-built response has no request id and must not raise `AttributeError`."""
    with pytest.raises(ResponseFailedError) as excinfo:
        raise_for_status(failure("server_error"))

    assert excinfo.value.request_id is None


def test_exceptions_are_exported_from_the_package_root() -> None:
    """Callers catch these by name, so they are part of the public surface."""
    import openai

    for name in ("ResponseNotCompletedError", "ResponseFailedError", "ResponseIncompleteError"):
        assert name in openai.__all__
        assert getattr(openai, name) is globals()[name]


# ---------------------------------------------------------------------------
# Public client boundary: sync and async, over every retrieval wrapper
#
# These drive the real `OpenAI` / `AsyncOpenAI` clients against a mocked
# transport. Nothing private is patched: the only seam is the HTTP layer, which
# answers `200 OK` with a terminal failure in the body — exactly the repro from
# the review.
# ---------------------------------------------------------------------------

RetrievalMode: TypeAlias = Literal["normal", "raw", "streaming"]
RETRIEVAL_MODES: tuple[RetrievalMode, ...] = ("normal", "raw", "streaming")

REQUEST_ID = "req_abc123"


def mock_retrieve(respx2_mock: MockRouter, status: str, **kwargs: Any) -> None:
    """`GET /responses/{id}` answering `200 OK` with a terminal `status` inside."""
    respx2_mock.get(RETRIEVE_PATH).mock(
        return_value=httpx2.Response(
            200,
            json=response_body(status, **kwargs),
            headers={"x-request-id": REQUEST_ID},
        )
    )


def retrieve_sync(client: OpenAI, mode: RetrievalMode) -> Response:
    """Fetch through the public sync client using one of the three wrappers."""
    if mode == "normal":
        return client.responses.retrieve(RESPONSE_ID)
    if mode == "raw":
        raw = client.responses.with_raw_response.retrieve(RESPONSE_ID)
        assert raw.http_response.status_code == 200
        return raw.parse()
    with client.responses.with_streaming_response.retrieve(RESPONSE_ID) as streamed:
        assert streamed.http_response.status_code == 200
        return streamed.parse()


async def retrieve_async(client: AsyncOpenAI, mode: RetrievalMode) -> Response:
    """Fetch through the public async client using one of the three wrappers."""
    if mode == "normal":
        return await client.responses.retrieve(RESPONSE_ID)
    if mode == "raw":
        raw = await client.responses.with_raw_response.retrieve(RESPONSE_ID)
        assert raw.http_response.status_code == 200
        return raw.parse()
    async with client.responses.with_streaming_response.retrieve(RESPONSE_ID) as streamed:
        assert streamed.http_response.status_code == 200
        return await streamed.parse()


def assert_transport_returned_200(respx2_mock: MockRouter) -> None:
    """The whole point: the poll itself succeeded, so no HTTP error was raised."""
    call = cast(Any, respx2_mock.calls).last
    assert call.response.status_code == 200
    assert call.request.method == "GET"


def assert_failed_error(exc: ResponseFailedError, *, code: str, message: str, retryable: bool) -> None:
    """Assert the full public surface of a `ResponseFailedError`."""
    assert isinstance(exc, ResponseNotCompletedError)
    assert isinstance(exc, OpenAIError)
    assert str(exc) == message
    assert exc.code == code
    assert exc.retryable is retryable
    assert exc.request_id == REQUEST_ID
    assert exc.response.status == "failed"
    assert exc.response.id == RESPONSE_ID
    assert exc.response.error is not None
    assert exc.response.error.code == code
    # never advertises an HTTP status the 200 poll did not return
    assert APIStatusError not in type(exc).__mro__
    assert not hasattr(exc, "status_code")


def assert_incomplete_error(exc: ResponseIncompleteError, *, reason: str) -> None:
    """Assert the full public surface of a `ResponseIncompleteError`."""
    assert isinstance(exc, ResponseNotCompletedError)
    assert isinstance(exc, OpenAIError)
    assert exc.reason == reason
    assert exc.retryable is False
    assert exc.request_id == REQUEST_ID
    assert exc.response.status == "incomplete"
    assert exc.response.id == RESPONSE_ID
    assert reason in str(exc)
    assert APIStatusError not in type(exc).__mro__
    assert not hasattr(exc, "status_code")


# --- retrieval stays resource-returning ------------------------------------


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("mode", RETRIEVAL_MODES)
def test_sync_retrieve_returns_failed_resource(client: OpenAI, respx2_mock: MockRouter, mode: RetrievalMode) -> None:
    """`retrieve()` and both wrappers return the resource — no compat break."""
    mock_retrieve(respx2_mock, "failed", error={"code": "server_error", "message": "boom"})

    response = retrieve_sync(client, mode)

    assert response.status == "failed"
    assert response.error is not None
    assert response.error.code == "server_error"
    assert_transport_returned_200(respx2_mock)


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("mode", RETRIEVAL_MODES)
async def test_async_retrieve_returns_failed_resource(
    async_client: AsyncOpenAI, respx2_mock: MockRouter, mode: RetrievalMode
) -> None:
    """The async client must not diverge from the sync one."""
    mock_retrieve(respx2_mock, "failed", error={"code": "server_error", "message": "boom"})

    response = await retrieve_async(async_client, mode)

    assert response.status == "failed"
    assert response.error is not None
    assert response.error.code == "server_error"
    assert_transport_returned_200(respx2_mock)


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("mode", RETRIEVAL_MODES)
def test_sync_retrieve_returns_incomplete_resource(
    client: OpenAI, respx2_mock: MockRouter, mode: RetrievalMode
) -> None:
    """An incomplete run comes back with its partial output reachable."""
    mock_retrieve(respx2_mock, "incomplete", incomplete_details={"reason": "max_output_tokens"})

    response = retrieve_sync(client, mode)

    assert response.status == "incomplete"
    assert response.incomplete_details is not None
    assert response.incomplete_details.reason == "max_output_tokens"
    assert_transport_returned_200(respx2_mock)


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("mode", RETRIEVAL_MODES)
async def test_async_retrieve_returns_incomplete_resource(
    async_client: AsyncOpenAI, respx2_mock: MockRouter, mode: RetrievalMode
) -> None:
    mock_retrieve(respx2_mock, "incomplete", incomplete_details={"reason": "max_output_tokens"})

    response = await retrieve_async(async_client, mode)

    assert response.status == "incomplete"
    assert response.incomplete_details is not None
    assert response.incomplete_details.reason == "max_output_tokens"
    assert_transport_returned_200(respx2_mock)


# --- public exception fields, end to end -----------------------------------


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("mode", RETRIEVAL_MODES)
def test_sync_retryable_failure_exception_fields(client: OpenAI, respx2_mock: MockRouter, mode: RetrievalMode) -> None:
    """Every public field of the exception, via the sync client over a real 200."""
    mock_retrieve(respx2_mock, "failed", error={"code": "server_error", "message": "boom"})

    response = retrieve_sync(client, mode)

    with pytest.raises(ResponseFailedError) as excinfo:
        raise_for_status(response)

    assert_failed_error(excinfo.value, code="server_error", message="boom", retryable=True)
    assert excinfo.value.response is response
    assert_transport_returned_200(respx2_mock)


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("mode", RETRIEVAL_MODES)
async def test_async_retryable_failure_exception_fields(
    async_client: AsyncOpenAI, respx2_mock: MockRouter, mode: RetrievalMode
) -> None:
    """The same public field assertions on the async client."""
    mock_retrieve(respx2_mock, "failed", error={"code": "server_error", "message": "boom"})

    response = await retrieve_async(async_client, mode)

    with pytest.raises(ResponseFailedError) as excinfo:
        raise_for_status(response)

    assert_failed_error(excinfo.value, code="server_error", message="boom", retryable=True)
    assert excinfo.value.response is response
    assert_transport_returned_200(respx2_mock)


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("mode", RETRIEVAL_MODES)
def test_sync_non_retryable_failure_exception_fields(
    client: OpenAI, respx2_mock: MockRouter, mode: RetrievalMode
) -> None:
    """A terminal, non-transient code reports `retryable is False` end to end."""
    mock_retrieve(respx2_mock, "failed", error={"code": "invalid_prompt", "message": "nope"})

    with pytest.raises(ResponseFailedError) as excinfo:
        raise_for_status(retrieve_sync(client, mode))

    assert_failed_error(excinfo.value, code="invalid_prompt", message="nope", retryable=False)


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("mode", RETRIEVAL_MODES)
async def test_async_non_retryable_failure_exception_fields(
    async_client: AsyncOpenAI, respx2_mock: MockRouter, mode: RetrievalMode
) -> None:
    mock_retrieve(respx2_mock, "failed", error={"code": "invalid_prompt", "message": "nope"})

    with pytest.raises(ResponseFailedError) as excinfo:
        raise_for_status(await retrieve_async(async_client, mode))

    assert_failed_error(excinfo.value, code="invalid_prompt", message="nope", retryable=False)


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("mode", RETRIEVAL_MODES)
def test_sync_failure_without_error_object_exception_fields(
    client: OpenAI, respx2_mock: MockRouter, mode: RetrievalMode
) -> None:
    """`failed` with no `error` body still raises, with `.code` as `None`."""
    mock_retrieve(respx2_mock, "failed", error=None)

    with pytest.raises(ResponseFailedError) as excinfo:
        raise_for_status(retrieve_sync(client, mode))

    exc = excinfo.value
    assert exc.code is None
    assert exc.retryable is False
    assert exc.request_id == REQUEST_ID
    assert exc.response.status == "failed"
    assert str(exc)


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("mode", RETRIEVAL_MODES)
async def test_async_failure_without_error_object_exception_fields(
    async_client: AsyncOpenAI, respx2_mock: MockRouter, mode: RetrievalMode
) -> None:
    mock_retrieve(respx2_mock, "failed", error=None)

    with pytest.raises(ResponseFailedError) as excinfo:
        raise_for_status(await retrieve_async(async_client, mode))

    exc = excinfo.value
    assert exc.code is None
    assert exc.retryable is False
    assert exc.request_id == REQUEST_ID
    assert str(exc)


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("mode", RETRIEVAL_MODES)
def test_sync_incomplete_is_opt_in(client: OpenAI, respx2_mock: MockRouter, mode: RetrievalMode) -> None:
    """Incomplete passes silently by default and raises only when opted in."""
    mock_retrieve(respx2_mock, "incomplete", incomplete_details={"reason": "content_filter"})

    response = retrieve_sync(client, mode)
    raise_for_status(response)  # default: no raise

    with pytest.raises(ResponseIncompleteError) as excinfo:
        raise_for_status(response, raise_on_incomplete=True)

    assert_incomplete_error(excinfo.value, reason="content_filter")
    assert excinfo.value.response is response


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("mode", RETRIEVAL_MODES)
async def test_async_incomplete_is_opt_in(
    async_client: AsyncOpenAI, respx2_mock: MockRouter, mode: RetrievalMode
) -> None:
    mock_retrieve(respx2_mock, "incomplete", incomplete_details={"reason": "content_filter"})

    response = await retrieve_async(async_client, mode)
    raise_for_status(response)  # default: no raise

    with pytest.raises(ResponseIncompleteError) as excinfo:
        raise_for_status(response, raise_on_incomplete=True)

    assert_incomplete_error(excinfo.value, reason="content_filter")
    assert excinfo.value.response is response


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("status", ["completed", "cancelled"])
def test_sync_successful_statuses_never_raise_over_the_wire(
    client: OpenAI, respx2_mock: MockRouter, status: str
) -> None:
    """No false positives: a healthy poll stays quiet through the public client."""
    mock_retrieve(respx2_mock, status)

    response = client.responses.retrieve(RESPONSE_ID)
    raise_for_status(response, raise_on_incomplete=True)

    assert response.status == status


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("status", ["completed", "cancelled"])
async def test_async_successful_statuses_never_raise_over_the_wire(
    async_client: AsyncOpenAI, respx2_mock: MockRouter, status: str
) -> None:
    mock_retrieve(respx2_mock, status)

    response = await async_client.responses.retrieve(RESPONSE_ID)
    raise_for_status(response, raise_on_incomplete=True)

    assert response.status == status


@pytest.mark.respx2(base_url=base_url)
def test_every_wrapper_produces_an_identical_exception(client: OpenAI, respx2_mock: MockRouter) -> None:
    """The three wrappers are interchangeable, asserted side by side in one test."""
    mock_retrieve(respx2_mock, "failed", error={"code": "server_error", "message": "boom"})

    results = [retrieve_sync(client, mode) for mode in RETRIEVAL_MODES]

    for response in results:
        with pytest.raises(ResponseFailedError) as excinfo:
            raise_for_status(response)

        assert_failed_error(excinfo.value, code="server_error", message="boom", retryable=True)


@pytest.mark.respx2(base_url=base_url)
def test_stream_true_yields_events_without_raising(client: OpenAI, respx2_mock: MockRouter) -> None:
    """`stream=True` returns a `Stream` of events and never classifies for you.

    The failure arrives as a `response.failed` event; the caller opts in by
    passing `event.response` to the helper.
    """
    event = {
        "type": "response.failed",
        "sequence_number": 1,
        "response": response_body("failed", error={"code": "server_error", "message": "boom"}),
    }
    respx2_mock.get(RETRIEVE_PATH).mock(
        return_value=httpx2.Response(
            200,
            headers={"content-type": "text/event-stream"},
            content=f"event: response.failed\ndata: {json.dumps(event)}\n\n".encode(),
        )
    )

    events = list(client.responses.retrieve(RESPONSE_ID, stream=True))

    assert len(events) == 1
    failed = cast(Any, events[0])
    assert failed.type == "response.failed"
    assert failed.response.status == "failed"

    with pytest.raises(ResponseFailedError):
        raise_for_status(failed.response)
