from __future__ import annotations

import json
import asyncio
import threading

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import OpenAI, AsyncOpenAI
from openai.types.realtime.conversation_item_param import ConversationItemParam
from openai.types.realtime.response_item_reference_param import ResponseItemReferenceParam
from openai.types.realtime.response_create_event_with_references_param import ResponseCreateEventWithReferencesParam
from openai.types.realtime.realtime_response_create_params_with_references_param import (
    RealtimeResponseCreateParamsWithReferencesParam,
)

from .responses.test_websocket_session import script_server


@pytest.fixture
def reference_response() -> RealtimeResponseCreateParamsWithReferencesParam:
    reference: ResponseItemReferenceParam = {"id": "item_existing", "type": "item_reference"}
    message: ConversationItemParam = {
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": "new input 東京"}],
    }
    return {
        "conversation": "none",
        "input": [reference, message],
        "instructions": "Use both inputs.",
        "metadata": {"case": "reference-input"},
        "output_modalities": ["text"],
    }


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("operation", ["create", "send"])
async def test_realtime_reference_inputs_preserve_mixed_wire_payload(
    mode: str,
    operation: str,
    reference_response: RealtimeResponseCreateParamsWithReferencesParam,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    event: ResponseCreateEventWithReferencesParam = {
        "type": "response.create",
        "event_id": "fake-reference-request",
        "response": reference_response,
    }

    validated = threading.Event()

    def script(socket: ServerConnection) -> None:
        wire = socket.recv(timeout=5)
        assert isinstance(wire, str)
        assert json.loads(wire) == {
            "type": "response.create",
            "event_id": "fake-reference-request",
            "response": {
                "conversation": "none",
                "input": [
                    {"id": "item_existing", "type": "item_reference"},
                    {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "new input 東京"}],
                    },
                ],
                "instructions": "Use both inputs.",
                "metadata": {"case": "reference-input"},
                "output_modalities": ["text"],
            },
        }
        validated.set()

    with script_server(script) as url:
        if mode == "sync":
            with OpenAI(
                api_key="fake-reference-key", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:
                with client.realtime.connect(model="gpt-realtime") as connection:
                    if operation == "create":
                        connection.response.create(event_id="fake-reference-request", response=reference_response)
                    else:
                        connection.send(event)
                    assert validated.wait(5), "Peer did not validate the request"
        else:
            async with AsyncOpenAI(
                api_key="fake-reference-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as async_client:
                async with async_client.realtime.connect(model="gpt-realtime") as async_connection:
                    if operation == "create":
                        await asyncio.wait_for(
                            async_connection.response.create(
                                event_id="fake-reference-request", response=reference_response
                            ),
                            timeout=5,
                        )
                    else:
                        await asyncio.wait_for(async_connection.send(event), timeout=5)
                    assert await asyncio.to_thread(validated.wait, 5), "Peer did not validate the request"
