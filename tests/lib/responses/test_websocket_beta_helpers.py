from __future__ import annotations

import json
import warnings
from copy import deepcopy
from typing import Any, AsyncGenerator
from contextlib import asynccontextmanager

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import OpenAI, AsyncOpenAI
from openai._compat import model_parse
from openai._models import BaseModel
from openai.types.responses import Response
from openai.lib.responses_websocket import (
    ResponsesWebSocketError,
    ResponsesWebSocketSession,
    ResponsesWebSocketAccumulator,
    AsyncResponsesWebSocketSession,
)
from openai.types.beta.beta_response import BetaResponse
from openai.types.beta.beta_response_failed_event import BetaResponseFailedEvent
from openai.types.beta.beta_response_created_event import BetaResponseCreatedEvent
from openai.types.beta.beta_responses_client_event import ResponseCreate as BetaResponseCreate
from openai.types.beta.beta_responses_server_event import (
    BetaResponseWsError,
    BetaResponseWsCreated,
    BetaResponseWsCompleted,
)
from openai.types.beta.beta_response_completed_event import BetaResponseCompletedEvent
from openai.types.beta.beta_response_incomplete_event import BetaResponseIncompleteEvent
from openai.types.beta.beta_response_output_item_done_event import BetaResponseOutputItemDoneEvent

from .test_websocket_session import LIMITS, Driver, bypass_proxy as bypass_proxy, script_server, response_event


@asynccontextmanager
async def beta_session(mode: str, url: str) -> AsyncGenerator[Driver]:
    if mode == "sync":
        with (
            OpenAI(api_key="fake-beta-key", base_url=url, http_client=httpx2.Client(trust_env=False)) as client,
            client.beta.responses.connect() as connection,
            ResponsesWebSocketSession(connection, limits=LIMITS) as session,
        ):
            yield Driver(session, mode)
    else:
        async with (
            AsyncOpenAI(
                api_key="fake-beta-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as client,
            client.beta.responses.connect() as connection,
            AsyncResponsesWebSocketSession(connection, limits=LIMITS) as session,
        ):
            yield Driver(session, mode)


def reasoning(marker: str) -> dict[str, Any]:
    return {
        "type": "reasoning",
        "id": "reason",
        "status": "completed",
        "summary": [{"type": "summary_text", "text": marker}],
        "encrypted_content": "opaque-" + marker,
        "agent": {"agent_name": "synthetic-agent"},
        "opaque_item": {"nested": [marker, {"keep": True}]},
    }


def beta_frame(kind: str, output: list[dict[str, Any]], sequence: int) -> dict[str, Any]:
    event = response_event(kind, "beta", output=output)
    event["sequence_number"] = sequence
    event["opaque_event"] = {"nested": ["keep", None]}
    event["response"]["opaque_response"] = {"nested": [kind]}
    return event


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("terminal", ["completed", "failed", "incomplete"])
@pytest.mark.parametrize("scaffold", [False, True])
@pytest.mark.parametrize("full_output", [False, True])
async def test_beta_native_final_and_caller_fed_family(
    mode: str,
    terminal: str,
    scaffold: bool,
    full_output: bool,
) -> None:
    frames = [beta_frame("created", [], 1)] if scaffold else []
    if scaffold:
        frames.append(
            {
                "type": "response.output_item.done",
                "sequence_number": 2,
                "stream_id": "beta",
                "output_index": 0,
                "item": reasoning("item-done"),
            }
        )
    final = beta_frame(terminal, [reasoning("terminal")] if full_output else [], len(frames) + 1)
    frames.append(final)
    models = {
        "completed": BetaResponseCompletedEvent,
        "failed": BetaResponseFailedEvent,
        "incomplete": BetaResponseIncompleteEvent,
    }
    model_parse(models[terminal], final)
    if scaffold:
        model_parse(BetaResponseCreatedEvent, frames[0])
        model_parse(BetaResponseOutputItemDoneEvent, frames[1])

    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv(timeout=5)) == {"type": "response.create", "stream_id": "beta"}
        for event in frames:
            socket.send(json.dumps(event))

    with script_server(script) as url:
        async with beta_session(mode, url) as driver:
            lane = driver.session.lane("beta")
            command = BetaResponseCreate(type="response.create") if scaffold else {"type": "response.create"}
            before_command = deepcopy(command.to_dict() if isinstance(command, BaseModel) else command)
            await driver.call(lane, "send", command)
            assert (command.to_dict() if isinstance(command, BaseModel) else command) == before_command
            accumulator = ResponsesWebSocketAccumulator(response_type=BetaResponse)
            received = []
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                for expected in frames:
                    event = await driver.call(lane, "recv")
                    assert event.to_dict() == expected
                    received.append(event)
                    accumulator.add_event(event)
                managed = await driver.call(lane, "get_final_response")
                collected = accumulator.get_final_response()
                assert isinstance(managed, BetaResponse)
                assert managed is not received[-1].response
                if full_output:
                    assert managed.output[0] is not received[-1].response.output[0]
                assert isinstance(collected, BetaResponse)
                assert managed.to_dict() == final["response"]
                assert collected.to_dict() == final["response"]
                assert not caught
            assert [event.to_dict() for event in received] == frames
            saved = accumulator.detailed_snapshot()
            collected.output.clear()
            assert accumulator.get_final_response().to_dict() == final["response"]
            accumulator.reset()
            assert saved["response"]["opaque_response"] == final["response"]["opaque_response"]
            assert [event.to_dict() for event in received] == frames
            assert managed.to_dict() == final["response"]


@pytest.mark.parametrize("beta", [False, True])
def test_caller_fed_selected_family_reset_and_rejection(beta: bool) -> None:
    # Runtime rejection from an untyped caller; separate native witnesses check
    # the public positive and negative type contracts without casts or ignores.
    accumulator: Any = (
        ResponsesWebSocketAccumulator(response_type=BetaResponse) if beta else ResponsesWebSocketAccumulator()
    )
    chosen = BetaResponseCreatedEvent if beta else None
    from openai.types.responses.responses_server_event import ResponseWsCreated

    model = chosen or ResponseWsCreated
    wrong = ResponseWsCreated if beta else BetaResponseCreatedEvent
    created = beta_frame("created", [], 1)
    original = deepcopy(created)
    accumulator.add_event(model_parse(model, created))
    snapshot = accumulator.detailed_snapshot()
    with pytest.raises(ValueError, match="missing a valid response"):
        accumulator.add_event(model_parse(wrong, created))
    assert accumulator.detailed_snapshot() == snapshot
    accumulator.reset()
    accumulator.add_event(model_parse(model, created))
    assert accumulator.detailed_snapshot() == snapshot
    assert created == original
    assert isinstance(model_parse(model, created).response, BetaResponse if beta else Response)


@pytest.mark.parametrize("mismatch", ["lane", "response"])
def test_beta_caller_fed_identity_rejection_keeps_prior_snapshot(mismatch: str) -> None:
    accumulator = ResponsesWebSocketAccumulator(response_type=BetaResponse)
    created = beta_frame("created", [], 1)
    accumulator.add_event(model_parse(BetaResponseWsCreated, created))
    saved = accumulator.detailed_snapshot()
    final = beta_frame("completed", [reasoning("authoritative")], 2)
    other = deepcopy(final)
    if mismatch == "lane":
        other["stream_id"] = "other"
    else:
        other["response"]["id"] = "other-response"
    with pytest.raises(ValueError, match="another"):
        accumulator.add_event(model_parse(BetaResponseWsCompleted, other))
    assert accumulator.detailed_snapshot() == saved
    with pytest.raises(RuntimeError, match="No terminal"):
        accumulator.get_final_response()
    accumulator.add_event(model_parse(BetaResponseWsCompleted, final))
    assert accumulator.get_final_response().to_dict() == final["response"]
    assert saved["terminal_type"] is None


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_beta_protocol_error_preserves_original_native_event(mode: str) -> None:
    error = {
        "type": "error",
        "stream_id": "beta",
        "error": {"type": "server_error", "message": "synthetic detail", "code": "synthetic"},
        "agent": {"agent_name": "synthetic-agent"},
        "opaque": {"keep": True},
    }
    model_parse(BetaResponseWsError, error)

    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv(timeout=5))["stream_id"] == "beta"
        socket.send(json.dumps(error))

    with script_server(script) as url:
        async with beta_session(mode, url) as driver:
            lane = driver.session.lane("beta")
            await driver.call(lane, "send", BetaResponseCreate(type="response.create"))
            with pytest.raises(ResponsesWebSocketError) as raised:
                await driver.call(lane, "get_final_response")
            assert isinstance(raised.value.event, BetaResponseWsError)
            assert raised.value.event.to_dict() == error
            assert str(raised.value) == "The Responses WebSocket request returned an error event"
