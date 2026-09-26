from __future__ import annotations

import json
from typing import Any, cast

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import OpenAI, AsyncOpenAI, omit, not_given
from openai.resources.beta.responses.responses import (
    ResponsesConnectionManager as BetaResponsesConnectionManager,
    AsyncResponsesConnectionManager as BetaAsyncResponsesConnectionManager,
)
from openai.types.beta.beta_responses_client_event import ResponseCreate as BetaResponseCreate
from openai.types.responses.responses_client_event import ResponseCreate
from openai.types.beta.beta_response_completed_event import BetaResponseCompletedEvent
from openai.types.responses.response_completed_event import ResponseCompletedEvent

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

    def handle_completed(event: ResponseCompletedEvent | BetaResponseCompletedEvent) -> None:
        handled.append(event.response.id)

    first: dict[str, Any] = {
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
    with script_server(script) as url:
        if mode == "sync":
            with OpenAI(
                api_key="fake-preconnect-key", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:
                manager = client.beta.responses.connect() if beta else client.responses.connect()
                manager.send(cast(Any, first))
                if isinstance(manager, BetaResponsesConnectionManager):
                    manager.send(BetaResponseCreate(type="response.create", model="gpt-4o-mini", input="second"))
                else:
                    manager.send(ResponseCreate(type="response.create", model="gpt-4o-mini", input="second"))
                manager.on("response.completed", handle_completed)
                with manager as connection:
                    connection.dispatch_events()
        else:
            async with AsyncOpenAI(
                api_key="fake-preconnect-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as async_client:
                # Queueing is synchronous even when opening/reading is async.
                async_manager = async_client.beta.responses.connect() if beta else async_client.responses.connect()
                async_manager.send(cast(Any, first))
                if isinstance(async_manager, BetaAsyncResponsesConnectionManager):
                    async_manager.send(BetaResponseCreate(type="response.create", model="gpt-4o-mini", input="second"))
                else:
                    async_manager.send(ResponseCreate(type="response.create", model="gpt-4o-mini", input="second"))
                async_manager.on("response.completed", handle_completed)
                async with async_manager as async_connection:
                    await async_connection.dispatch_events()

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
