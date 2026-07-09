"""Tests for the opt-in httpx2 backend (`openai._httpx2_compat`).

These exercise the real `httpx2` library end-to-end, via `httpx2.MockTransport`,
against the openai client's request/response pipeline:

  * the isinstance gate that accepts/rejects httpx2 clients on `OpenAI`/`AsyncOpenAI`
  * the 600s timeout footgun fix (httpx2's own bare-client default is 5s)
  * the classic-httpx `URL` -> `str` coercion needed at request-build time
  * the widened exception tuples that map httpx2's *independent* exception
    hierarchy onto the SDK's error classes (status errors, timeouts, connect errors)
  * retries (and the `x-stainless-retry-count` header) over an httpx2 transport
  * the Bedrock SigV4 body-signing seam, where httpx2's `RequestNotRead` must map
    onto the SDK's friendly `OpenAIError`
  * provider-managed auth over an httpx2 backend: the no-op `Auth` handed to `send()`
    must come from the client's own backend (httpx2 rejects a classic `httpx.Auth`)

httpx2 is an opt-in extra that isn't installable on Python 3.9, so the whole module
is skipped cleanly when it isn't present.
"""

from __future__ import annotations

from typing import Any, Callable
from unittest import mock

import httpx
import pytest

httpx2 = pytest.importorskip("httpx2")

from openai import (
    OpenAI,
    AsyncOpenAI,
    OpenAIError,
    NotFoundError,
    APIStatusError,
    RateLimitError,
    APITimeoutError,
    BadRequestError,
    APIConnectionError,
    DefaultHttpx2Client,
    InternalServerError,
    DefaultAsyncHttpx2Client,
)

api_key = "sk-test"

MODEL_JSON = {"id": "gpt-4", "object": "model", "created": 0, "owned_by": "openai"}

Handler = Callable[[Any], Any]


def _error_body(message: str = "boom") -> dict[str, Any]:
    return {"error": {"message": message, "type": "invalid_request_error", "code": None, "param": None}}


def _low_retry_timeout(*_args: Any, **_kwargs: Any) -> float:
    return 0.01


def _assert_sdk_default_timeout(timeout: Any) -> None:
    # The timeout is duck-typed: an httpx2.Timeout when the SDK adopts the httpx2
    # client's own value, or a classic httpx.Timeout when it substitutes DEFAULT_TIMEOUT
    # (the bare-client path). Both expose .read/.connect; typing the param as Any
    # sidesteps the `float | Timeout | None` union member access under pyright-strict.
    assert timeout.read == 600
    assert timeout.connect == 5


def _model_handler(request: Any) -> Any:
    """Handler shared by sync + async tests: httpx2.MockTransport allows a plain
    (non-async) handler for both `httpx2.Client` and `httpx2.AsyncClient`."""
    if "missing" in request.url.path:
        return httpx2.Response(404, json=_error_body("no such model"))
    return httpx2.Response(200, json=MODEL_JSON)


def _status_handler(status_code: int) -> Handler:
    def handler(_request: Any) -> Any:
        return httpx2.Response(status_code, json=_error_body())

    return handler


def _sync_client(handler: Handler, **kwargs: Any) -> OpenAI:
    return OpenAI(
        api_key=api_key,
        http_client=DefaultHttpx2Client(transport=httpx2.MockTransport(handler)),
        **kwargs,
    )


def _async_client(handler: Handler, **kwargs: Any) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=api_key,
        http_client=DefaultAsyncHttpx2Client(transport=httpx2.MockTransport(handler)),
        **kwargs,
    )


class TestConstructionAndGate:
    def test_default_httpx2_client_constructs(self) -> None:
        with DefaultHttpx2Client(transport=httpx2.MockTransport(_model_handler)) as client:
            assert isinstance(client, httpx2.Client)

    async def test_default_async_httpx2_client_constructs(self) -> None:
        async with DefaultAsyncHttpx2Client(transport=httpx2.MockTransport(_model_handler)) as client:
            assert isinstance(client, httpx2.AsyncClient)

    def test_openai_accepts_default_httpx2_client(self) -> None:
        with _sync_client(_model_handler) as client:
            assert isinstance(client._client, httpx2.Client)

    async def test_async_openai_accepts_default_async_httpx2_client(self) -> None:
        async with _async_client(_model_handler) as client:
            assert isinstance(client._client, httpx2.AsyncClient)

    def test_sync_openai_rejects_async_httpx2_client(self) -> None:
        # the message should name both accepted types now that the extra is installed
        with pytest.raises(TypeError, match=r"`httpx\.Client` or `httpx2\.Client`"):
            OpenAI(api_key=api_key, http_client=httpx2.AsyncClient())

    async def test_async_openai_rejects_sync_httpx2_client(self) -> None:
        with pytest.raises(TypeError, match=r"`httpx\.AsyncClient` or `httpx2\.AsyncClient`"):
            AsyncOpenAI(api_key=api_key, http_client=httpx2.Client())

    def test_default_httpx2_client_uses_sdk_timeout_not_httpx2_default(self) -> None:
        # httpx2's own default is `Timeout(5.0)`; DefaultHttpx2Client explicitly sets
        # the SDK's default (read=600, connect=5) instead.
        with DefaultHttpx2Client(transport=httpx2.MockTransport(_model_handler)) as client:
            _assert_sdk_default_timeout(client.timeout)

    def test_openai_with_default_httpx2_client_reports_sdk_timeout(self) -> None:
        with _sync_client(_model_handler) as client:
            _assert_sdk_default_timeout(client.timeout)

    async def test_async_openai_with_default_httpx2_client_reports_sdk_timeout(self) -> None:
        async with _async_client(_model_handler) as client:
            _assert_sdk_default_timeout(client.timeout)

    def test_bare_httpx2_client_gets_sdk_default_timeout(self) -> None:
        # The footgun: a *bare* `httpx2.Client()` structurally reports httpx2's own
        # 5s default, which is `!=` classic httpx's default across the class
        # boundary. Without the fix in `_base_client.py`, `OpenAI` would mistake
        # that for a user-supplied timeout and silently adopt the 5s value.
        bare = httpx2.Client(transport=httpx2.MockTransport(_model_handler))
        with OpenAI(api_key=api_key, http_client=bare) as client:
            _assert_sdk_default_timeout(client.timeout)

    async def test_bare_async_httpx2_client_gets_sdk_default_timeout(self) -> None:
        bare = httpx2.AsyncClient(transport=httpx2.MockTransport(_model_handler))
        async with AsyncOpenAI(api_key=api_key, http_client=bare) as client:
            _assert_sdk_default_timeout(client.timeout)

    def test_explicit_library_default_timeout_is_treated_as_uncustomised(self) -> None:
        # Documented parity with classic httpx: the SDK's structural check treats a
        # client whose timeout equals the *library's own default* (httpx2's 5s) as
        # "not customised" and substitutes DEFAULT_TIMEOUT (600s) -- exactly as it
        # already does for a classic `httpx.Client(timeout=5.0)`. Callers who truly
        # want 5s must pass `timeout=` to `OpenAI(...)` directly. This asserts the
        # behaviour is intentional, not an accident of the footgun fix.
        explicit = httpx2.Client(timeout=httpx2.Timeout(5.0), transport=httpx2.MockTransport(_model_handler))
        with OpenAI(api_key=api_key, http_client=explicit) as client:
            _assert_sdk_default_timeout(client.timeout)

    def test_non_default_httpx2_timeout_is_respected(self) -> None:
        # Conversely, a genuinely non-default httpx2 timeout IS honoured (it differs
        # from both the classic and httpx2 library defaults).
        explicit = httpx2.Client(timeout=httpx2.Timeout(30.0), transport=httpx2.MockTransport(_model_handler))
        with OpenAI(api_key=api_key, http_client=explicit) as client:
            timeout: Any = client.timeout
            assert timeout.read == 30


class TestUrlCoercion:
    """A successful request implicitly proves the classic-httpx `URL` -> `str`
    coercion at the one `build_request` call site: without it every request would
    raise `TypeError: Expected str or httpx2.URL, got httpx.URL` before it ever
    reaches the mock transport."""

    def test_sync_get_returns_parsed_model(self) -> None:
        with _sync_client(_model_handler) as client:
            model = client.models.retrieve("gpt-4")
            assert model.id == "gpt-4"

    async def test_async_get_returns_parsed_model(self) -> None:
        async with _async_client(_model_handler) as client:
            model = await client.models.retrieve("gpt-4")
            assert model.id == "gpt-4"


class TestStatusMapping:
    """Load-bearing: proves httpx2's *independent* `HTTPStatusError` is caught by
    the widened `HTTP_STATUS_ERRORS` tuple. Without that widening, `raise_for_status()`
    would raise an exception the `except HTTP_STATUS_ERRORS` clause doesn't see, and
    it would fall through to the generic `except Exception` branch, surfacing as
    `APIConnectionError` instead of the correct status-specific error."""

    @pytest.mark.parametrize(
        "status_code,expected_error",
        [
            (400, BadRequestError),
            (404, NotFoundError),
            (429, RateLimitError),
            (500, InternalServerError),
            (402, APIStatusError),  # generic 4xx with no dedicated subclass
        ],
    )
    def test_sync_status_mapping(self, status_code: int, expected_error: type[APIStatusError]) -> None:
        with _sync_client(_status_handler(status_code), max_retries=0) as client:
            with pytest.raises(expected_error) as excinfo:
                client.models.retrieve("gpt-4")
            assert type(excinfo.value) is expected_error
            assert excinfo.value.status_code == status_code

    @pytest.mark.parametrize(
        "status_code,expected_error",
        [
            (400, BadRequestError),
            (404, NotFoundError),
            (429, RateLimitError),
            (500, InternalServerError),
            (402, APIStatusError),
        ],
    )
    async def test_async_status_mapping(self, status_code: int, expected_error: type[APIStatusError]) -> None:
        async with _async_client(_status_handler(status_code), max_retries=0) as client:
            with pytest.raises(expected_error) as excinfo:
                await client.models.retrieve("gpt-4")
            assert type(excinfo.value) is expected_error
            assert excinfo.value.status_code == status_code


class TestTransportErrors:
    """Proves the widened `TIMEOUT_EXCEPTIONS` tuple catches httpx2's own
    `ReadTimeout`/`TimeoutException`, and that other httpx2 transport errors
    (e.g. `ConnectError`) still fall through to `APIConnectionError` as expected."""

    def test_sync_read_timeout_raises_api_timeout_error(self) -> None:
        def handler(request: Any) -> Any:
            raise httpx2.ReadTimeout("simulated read timeout", request=request)

        with _sync_client(handler, max_retries=0) as client:
            with pytest.raises(APITimeoutError):
                client.models.retrieve("gpt-4")

    async def test_async_read_timeout_raises_api_timeout_error(self) -> None:
        def handler(request: Any) -> Any:
            raise httpx2.ReadTimeout("simulated read timeout", request=request)

        async with _async_client(handler, max_retries=0) as client:
            with pytest.raises(APITimeoutError):
                await client.models.retrieve("gpt-4")

    def test_sync_connect_error_raises_api_connection_error(self) -> None:
        def handler(request: Any) -> Any:
            raise httpx2.ConnectError("simulated connect error", request=request)

        with _sync_client(handler, max_retries=0) as client:
            with pytest.raises(APIConnectionError):
                client.models.retrieve("gpt-4")

    async def test_async_connect_error_raises_api_connection_error(self) -> None:
        def handler(request: Any) -> Any:
            raise httpx2.ConnectError("simulated connect error", request=request)

        async with _async_client(handler, max_retries=0) as client:
            with pytest.raises(APIConnectionError):
                await client.models.retrieve("gpt-4")


class TestRetries:
    """A 500 followed by a 200 should be retried transparently over the httpx2
    transport, and the retry count should be reflected in the
    `x-stainless-retry-count` header -- proving retries work end-to-end on this
    backend, not just the status-error mapping in isolation."""

    @mock.patch("openai._base_client.BaseClient._calculate_retry_timeout", _low_retry_timeout)
    def test_sync_retries_after_500_then_succeeds(self) -> None:
        nb_calls = 0

        def handler(_request: Any) -> Any:
            nonlocal nb_calls
            nb_calls += 1
            if nb_calls == 1:
                return httpx2.Response(500, json=_error_body())
            return httpx2.Response(200, json=MODEL_JSON)

        with _sync_client(handler, max_retries=1) as client:
            response = client.models.with_raw_response.retrieve("gpt-4")

        assert nb_calls == 2
        assert response.http_request.headers.get("x-stainless-retry-count") == "1"
        assert response.parse().id == "gpt-4"

    @mock.patch("openai._base_client.BaseClient._calculate_retry_timeout", _low_retry_timeout)
    async def test_async_retries_after_500_then_succeeds(self) -> None:
        nb_calls = 0

        def handler(_request: Any) -> Any:
            nonlocal nb_calls
            nb_calls += 1
            if nb_calls == 1:
                return httpx2.Response(500, json=_error_body())
            return httpx2.Response(200, json=MODEL_JSON)

        async with _async_client(handler, max_retries=1) as client:
            response = await client.models.with_raw_response.retrieve("gpt-4")

        assert nb_calls == 2
        assert response.http_request.headers.get("x-stainless-retry-count") == "1"
        assert response.parse().id == "gpt-4"


class TestBedrockBodySigning:
    """Bedrock SigV4 signing reads `request.content` to build the signature. With an
    httpx2 backend the request is an `httpx2.Request`, and an unbuffered (streaming)
    body raises httpx2's own `RequestNotRead` -- a distinct class from httpx's that
    the widened `REQUEST_NOT_READ_ERRORS` tuple must catch so the caller sees the
    actionable `OpenAIError` instead of a raw httpx2 exception."""

    def test_httpx2_request_not_read_maps_to_openai_error(self) -> None:
        from openai.providers.bedrock import _body_for_signing

        # an iterator body is a one-shot stream: `.content` raises RequestNotRead
        # until the request is explicitly buffered with `.read()`
        request: Any = httpx2.Request("POST", "http://localhost/test", content=iter([b"chunk"]))
        with pytest.raises(OpenAIError, match="replayable request body"):
            _body_for_signing(request)

    def test_buffered_httpx2_request_body_is_returned(self) -> None:
        from openai.providers.bedrock import _body_for_signing

        request: Any = httpx2.Request("POST", "http://localhost/test", content=b"chunk")
        assert _body_for_signing(request) == b"chunk"


class TestProviderAuth:
    """Provider-managed clients (e.g. Bedrock) pass a no-op `Auth` to `send()` so the
    provider's request hooks own authentication. httpx2's `send` rejects a classic
    `httpx.Auth` instance (`TypeError: Invalid "auth" argument`) -- which the SDK's
    generic exception handling would then surface as a misleading `APIConnectionError`
    -- so the no-op auth must come from the client's own backend (`noop_auth_for`)."""

    def test_sync_bedrock_provider_over_httpx2(self) -> None:
        from openai.providers import bedrock

        requests: list[Any] = []

        def handler(request: Any) -> Any:
            requests.append(request)
            return httpx2.Response(200, json={})

        client = OpenAI(
            provider=bedrock(region="us-east-1", api_key="bedrock token"),
            http_client=DefaultHttpx2Client(transport=httpx2.MockTransport(handler), trust_env=False),
        )
        client.get("/models", cast_to=httpx.Response)

        assert requests[0].headers["Authorization"] == "Bearer bedrock token"

    async def test_async_bedrock_provider_over_httpx2(self) -> None:
        from openai.providers import bedrock

        requests: list[Any] = []

        def handler(request: Any) -> Any:
            requests.append(request)
            return httpx2.Response(200, json={})

        client = AsyncOpenAI(
            provider=bedrock(region="us-east-1", token_provider=lambda: "bedrock token"),
            http_client=DefaultAsyncHttpx2Client(transport=httpx2.MockTransport(handler), trust_env=False),
        )
        await client.get("/models", cast_to=httpx.Response)
        await client.close()

        assert requests[0].headers["Authorization"] == "Bearer bedrock token"


class TestStreamConsumed:
    @pytest.mark.skip(
        reason=(
            "Not reproducible against httpx2.MockTransport: `httpx2.Response(status_code, "
            "json=...)` eagerly reads its body into `self._content` at construction time "
            "whenever it is built with `content=`/`json=`/`text=` (see `Response.__init__` "
            "in httpx2/_models.py, which calls `self.read()` immediately for any "
            "`ByteStream` body). Every subsequent `.read()`/`.iter_bytes()` call then hits "
            "the cached-content fast path and never reaches the raw-stream branch that "
            "raises `StreamConsumed`. Reproducing genuine double-consumption would require "
            "a response built with a real `stream=`/`SyncByteStream` object standing in for "
            "the transport's raw byte stream, which MockTransport's handler-based API does "
            "not expose."
        )
    )
    def test_double_read_raises_stream_already_consumed(self) -> None: ...
