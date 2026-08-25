from __future__ import annotations

import asyncio
import pickle
from collections.abc import Iterator
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import httpx2
import pytest

from openai import APITimeoutError, AsyncOpenAI, BadRequestError, OpenAI, OpenAIError
from openai._exceptions import SubjectTokenProviderError, WebSocketConnectionClosedError


_ERROR_PAYLOAD = b'{"error":{"message":"bad request","type":"invalid_request_error","param":null,"code":"bad_request"}}'
_REDACTED_REQUEST_URL = "https://redacted.invalid/"


class _CustomNewOpenAIError(OpenAIError):
    def __new__(cls, message: str) -> _CustomNewOpenAIError:
        return Exception.__new__(cls)


class _SlottedOpenAIError(OpenAIError):
    __slots__ = ("context",)

    def __init__(self, message: str, context: str) -> None:
        super().__init__(message, context)
        self.context = context


class _BadRequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        self.send_response(400)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(_ERROR_PAYLOAD)))
        self.send_header("x-request-id", "req_transport")
        self.end_headers()
        self.wfile.write(_ERROR_PAYLOAD)

    def log_message(self, format: str, *args: object) -> None:
        pass


@pytest.fixture
def transport_error_base_url() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _BadRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_timeout_error_pickle_round_trip() -> None:
    request = httpx2.Request("POST", "https://example.test/v1/responses")
    error = APITimeoutError(request)

    restored = pickle.loads(pickle.dumps(error))

    assert isinstance(restored, APITimeoutError)
    assert str(restored) == "Request timed out."
    assert restored.message == "Request timed out."
    assert restored.request.method == "POST"
    assert str(restored.request.url) == _REDACTED_REQUEST_URL
    assert restored.body is None


def test_request_private_data_is_omitted_and_timeout_is_preserved() -> None:
    request = httpx2.Request(
        "POST",
        "https://example.test/v1/responses?customer_secret=query-private",
        content=b"request-body-private",
        extensions={
            "timeout": {
                "connect": 1.0,
                "read": 2.0,
                "write": 3.0,
                "pool": 4.0,
            }
        },
    )
    error = APITimeoutError(request)

    payload = pickle.dumps(error)
    restored = pickle.loads(payload)

    assert b"query-private" not in payload
    assert b"request-body-private" not in payload
    assert str(restored.request.url) == _REDACTED_REQUEST_URL
    assert restored.request.extensions["timeout"] == {
        "connect": 1.0,
        "read": 2.0,
        "write": 3.0,
        "pool": 4.0,
    }


@pytest.mark.parametrize(
    ("header_name", "header_value"),
    [
        ("Authorization", "Bearer sk-openai-secret"),
        ("api-key", "azure-secret-key"),
    ],
)
def test_request_credentials_are_redacted_from_pickle(header_name: str, header_value: str) -> None:
    request = httpx2.Request(
        "POST",
        "https://example.test/v1/responses",
        headers={header_name: header_value},
    )
    error = APITimeoutError(request)

    payload = pickle.dumps(error)
    restored = pickle.loads(payload)

    assert header_value.encode() not in payload
    assert restored.request.headers[header_name] == "<redacted>"


def test_response_private_data_is_omitted_and_headers_are_redacted() -> None:
    request = httpx2.Request("POST", "https://example.test/v1/token")
    response = httpx2.Response(
        400,
        request=request,
        headers={
            "Authorization": "Bearer response-auth-secret",
            "api-key": "response-api-key-secret",
            "Set-Cookie": "session=response-cookie-secret",
            "x-request-id": "req_123",
        },
        content=b"response-body-private",
    )
    error = SubjectTokenProviderError("token exchange failed", response=response)

    payload = pickle.dumps(error)
    restored = pickle.loads(payload)

    assert b"response-auth-secret" not in payload
    assert b"response-api-key-secret" not in payload
    assert b"response-cookie-secret" not in payload
    assert b"response-body-private" not in payload
    assert restored.response is not None
    assert restored.response.headers["Authorization"] == "<redacted>"
    assert restored.response.headers["api-key"] == "<redacted>"
    assert restored.response.headers["Set-Cookie"] == "<redacted>"
    assert restored.response.headers["x-request-id"] == "req_123"
    assert restored.response.content == b""


def test_status_error_pickle_round_trip_preserves_response_state() -> None:
    request = httpx2.Request("POST", "https://example.test/v1/responses")
    response = httpx2.Response(
        400,
        request=request,
        headers={"x-request-id": "req_123"},
        json={"error": "bad request"},
    )
    response.elapsed = timedelta(milliseconds=125)
    body = {
        "code": "invalid_value",
        "param": "input",
        "type": "invalid_request_error",
    }
    error = BadRequestError("Bad request", response=response, body=body)

    restored = pickle.loads(pickle.dumps(error))

    assert isinstance(restored, BadRequestError)
    assert restored.status_code == 400
    assert restored.request_id == "req_123"
    assert restored.body == body
    assert restored.code == "invalid_value"
    assert restored.param == "input"
    assert restored.type == "invalid_request_error"
    assert restored.response.status_code == 400
    assert restored.response.content == b""
    assert restored.response.elapsed == timedelta(milliseconds=125)


def _assert_transport_status_error_pickle_round_trip(error: BadRequestError) -> None:
    restored = pickle.loads(pickle.dumps(error))

    assert isinstance(restored, BadRequestError)
    assert restored.status_code == 400
    assert restored.request_id == "req_transport"
    assert restored.response.status_code == 400
    assert restored.response.request is restored.request
    assert restored.request.method == "GET"
    assert str(restored.request.url) == _REDACTED_REQUEST_URL
    assert restored.body == {
        "error": {
            "message": "bad request",
            "type": "invalid_request_error",
            "param": None,
            "code": "bad_request",
        }
    }
    assert restored.response.content == b""
    assert restored.request.headers["Authorization"] == "<redacted>"
    assert error.request.headers["Authorization"] != restored.request.headers["Authorization"]
    assert restored.response.elapsed >= timedelta(0)


def test_status_error_from_sync_transport_pickle_round_trip(transport_error_base_url: str) -> None:
    with OpenAI(api_key="test", base_url=transport_error_base_url) as client:
        with pytest.raises(BadRequestError) as exc_info:
            client.models.list()

        _assert_transport_status_error_pickle_round_trip(exc_info.value)


def test_status_error_from_async_transport_pickle_round_trip(transport_error_base_url: str) -> None:
    async def run() -> None:
        async with AsyncOpenAI(api_key="test", base_url=transport_error_base_url) as client:
            with pytest.raises(BadRequestError) as exc_info:
                await client.models.list()

            _assert_transport_status_error_pickle_round_trip(exc_info.value)

    asyncio.run(run())


def test_custom_error_subclass_with_required_new_argument_pickle_round_trip() -> None:
    error = _CustomNewOpenAIError("custom error")

    restored = pickle.loads(pickle.dumps(error))

    assert isinstance(restored, _CustomNewOpenAIError)
    assert str(restored) == "custom error"


def test_custom_error_subclass_preserves_slotted_state() -> None:
    error = _SlottedOpenAIError("custom error", "slot context")

    restored = pickle.loads(pickle.dumps(error))

    assert isinstance(restored, _SlottedOpenAIError)
    assert restored.args == ("custom error", "slot context")
    assert restored.context == "slot context"


def test_websocket_error_pickle_round_trip_preserves_unsent_messages() -> None:
    error = WebSocketConnectionClosedError(
        "connection closed",
        unsent_messages=["first", "second"],
    )

    restored = pickle.loads(pickle.dumps(error))

    assert isinstance(restored, WebSocketConnectionClosedError)
    assert str(restored) == "connection closed"
    assert restored.unsent_messages == ["first", "second"]
