from __future__ import annotations

import json
from typing import Any, cast

from openai.resources.responses.responses import ResponsesConnection, AsyncResponsesConnection


class FakeWebSocket:
    def __init__(self) -> None:
        self.sent: list[str] = []

    def send(self, data: str) -> None:
        self.sent.append(data)


class AsyncFakeWebSocket:
    def __init__(self) -> None:
        self.sent: list[str] = []

    async def send(self, data: str) -> None:
        self.sent.append(data)


def test_responses_websocket_create_preserves_decimal_temperature() -> None:
    websocket = FakeWebSocket()
    connection = ResponsesConnection(cast(Any, websocket))

    connection.response.create(model="gpt-4.1-mini", input="hello", temperature=1.2)

    assert len(websocket.sent) == 1
    payload = json.loads(websocket.sent[0])
    assert payload["type"] == "response.create"
    assert payload["temperature"] == 1.2
    assert isinstance(payload["temperature"], float)


async def test_async_responses_websocket_create_preserves_decimal_temperature() -> None:
    websocket = AsyncFakeWebSocket()
    connection = AsyncResponsesConnection(cast(Any, websocket))

    await connection.response.create(model="gpt-4.1-mini", input="hello", temperature=1.2)

    assert len(websocket.sent) == 1
    payload = json.loads(websocket.sent[0])
    assert payload["type"] == "response.create"
    assert payload["temperature"] == 1.2
    assert isinstance(payload["temperature"], float)
