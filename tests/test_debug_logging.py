from __future__ import annotations

import io
import json
import logging
import importlib
from typing import Any, AsyncIterator
from unittest.mock import Mock, AsyncMock, patch

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, APIStatusError, APITimeoutError, APIConnectionError
from openai._models import FinalRequestOptions

FAKE_SECRET = "fake-private-value-for-logging-tests"
BASE_URL = "https://example.test/v1"


def assert_safe_logs(caplog: pytest.LogCaptureFixture) -> list[str]:
    records = [record for record in caplog.records if record.name.startswith("openai.") or record.name == "httpx2"]
    assert records
    # Handlers may retain the unformatted arguments or exception, not just text.
    for record in records:
        assert FAKE_SECRET not in record.getMessage()
        assert FAKE_SECRET not in repr(record.args)
        assert record.exc_info is None
    return [record.getMessage() for record in records]


def request_options(kind: str) -> FinalRequestOptions:
    common: dict[str, Any] = {
        "method": "post",
        "url": "/logging-test?private=" + FAKE_SECRET,
        "headers": {"Authorization": FAKE_SECRET, "X-Custom": FAKE_SECRET},
        "params": {"private": FAKE_SECRET},
        "idempotency_key": FAKE_SECRET,
    }
    if kind == "json":
        common.update(
            json_data={"input": FAKE_SECRET, "tools": [{"authorization": FAKE_SECRET}]},
            extra_json={"nested": {"headers": {"X-Custom": FAKE_SECRET}}},
        )
    elif kind == "json-bytes":
        common["json_data"] = FAKE_SECRET.encode()
    elif kind == "content":
        common["content"] = FAKE_SECRET.encode()
    elif kind == "stream":
        common["content"] = iter([FAKE_SECRET.encode()])
    elif kind == "multipart":
        common["json_data"] = {"purpose": FAKE_SECRET}
        common["files"] = {"file": (FAKE_SECRET + ".txt", io.BytesIO(FAKE_SECRET.encode()))}
        common["headers"]["Content-Type"] = "multipart/form-data"
    else:
        raise AssertionError(kind)
    return FinalRequestOptions.construct(**common)


def echo_request(request: httpx2.Request) -> httpx2.Response:
    assert FAKE_SECRET.encode() in request.content
    assert request.headers["X-Custom"] == FAKE_SECRET
    assert request.url.params["private"] == FAKE_SECRET
    return httpx2.Response(
        200,
        json={"result": FAKE_SECRET},
        headers={"x-private": FAKE_SECRET, "x-request-id": "req_fake_logging"},
    )


@pytest.mark.parametrize("kind", ["json", "json-bytes", "content", "stream", "multipart"])
def test_sync_request_metadata(kind: str, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG, logger="openai"):
        with OpenAI(
            api_key="fake-api-key",
            base_url=BASE_URL,
            http_client=httpx2.Client(transport=httpx2.MockTransport(echo_request)),
        ) as client:
            result = client.request(object, request_options(kind))
    assert result == {"result": FAKE_SECRET}
    messages = assert_safe_logs(caplog)
    assert "Building HTTP request: method=POST retries_taken=0" in messages
    assert "HTTP Response: POST 200" in messages
    assert "request_id: req_fake_logging" in messages


@pytest.mark.parametrize("kind", ["json", "json-bytes", "content", "stream", "multipart"])
async def test_async_request_metadata(kind: str, caplog: pytest.LogCaptureFixture) -> None:
    options = request_options(kind)
    if kind == "stream":

        async def content() -> AsyncIterator[bytes]:
            yield FAKE_SECRET.encode()

        options.content = content()
    with caplog.at_level(logging.DEBUG, logger="openai"):
        async with AsyncOpenAI(
            api_key="fake-api-key",
            base_url=BASE_URL,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(echo_request)),
        ) as client:
            result = await client.request(object, options)
    assert result == {"result": FAKE_SECRET}
    messages = assert_safe_logs(caplog)
    assert "Building HTTP request: method=POST retries_taken=0" in messages
    assert "HTTP Response: POST 200" in messages
    assert "request_id: req_fake_logging" in messages


def mcp_response(request: httpx2.Request) -> httpx2.Response:
    body = json.loads(request.content)
    assert body["input"] == FAKE_SECRET
    assert body["tools"][0]["authorization"] == FAKE_SECRET
    assert body["tools"][0]["headers"]["X-Custom"] == FAKE_SECRET
    return httpx2.Response(200, json={"id": "resp_fake_logging", "object": "response", "output": []})


def mcp_tools() -> Any:
    return [
        {
            "type": "mcp",
            "server_label": "fake",
            "server_url": "https://example.test/mcp",
            "authorization": FAKE_SECRET,
            "headers": {"X-Custom": FAKE_SECRET},
        }
    ]


def test_sync_public_mcp_request(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG, logger="openai"):
        with OpenAI(
            api_key="fake-api-key",
            base_url=BASE_URL,
            http_client=httpx2.Client(transport=httpx2.MockTransport(mcp_response)),
        ) as client:
            result = client.responses.create(model="fake-model", input=FAKE_SECRET, tools=mcp_tools())
    assert result.id == "resp_fake_logging"
    assert_safe_logs(caplog)


async def test_async_public_mcp_request(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG, logger="openai"):
        async with AsyncOpenAI(
            api_key="fake-api-key",
            base_url=BASE_URL,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(mcp_response)),
        ) as client:
            result = await client.responses.create(model="fake-model", input=FAKE_SECRET, tools=mcp_tools())
    assert result.id == "resp_fake_logging"
    assert_safe_logs(caplog)


@pytest.mark.parametrize("failure", ["status", "timeout", "connection"])
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_failure_and_retry_metadata(failure: str, asynchronous: bool, caplog: pytest.LogCaptureFixture) -> None:
    calls = 0

    def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal calls
        calls += 1
        if failure == "timeout":
            raise httpx2.ReadTimeout(FAKE_SECRET, request=request)
        if failure == "connection":
            raise RuntimeError(FAKE_SECRET)
        return httpx2.Response(
            500, json={"error": {"message": FAKE_SECRET}}, headers={"x-private": FAKE_SECRET, "retry-after-ms": "1"}
        )

    expected = {"status": APIStatusError, "timeout": APITimeoutError, "connection": APIConnectionError}[failure]
    kwargs: dict[str, Any] = {"api_key": "fake-api-key", "base_url": BASE_URL, "max_retries": 1}
    with caplog.at_level(logging.DEBUG, logger="openai"):
        if asynchronous:
            async with AsyncOpenAI(
                **kwargs, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
            ) as async_client:
                with pytest.raises(expected) as exc:
                    await async_client.get("/logging-test?private=" + FAKE_SECRET, cast_to=object)
        else:
            with OpenAI(**kwargs, http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
                with pytest.raises(expected) as exc:
                    client.get("/logging-test?private=" + FAKE_SECRET, cast_to=object)
    assert calls == 2
    if failure == "status":
        assert isinstance(exc.value, APIStatusError)
        assert exc.value.body == {"message": FAKE_SECRET}
    assert any("Retrying request in" in message for message in assert_safe_logs(caplog))


WEBSOCKET_MODULES = [
    "openai.resources.realtime.realtime",
    "openai.resources.responses.responses",
    "openai.resources.beta.responses.responses",
    "openai.resources.beta.realtime.realtime",
]


@pytest.mark.parametrize("module_name", WEBSOCKET_MODULES)
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("parsed", [False, True])
async def test_websocket_receive_metadata(
    module_name: str, asynchronous: bool, parsed: bool, caplog: pytest.LogCaptureFixture
) -> None:
    module = importlib.import_module(module_name)
    name = "RealtimeConnection" if ".realtime." in module_name else "ResponsesConnection"
    cls = getattr(module, ("Async" if asynchronous else "") + name)
    payload = (
        json.dumps({"type": "response.output_text.delta", "delta": FAKE_SECRET}).encode()
        if parsed
        else b"\x00" + FAKE_SECRET.encode()
    )
    websocket = Mock()
    websocket.recv = AsyncMock(return_value=payload) if asynchronous else Mock(return_value=payload)
    connection = cls(websocket)
    with caplog.at_level(logging.DEBUG, logger="openai"):
        result = connection.recv() if parsed else connection.recv_bytes()
        if asynchronous:
            result = await result
    websocket.recv.assert_called_once_with(decode=False)
    if parsed:
        assert result.type == "response.output_text.delta"
        assert result.delta == FAKE_SECRET
    else:
        assert result is payload
    assert assert_safe_logs(caplog) == [f"Received WebSocket message: {len(payload)} bytes"]


@pytest.mark.parametrize("module_name", WEBSOCKET_MODULES)
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_websocket_connection_metadata(
    module_name: str, asynchronous: bool, caplog: pytest.LogCaptureFixture
) -> None:
    module = importlib.import_module(module_name)
    realtime = ".realtime." in module_name
    name = "Realtime" if realtime else "Responses"
    cls = getattr(module, ("Async" if asynchronous else "") + name)
    websocket = Mock()
    websocket.send = AsyncMock() if asynchronous else Mock()
    websocket.close = AsyncMock() if asynchronous else Mock()
    connect = AsyncMock(return_value=websocket) if asynchronous else Mock(return_value=websocket)
    kwargs: dict[str, Any] = {
        "extra_query": {"private": FAKE_SECRET},
        "extra_headers": {"X-Custom": FAKE_SECRET},
        "websocket_connection_options": {"origin": FAKE_SECRET},
    }
    if realtime:
        kwargs["model"] = "fake-model"
    with (
        caplog.at_level(logging.DEBUG, logger="openai"),
        patch("openai.lib._websocket._WebSocketConnect" if asynchronous else "websockets.sync.client.connect", connect),
    ):
        if asynchronous:
            async with AsyncOpenAI(
                api_key="fake-api-key",
                base_url=BASE_URL,
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(echo_request)),
            ) as async_client:
                async with cls(async_client).connect(**kwargs):
                    pass
        else:
            with OpenAI(
                api_key="fake-api-key",
                base_url=BASE_URL,
                http_client=httpx2.Client(transport=httpx2.MockTransport(echo_request)),
            ) as client:
                with cls(client).connect(**kwargs):
                    pass
    assert FAKE_SECRET in connect.call_args.args[0]
    assert connect.call_args.kwargs["additional_headers"]["X-Custom"] == FAKE_SECRET
    assert connect.call_args.kwargs["origin"] == FAKE_SECRET
    assert "Connecting to WebSocket API" in assert_safe_logs(caplog)


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_response_parser_metadata(legacy: bool, asynchronous: bool, caplog: pytest.LogCaptureFixture) -> None:
    from openai._models import BaseModel
    from openai._response import APIResponse, AsyncAPIResponse
    from openai._legacy_response import LegacyAPIResponse

    raw = httpx2.Response(200, text=FAKE_SECRET)
    raw.json = Mock(side_effect=ValueError(FAKE_SECRET))
    kwargs: dict[str, Any] = {
        "raw": raw,
        "cast_to": BaseModel,
        "stream": False,
        "stream_cls": None,
        "options": FinalRequestOptions.construct(method="get", url="/logging-test"),
    }
    with caplog.at_level(logging.DEBUG, logger="openai"):
        if asynchronous:
            async with AsyncOpenAI(
                api_key="fake-api-key", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(echo_request))
            ) as async_client:
                if legacy:
                    result = LegacyAPIResponse[Any](client=async_client, **kwargs).parse()
                else:
                    result = await AsyncAPIResponse[Any](client=async_client, **kwargs).parse()
        else:
            with OpenAI(
                api_key="fake-api-key", http_client=httpx2.Client(transport=httpx2.MockTransport(echo_request))
            ) as client:
                if legacy:
                    result = LegacyAPIResponse[Any](client=client, **kwargs).parse()
                else:
                    result = APIResponse[Any](client=client, **kwargs).parse()
    assert result == FAKE_SECRET
    assert assert_safe_logs(caplog) == ["Could not read JSON from response data due to ValueError"]


@pytest.mark.parametrize("module_name", WEBSOCKET_MODULES[:3])
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_websocket_queue_failure_metadata(
    module_name: str, asynchronous: bool, caplog: pytest.LogCaptureFixture
) -> None:
    module = importlib.import_module(module_name)
    name = "RealtimeConnection" if ".realtime." in module_name else "ResponsesConnection"
    cls = getattr(module, ("Async" if asynchronous else "") + name)
    websocket = Mock()
    websocket.send = (
        AsyncMock(side_effect=RuntimeError(FAKE_SECRET))
        if asynchronous
        else Mock(side_effect=RuntimeError(FAKE_SECRET))
    )
    connection = cls(websocket)
    connection._send_queue.enqueue(FAKE_SECRET)
    with caplog.at_level(logging.DEBUG, logger="openai"):
        if asynchronous:
            await connection._flush_send_queue()
        else:
            connection._flush_send_queue()
    websocket.send.assert_called_once_with(FAKE_SECRET)
    assert assert_safe_logs(caplog) == ["Failed to flush send queue after reconnect"]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method", ["post", FAKE_SECRET])
async def test_custom_method_metadata(method: str, asynchronous: bool, caplog: pytest.LogCaptureFixture) -> None:
    received: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        received.append(request.method)
        return httpx2.Response(200, json={"ok": True})

    options = FinalRequestOptions.construct(method=method, url="/logging-test")
    with caplog.at_level(logging.DEBUG, logger="openai"):
        if asynchronous:
            async with AsyncOpenAI(
                api_key="fake-api-key",
                base_url=BASE_URL,
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler)),
            ) as async_client:
                assert await async_client.request(object, options) == {"ok": True}
        else:
            with OpenAI(
                api_key="fake-api-key",
                base_url=BASE_URL,
                http_client=httpx2.Client(transport=httpx2.MockTransport(handler)),
            ) as client:
                assert client.request(object, options) == {"ok": True}
    assert received == [method.upper()]
    expected = "POST" if method == "post" else "<custom>"
    messages = assert_safe_logs(caplog)
    assert f"Building HTTP request: method={expected} retries_taken=0" in messages
    assert f"Sending HTTP Request: {expected}" in messages
    assert f"HTTP Response: {expected} 200" in messages
    assert FAKE_SECRET.upper() not in "\n".join(messages)


@pytest.mark.parametrize("setting", ["debug", "info"])
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_sdk_log_switch_does_not_enable_transport_payloads(
    setting: str, asynchronous: bool, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    from openai._utils._logs import setup_logging

    # Exercise the documented switch with normal application logging defaults.
    with (
        caplog.at_level(logging.WARNING),
        caplog.at_level(logging.NOTSET, logger="httpx2"),
        caplog.at_level(logging.WARNING, logger="openai"),
    ):
        monkeypatch.setattr(caplog.handler, "level", logging.NOTSET)
        monkeypatch.setenv("OPENAI_LOG", setting)
        setup_logging()
        if asynchronous:
            async with AsyncOpenAI(
                api_key="fake-api-key",
                base_url=BASE_URL,
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(echo_request)),
            ) as async_client:
                assert await async_client.request(object, request_options("json")) == {"result": FAKE_SECRET}
        else:
            with OpenAI(
                api_key="fake-api-key",
                base_url=BASE_URL,
                http_client=httpx2.Client(transport=httpx2.MockTransport(echo_request)),
            ) as client:
                assert client.request(object, request_options("json")) == {"result": FAKE_SECRET}
        assert logging.getLogger("httpx2").level == logging.NOTSET
    assert not any(FAKE_SECRET in record.getMessage() or FAKE_SECRET in repr(record.args) for record in caplog.records)
