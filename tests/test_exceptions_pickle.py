from __future__ import annotations

import pickle

import httpx2

from openai import APITimeoutError, BadRequestError
from openai._exceptions import WebSocketConnectionClosedError


def test_timeout_error_pickle_round_trip() -> None:
    request = httpx2.Request("POST", "https://example.test/v1/responses")
    error = APITimeoutError(request)

    restored = pickle.loads(pickle.dumps(error))

    assert isinstance(restored, APITimeoutError)
    assert str(restored) == "Request timed out."
    assert restored.message == "Request timed out."
    assert restored.request.method == "POST"
    assert str(restored.request.url) == "https://example.test/v1/responses"
    assert restored.body is None


def test_status_error_pickle_round_trip_preserves_response_state() -> None:
    request = httpx2.Request("POST", "https://example.test/v1/responses")
    response = httpx2.Response(
        400,
        request=request,
        headers={"x-request-id": "req_123"},
        json={"error": "bad request"},
    )
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
    assert restored.response.json() == {"error": "bad request"}


def test_websocket_error_pickle_round_trip_preserves_unsent_messages() -> None:
    error = WebSocketConnectionClosedError(
        "connection closed",
        unsent_messages=["first", "second"],
    )

    restored = pickle.loads(pickle.dumps(error))

    assert isinstance(restored, WebSocketConnectionClosedError)
    assert str(restored) == "connection closed"
    assert restored.unsent_messages == ["first", "second"]
