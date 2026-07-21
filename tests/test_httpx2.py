from __future__ import annotations

from typing import Any
from typing_extensions import override

import httpx
import pytest

import openai
from openai import OpenAI, AsyncOpenAI, OpenAIError, APIStatusError, APITimeoutError, APIConnectionError
from openai._response import StreamAlreadyConsumed
from openai.providers import bedrock

httpx2 = pytest.importorskip("httpx2")


@pytest.fixture(autouse=True)
def forbid_httpx_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("the experimental path unexpectedly executed an HTTPX client")

    monkeypatch.setattr(httpx.Client, "build_request", forbidden)
    monkeypatch.setattr(httpx.Client, "send", forbidden)
    monkeypatch.setattr(httpx.AsyncClient, "build_request", forbidden)
    monkeypatch.setattr(httpx.AsyncClient, "send", forbidden)


def model_list(request: httpx.Request) -> httpx.Response:
    return httpx2.Response(200, json={"object": "list", "data": []}, request=request)


def sse_response(request: httpx.Request) -> httpx.Response:
    return httpx2.Response(
        200,
        headers={"content-type": "text/event-stream"},
        content=(
            b'data: {"type":"response.completed","response":{"id":"resp_test","object":"response",'
            b'"created_at":0,"model":"gpt-4o","output":[],"parallel_tool_calls":false,'
            b'"tool_choice":"auto","tools":[]}}\n\ndata: [DONE]\n\n'
        ),
        request=request,
    )


async def test_httpx2_helpers_supply_sdk_defaults_and_accept_native_proxy() -> None:
    sync_client = openai.DefaultHttpx2Client(proxy="http://127.0.0.1:8080", trust_env=False)
    async_client = openai.DefaultAsyncHttpx2Client(proxy="http://127.0.0.1:8080", trust_env=False)
    try:
        assert type(sync_client).__module__ == "httpx2"
        assert type(async_client).__module__ == "httpx2"
        assert sync_client.timeout.as_dict() == {"connect": 5.0, "read": 600, "write": 600, "pool": 600}
        assert async_client.timeout.as_dict() == {"connect": 5.0, "read": 600, "write": 600, "pool": 600}
        assert sync_client.follow_redirects
        assert async_client.follow_redirects
    finally:
        sync_client.close()
        await async_client.aclose()


def test_sync_helper_preserves_httpx2_family_for_parsed_raw_and_sse() -> None:
    requests: list[httpx.Request] = []
    hooks: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return sse_response(request) if request.url.path.endswith("/responses") else model_list(request)

    def on_request(request: httpx.Request) -> None:
        hooks.append(type(request).__module__)

    with OpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=openai.DefaultHttpx2Client(
            timeout=httpx.Timeout(30.0, read=10.0),
            auth=httpx2.BasicAuth("user", "pass"),
            headers=[("x-repeated", "one"), ("x-repeated", "two")],
            mounts={"https://example.test": httpx2.MockTransport(handler)},
            event_hooks={"request": [on_request]},
            trust_env=False,
        ),
        max_retries=0,
    ) as client:
        parsed = client.models.list(extra_query={"tag": ["one", "two"]})
        raw = client.models.with_raw_response.list()
        stream = client.responses.create(model="gpt-4o", input="hello", stream=True)
        events = list(stream)
        multipart = client.post(
            "/multipart",
            files={"file": ("example.txt", b"body", "text/plain")},
            options={"headers": {"Content-Type": "multipart/form-data"}},
            cast_to=httpx.Response,
        )

    assert parsed.object == "list"
    assert type(raw.http_response).__module__ == "httpx2"
    assert type(raw.http_request).__module__ == "httpx2"
    assert type(stream.response).__module__ == "httpx2"
    assert [event.type for event in events] == ["response.completed"]
    assert type(multipart).__module__ == "httpx2"
    assert hooks == ["httpx2", "httpx2", "httpx2", "httpx2"]
    assert all(type(request).__module__ == "httpx2" for request in requests)
    assert requests[0].headers["authorization"] == "Basic dXNlcjpwYXNz"
    assert requests[0].headers.get_list("x-repeated") == ["one", "two"]
    assert requests[0].url.params.get_list("tag[]") == ["one", "two"]
    assert requests[0].extensions["timeout"] == {"connect": 30.0, "read": 10.0, "write": 30.0, "pool": 30.0}
    assert requests[-1].headers["content-type"].startswith("multipart/form-data; boundary=")


async def test_async_helper_preserves_httpx2_family_for_parsed_raw_and_sse() -> None:
    requests: list[httpx.Request] = []
    hooks: list[str] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return sse_response(request) if request.url.path.endswith("/responses") else model_list(request)

    async def on_request(request: httpx.Request) -> None:
        hooks.append(type(request).__module__)

    async with AsyncOpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=openai.DefaultAsyncHttpx2Client(
            timeout=httpx.Timeout(30.0, read=10.0),
            auth=httpx2.BasicAuth("user", "pass"),
            headers=[("x-repeated", "one"), ("x-repeated", "two")],
            transport=httpx2.MockTransport(handler),
            event_hooks={"request": [on_request]},
            trust_env=False,
        ),
        max_retries=0,
    ) as client:
        parsed = await client.models.list(extra_query={"tag": ["one", "two"]})
        raw = await client.models.with_raw_response.list()
        stream = await client.responses.create(model="gpt-4o", input="hello", stream=True)
        events = [event async for event in stream]
        multipart = await client.post(
            "/multipart",
            files={"file": ("example.txt", b"body", "text/plain")},
            options={"headers": {"Content-Type": "multipart/form-data"}},
            cast_to=httpx.Response,
        )

    assert parsed.object == "list"
    assert type(raw.http_response).__module__ == "httpx2"
    assert type(raw.http_request).__module__ == "httpx2"
    assert type(stream.response).__module__ == "httpx2"
    assert [event.type for event in events] == ["response.completed"]
    assert type(multipart).__module__ == "httpx2"
    assert hooks == ["httpx2", "httpx2", "httpx2", "httpx2"]
    assert all(type(request).__module__ == "httpx2" for request in requests)
    assert requests[0].headers["authorization"] == "Basic dXNlcjpwYXNz"
    assert requests[0].headers.get_list("x-repeated") == ["one", "two"]
    assert requests[0].url.params.get_list("tag[]") == ["one", "two"]
    assert requests[0].extensions["timeout"] == {"connect": 30.0, "read": 10.0, "write": 30.0, "pool": 30.0}
    assert requests[-1].headers["content-type"].startswith("multipart/form-data; boundary=")


def test_direct_sync_injection_and_module_configuration() -> None:
    direct = httpx2.Client(transport=httpx2.MockTransport(model_list), trust_env=False)
    with OpenAI(api_key="test", base_url="https://example.test/v1", http_client=direct, max_retries=0) as client:
        assert client.models.list().object == "list"

    openai.api_key = "test"
    openai.base_url = "https://example.test/v1"
    openai.http_client = openai.DefaultHttpx2Client(transport=httpx2.MockTransport(model_list), trust_env=False)
    try:
        response = openai.models.with_raw_response.list()
    finally:
        openai._reset_client()
        openai.http_client = None

    assert type(response.http_response).__module__ == "httpx2"


async def test_direct_async_injection() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return model_list(request)

    direct = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
    async with AsyncOpenAI(
        api_key="test", base_url="https://example.test/v1", http_client=direct, max_retries=0
    ) as client:
        assert (await client.models.list()).object == "list"


@pytest.mark.parametrize("failure", ["timeout", "connection", "status"])
def test_sync_retries_and_failure_families(failure: str, monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) > 1:
            return model_list(request)
        if failure == "timeout":
            raise httpx2.ReadTimeout("timeout", request=request)
        if failure == "connection":
            raise httpx2.ConnectError("connection", request=request)
        return httpx2.Response(500, json={"error": {"message": "bad", "type": "test"}}, request=request)

    client = OpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
        max_retries=1,
    )

    def no_sleep(**_kwargs: Any) -> None:
        return None

    monkeypatch.setattr(client, "_sleep_for_retry", no_sleep)
    try:
        assert client.models.list().object == "list"
    finally:
        client.close()

    assert len(requests) == 2
    assert all(type(request).__module__ == "httpx2" for request in requests)

    def always_fail(request: httpx.Request) -> httpx.Response:
        if failure == "timeout":
            raise httpx2.ReadTimeout("timeout", request=request)
        if failure == "connection":
            raise httpx2.ConnectError("connection", request=request)
        return httpx2.Response(500, json={"error": {"message": "bad", "type": "test"}}, request=request)

    expected: type[Exception]
    if failure == "timeout":
        expected = APITimeoutError
    elif failure == "connection":
        expected = APIConnectionError
    else:
        expected = APIStatusError

    with OpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=httpx2.Client(transport=httpx2.MockTransport(always_fail), trust_env=False),
        max_retries=0,
    ) as failing_client:
        with pytest.raises(expected) as exc_info:
            failing_client.models.list()

    error = exc_info.value
    transport_value = getattr(error, "response", None) or getattr(error, "request", None)
    assert type(transport_value).__module__ == "httpx2"


@pytest.mark.parametrize("failure", ["timeout", "connection", "status"])
async def test_async_retries_and_failure_families(failure: str, monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) > 1:
            return model_list(request)
        if failure == "timeout":
            raise httpx2.ReadTimeout("timeout", request=request)
        if failure == "connection":
            raise httpx2.ConnectError("connection", request=request)
        return httpx2.Response(500, json={"error": {"message": "bad", "type": "test"}}, request=request)

    client = AsyncOpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False),
        max_retries=1,
    )

    async def no_sleep(**_kwargs: Any) -> None:
        return None

    monkeypatch.setattr(client, "_sleep_for_retry", no_sleep)
    try:
        assert (await client.models.list()).object == "list"
    finally:
        await client.close()

    assert len(requests) == 2
    assert all(type(request).__module__ == "httpx2" for request in requests)

    async def always_fail(request: httpx.Request) -> httpx.Response:
        if failure == "timeout":
            raise httpx2.ReadTimeout("timeout", request=request)
        if failure == "connection":
            raise httpx2.ConnectError("connection", request=request)
        return httpx2.Response(500, json={"error": {"message": "bad", "type": "test"}}, request=request)

    expected: type[Exception]
    if failure == "timeout":
        expected = APITimeoutError
    elif failure == "connection":
        expected = APIConnectionError
    else:
        expected = APIStatusError

    async with AsyncOpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(always_fail), trust_env=False),
        max_retries=0,
    ) as failing_client:
        with pytest.raises(expected) as exc_info:
            await failing_client.models.list()

    error = exc_info.value
    transport_value = getattr(error, "response", None) or getattr(error, "request", None)
    assert type(transport_value).__module__ == "httpx2"


async def test_provider_auth_and_stream_consumed_families() -> None:
    sync_requests: list[httpx.Request] = []
    async_requests: list[httpx.Request] = []

    def sync_handler(request: httpx.Request) -> httpx.Response:
        sync_requests.append(request)
        return model_list(request)

    async def async_handler(request: httpx.Request) -> httpx.Response:
        async_requests.append(request)
        return model_list(request)

    with OpenAI(
        provider=bedrock(region="us-east-1", api_key="bedrock-token", base_url="https://bedrock.test/openai/v1"),
        http_client=openai.DefaultHttpx2Client(transport=httpx2.MockTransport(sync_handler), trust_env=False),
        max_retries=0,
    ) as sync_client:
        assert sync_client.models.list().object == "list"

    async with AsyncOpenAI(
        provider=bedrock(region="us-east-1", api_key="bedrock-token", base_url="https://bedrock.test/openai/v1"),
        http_client=openai.DefaultAsyncHttpx2Client(transport=httpx2.MockTransport(async_handler), trust_env=False),
        max_retries=0,
    ) as async_client:
        assert (await async_client.models.list()).object == "list"

    assert sync_requests[0].headers["authorization"] == "Bearer bedrock-token"
    assert async_requests[0].headers["authorization"] == "Bearer bedrock-token"

    class SyncStream(httpx2.SyncByteStream):
        def __iter__(self):
            yield b'{"object":"list","data":[]}'

    class AsyncStream(httpx2.AsyncByteStream):
        async def __aiter__(self):
            yield b'{"object":"list","data":[]}'

    class FailingSyncStream(httpx2.SyncByteStream):
        def __iter__(self):
            yield b"partial"
            raise httpx2.ReadTimeout("stream timeout")

    class FailingAsyncStream(httpx2.AsyncByteStream):
        async def __aiter__(self):
            yield b"partial"
            raise httpx2.ReadTimeout("stream timeout")

    def sync_stream_handler(request: httpx.Request) -> httpx.Response:
        return httpx2.Response(200, headers={"content-type": "application/json"}, stream=SyncStream(), request=request)

    async def async_stream_handler(request: httpx.Request) -> httpx.Response:
        return httpx2.Response(200, headers={"content-type": "application/json"}, stream=AsyncStream(), request=request)

    def sync_failing_stream_handler(request: httpx.Request) -> httpx.Response:
        return httpx2.Response(
            200, headers={"content-type": "application/json"}, stream=FailingSyncStream(), request=request
        )

    async def async_failing_stream_handler(request: httpx.Request) -> httpx.Response:
        return httpx2.Response(
            200, headers={"content-type": "application/json"}, stream=FailingAsyncStream(), request=request
        )

    with OpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=httpx2.Client(transport=httpx2.MockTransport(sync_stream_handler), trust_env=False),
        max_retries=0,
    ) as sync_client:
        with sync_client.models.with_streaming_response.list() as response:
            assert b"".join(response.iter_bytes()) == b'{"object":"list","data":[]}'
            with pytest.raises(StreamAlreadyConsumed):
                response.read()

    with OpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=httpx2.Client(transport=httpx2.MockTransport(sync_failing_stream_handler), trust_env=False),
        max_retries=0,
    ) as sync_client:
        with sync_client.models.with_streaming_response.list() as response:
            with pytest.raises(httpx2.ReadTimeout, match="stream timeout"):
                list(response.iter_bytes())

    async with AsyncOpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(async_stream_handler), trust_env=False),
        max_retries=0,
    ) as async_client:
        async with async_client.models.with_streaming_response.list() as response:
            assert b"".join([chunk async for chunk in response.iter_bytes()]) == b'{"object":"list","data":[]}'
            with pytest.raises(StreamAlreadyConsumed):
                await response.read()

    async with AsyncOpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(async_failing_stream_handler), trust_env=False),
        max_retries=0,
    ) as async_client:
        async with async_client.models.with_streaming_response.list() as response:
            with pytest.raises(httpx2.ReadTimeout, match="stream timeout"):
                [chunk async for chunk in response.iter_bytes()]


@pytest.mark.filterwarnings("ignore:The Assistants API is deprecated in favor of the Responses API:DeprecationWarning")
async def test_assistant_stream_timeout_callbacks_preserve_httpx2_family() -> None:
    class SyncHandler(openai.AssistantEventHandler):
        def __init__(self) -> None:
            super().__init__()
            self.timed_out = False
            self.exception: Exception | None = None

        @override
        def on_timeout(self) -> None:
            self.timed_out = True

        @override
        def on_exception(self, exception: Exception) -> None:
            self.exception = exception

    class AsyncHandler(openai.AsyncAssistantEventHandler):
        def __init__(self) -> None:
            super().__init__()
            self.timed_out = False
            self.exception: Exception | None = None

        @override
        async def on_timeout(self) -> None:
            self.timed_out = True

        @override
        async def on_exception(self, exception: Exception) -> None:
            self.exception = exception

    class FailingSyncStream(httpx2.SyncByteStream):
        def __iter__(self):
            yield b"partial"
            raise httpx2.ReadTimeout("assistant stream timeout")

    class FailingAsyncStream(httpx2.AsyncByteStream):
        async def __aiter__(self):
            yield b"partial"
            raise httpx2.ReadTimeout("assistant stream timeout")

    def sync_response(request: httpx.Request) -> httpx.Response:
        return httpx2.Response(
            200, headers={"content-type": "text/event-stream"}, stream=FailingSyncStream(), request=request
        )

    async def async_response(request: httpx.Request) -> httpx.Response:
        return httpx2.Response(
            200, headers={"content-type": "text/event-stream"}, stream=FailingAsyncStream(), request=request
        )

    sync_handler = SyncHandler()
    with OpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=openai.DefaultHttpx2Client(transport=httpx2.MockTransport(sync_response), trust_env=False),
        max_retries=0,
    ) as sync_client:
        with sync_client.beta.threads.runs.stream(  # pyright: ignore[reportDeprecated]
            assistant_id="asst_test", thread_id="thread_test", event_handler=sync_handler
        ) as stream:
            with pytest.raises(httpx2.ReadTimeout, match="assistant stream timeout"):
                stream.until_done()

    assert sync_handler.timed_out
    assert isinstance(sync_handler.exception, httpx2.ReadTimeout)

    async_handler = AsyncHandler()
    async with AsyncOpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=openai.DefaultAsyncHttpx2Client(transport=httpx2.MockTransport(async_response), trust_env=False),
        max_retries=0,
    ) as async_client:
        async with async_client.beta.threads.runs.stream(  # pyright: ignore[reportDeprecated]
            assistant_id="asst_test", thread_id="thread_test", event_handler=async_handler
        ) as async_stream:
            with pytest.raises(httpx2.ReadTimeout, match="assistant stream timeout"):
                await async_stream.until_done()

    assert async_handler.timed_out
    assert isinstance(async_handler.exception, httpx2.ReadTimeout)


async def test_sigv4_provider_preserves_httpx2_family_and_rejects_one_shot_bodies() -> None:
    pytest.importorskip("botocore")

    sync_requests: list[httpx.Request] = []
    async_requests: list[httpx.Request] = []

    def sync_handler(request: httpx.Request) -> httpx.Response:
        sync_requests.append(request)
        return model_list(request)

    async def async_handler(request: httpx.Request) -> httpx.Response:
        async_requests.append(request)
        return model_list(request)

    provider = bedrock(
        region="us-east-1",
        access_key_id="fixture-access-key",
        secret_access_key="fixture-secret-key",
        session_token="fixture-session-token",
        base_url="https://bedrock-mantle.us-east-1.api.aws/openai/v1",
    )

    with OpenAI(
        provider=provider,
        http_client=openai.DefaultHttpx2Client(transport=httpx2.MockTransport(sync_handler), trust_env=False),
        max_retries=0,
    ) as sync_client:
        sync_client.post("/responses", content=b"body", cast_to=httpx.Response)
        with pytest.raises(OpenAIError, match="requires a replayable request body"):
            sync_client.post("/responses", content=iter([b"body"]), cast_to=httpx.Response)

    async def body():
        yield b"body"

    async with AsyncOpenAI(
        provider=provider,
        http_client=openai.DefaultAsyncHttpx2Client(transport=httpx2.MockTransport(async_handler), trust_env=False),
        max_retries=0,
    ) as async_client:
        await async_client.post("/responses", content=b"body", cast_to=httpx.Response)
        with pytest.raises(OpenAIError, match="requires a replayable request body"):
            await async_client.post("/responses", content=body(), cast_to=httpx.Response)

    assert len(sync_requests) == 1
    assert len(async_requests) == 1
    assert "Credential=fixture-access-key/" in sync_requests[0].headers["authorization"]
    assert "Credential=fixture-access-key/" in async_requests[0].headers["authorization"]
    assert sync_requests[0].headers["x-amz-security-token"] == "fixture-session-token"
    assert async_requests[0].headers["x-amz-security-token"] == "fixture-session-token"
