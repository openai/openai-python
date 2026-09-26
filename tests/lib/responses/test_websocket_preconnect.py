from __future__ import annotations

import json
from typing import Any, cast

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import OpenAI, AsyncOpenAI, omit, not_given
from openai.types.responses.responses_client_event import ResponseCreate

from .test_websocket_session import script_server, response_event


@pytest.fixture(autouse=True)
def bypass_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("beta", [False, True], ids=["public", "beta"])
async def test_preopen_sends_normalize_omissions_without_losing_values_or_order(mode: str, beta: bool) -> None:
    received: list[dict[str, Any]] = []
    handled: list[str] = []

    def script(socket: ServerConnection) -> None:
        for _ in range(2):
            received.append(json.loads(socket.recv(timeout=5)))
        socket.send(json.dumps(response_event("completed", id="resp_queued")))
        socket.close()

    first = {
        "type": "response.create",
        "model": "gpt-4o-mini",
        "instructions": omit,
        "previous_response_id": not_given,
        "input": [],
        "tools": [],
        "store": False,
        "metadata": {},
        "tool_choice": None,
        "future_option": {"enabled": False, "value": None, "empty": []},
    }
    second = ResponseCreate(type="response.create", model="gpt-4o-mini", input="second")

    with script_server(script) as url:
        if mode == "sync":
            with OpenAI(
                api_key="fake-preconnect-key", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:
                resource = client.beta.responses if beta else client.responses
                manager = resource.connect()
                manager.on("response.completed", lambda event: handled.append(event.response.id))
                manager.send(cast(Any, first))
                manager.send(second)
                with manager as connection:
                    connection.dispatch_events()
        else:
            async with AsyncOpenAI(
                api_key="fake-preconnect-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as client:
                resource = client.beta.responses if beta else client.responses
                manager = resource.connect()
                manager.on("response.completed", lambda event: handled.append(event.response.id))
                # Queueing is synchronous even when opening/reading is async.
                manager.send(cast(Any, first))
                manager.send(second)
                async with manager as connection:
                    await connection.dispatch_events()

    assert received == [
        {
            "type": "response.create",
            "model": "gpt-4o-mini",
            "input": [],
            "tools": [],
            "store": False,
            "metadata": {},
            "tool_choice": None,
            "future_option": {"enabled": False, "value": None, "empty": []},
        },
        {"type": "response.create", "model": "gpt-4o-mini", "input": "second"},
    ]
    assert handled == ["resp_queued"]
