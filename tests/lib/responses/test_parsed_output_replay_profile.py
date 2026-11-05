"""Compare documented retained output versus user-converted inspection dictionaries."""

import json
import asyncio
from copy import deepcopy
from typing import Any
from contextlib import AsyncExitStack

import httpx2
import pytest

import openai
from tests.lib.responses.test_websocket_session import script_server


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("family", ["message", "function_call"])
@pytest.mark.parametrize("representation", ["retained-output", "to-dict"])
async def test_parsed_output_replay_observation_after_peer_cleanup(mode, family, representation):
    item: dict[str, Any] = (
        {
            "id": "msg",
            "type": "message",
            "role": "assistant",
            "phase": "commentary",
            "status": "completed",
            "content": [
                {"type": "output_text", "text": "plain", "annotations": [], "logprobs": None},
                # This is a server field on a different part type, not SDK parsing metadata.
                {"type": "refusal", "refusal": "fixture refusal", "parsed": {"server_fixture": [None, False]}},
            ],
        }
        if family == "message"
        else {"type": "function_call", "call_id": "c1", "name": "never_execute", "arguments": '{"kind":"inert"}'}
    )
    item["future"] = {"nullable": [None, False, 0]}
    raw = {
        "id": "resp",
        "object": "response",
        "created_at": 1,
        "model": "fixture-model",
        "status": "completed",
        "output": [deepcopy(item)],
        "metadata": {"io": "fixture"},
    }
    expected = {
        "type": "response.create",
        "model": "fixture-model",
        "input": [item],
        "store": False,
        "stream_id": "history",
    }
    seen = []

    def http_peer(request):
        assert request.url.path == "/v1/responses"
        return httpx2.Response(200, json=raw)

    def peer(socket):
        seen.append(json.loads(socket.recv(timeout=4)))
        socket.send(json.dumps({"type": "future.replay.confirm", "stream_id": "history"}))

    with script_server(peer) as url:
        async with AsyncExitStack() as stack:
            if mode == "sync":
                client = stack.enter_context(
                    openai.OpenAI(
                        api_key="fake",
                        base_url="http://localhost/v1",
                        websocket_base_url=url,
                        http_client=httpx2.Client(transport=httpx2.MockTransport(http_peer)),
                    )
                )
                conn = stack.enter_context(client.responses.connect(max_retries=0))
            else:
                client = await stack.enter_async_context(
                    openai.AsyncOpenAI(
                        api_key="fake",
                        base_url="http://localhost/v1",
                        websocket_base_url=url,
                        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(http_peer)),
                    )
                )
                conn = await stack.enter_async_context(client.responses.connect(max_retries=0))

            async def call(obj, name, **kwargs):
                if mode == "sync":
                    return await asyncio.wait_for(asyncio.to_thread(getattr(obj, name), **kwargs), 4)
                return await asyncio.wait_for(getattr(obj, name)(**kwargs), 4)

            parsed = await call(client.responses, "parse", model="fixture-model", input="synthetic")
            inspection = parsed.output[0].to_dict(exclude_unset=True)
            history = parsed.output if representation == "retained-output" else [inspection]
            await call(conn.response, "create", model="fixture-model", input=history, store=False, stream_id="history")
            event = await call(conn, "recv")
            assert event.to_dict(exclude_unset=True) == {"type": "future.replay.confirm", "stream_id": "history"}
            assert parsed.output[0].to_dict(exclude_unset=True) == inspection
    assert len(seen) == 1
    if representation == "to-dict":
        # Inspection dicts are caller-owned, including their parsed fields.
        expected["input"] = [inspection]
    assert seen[0] == expected
