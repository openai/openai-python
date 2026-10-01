from __future__ import annotations

from typing import Any
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.lib.beta.agents import AgentTurnResult, AgentTurnResultError
from openai.lib.streaming.agents._types import ToolHandler
from tests.lib.streaming.agents.test_results import message
from tests.lib.streaming.agents.test_streams import Server, EventBody, sdk as sdk, call, idle, session, turn_event


def turn(status: str = "in_progress", turn_id: str = "turn_root", subagent_id: str | None = None) -> dict[str, Any]:
    value = turn_event("created", turn_id, subagent_id=subagent_id)["turn"]
    assert isinstance(value, dict)
    return {**value, "status": status}


class AttachmentServer(Server):
    def __init__(self) -> None:
        super().__init__()
        self.status = "in_progress"
        self.turns: list[dict[str, Any]] = [turn()]
        self.after_status: str | None = None
        self.reads = 0
        self.items: list[dict[str, Any]] = [message("earlier")["item"], message("later", item_id="later")["item"]]
        self.body = EventBody([call(), turn_event("completed"), idle()])
        self.stale_required_actions = False

    @override
    def handle(self, request: httpx2.Request) -> httpx2.Response:
        path = request.url.path
        if request.method == "GET" and not path.endswith("/events"):
            self.requests.append(request)
            if path.endswith("/turns"):
                after = request.url.params.get("after")
                # One item per page exercises existing automatic pagination.
                offset = next((i + 1 for i, item in enumerate(self.turns) if item["id"] == after), 0)
                data = self.turns[offset : offset + 1]
                return httpx2.Response(
                    200, json={"data": data, "has_more": offset + 1 < len(self.turns), "object": "list"}
                )
            if "/turns/" in path:
                turn_id = path.rsplit("/", 1)[-1]
                status = (
                    "completed"
                    if self.after_status == "idle" or self.body.read_count >= len(self.body.events)
                    else "in_progress"
                )
                return httpx2.Response(200, json=turn(status, turn_id, "child" if turn_id == "child_turn" else None))
            if path.endswith("/items"):
                after = request.url.params.get("after")
                offset = next((i + 1 for i, item in enumerate(self.items) if item["id"] == after), 0)
                data = self.items[offset : offset + 1]
                return httpx2.Response(
                    200, json={"data": data, "has_more": offset + 1 < len(self.items), "object": "list"}
                )
            self.reads += 1
            value = session(self.after_status if self.reads > 1 and self.after_status else self.status)
            if self.stale_required_actions:
                value["required_actions"] = [
                    {
                        "type": "function_call",
                        "turn_id": "turn_root",
                        "call_id": "answered",
                        "name": "missing",
                        "arguments": {},
                    }
                ]
            return httpx2.Response(200, json=value)
        return super().handle(request)


@pytest.fixture
def server() -> AttachmentServer:
    return AttachmentServer()


async def attach_result(sdk: OpenAI | AsyncOpenAI, handlers: dict[str, ToolHandler] | None = None) -> AgentTurnResult:
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream("session_test", tool_handlers=handlers) as stream:
            result = await stream.get_final_result()
            assert await stream.get_final_result() is result
            return result
    with sdk.beta.agents.sessions.stream("session_test", tool_handlers=handlers) as stream:
        result = stream.get_final_result()
        assert stream.get_final_result() is result
        return result


async def test_attach_dispatches_pending_once_and_recovers_paginated_output(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.turns.insert(0, turn(subagent_id="child", turn_id="child_turn"))
    server.body = EventBody([call(), call(), message("later", item_id="later"), turn_event("completed"), idle()])
    server.items.insert(1, {**message("user", item_id="user")["item"], "role": "user"})
    server.items.insert(2, message("child", item_id="child", turn_id="child_turn")["item"])
    server.items.insert(3, message("commentary", item_id="commentary", phase="commentary")["item"])
    calls: list[object] = []
    result = await attach_result(sdk, {"search": lambda args: calls.append(args) or "found"})
    assert calls == [{"query": "test"}]
    assert result.output_text == "earlierlater"
    assert len(server.inputs()) == 1
    assert server.inputs()[0]["type"] == "agent.session.input.tool_result"
    assert len([r for r in server.requests if r.url.path.endswith("/items")]) == len(server.items)
    assert server.body.closed


async def test_pending_call_can_identify_root_without_turn_created(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.turns = []
    seen: list[object] = []
    result = await attach_result(sdk, {"search": lambda args: seen.append(args) or "found"})
    assert result.turn_id == "turn_root"
    assert len(seen) == 1


async def test_completion_between_initial_read_and_subscription(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.after_status = "idle"
    server.body = EventBody([])
    result = await attach_result(sdk)
    assert result.output_text == "earlierlater"
    assert server.body.read_count == 0
    assert not server.inputs()


async def test_idle_without_selected_turn_settles_and_has_no_result(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.status = "idle"
    server.turns = [turn("completed", "old_turn")]
    server.body = EventBody([])
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream("session_test") as stream:
            await stream.until_done()
            with pytest.raises(AgentTurnResultError, match="incomplete"):
                await stream.get_final_result()
    else:
        with sdk.beta.agents.sessions.stream("session_test") as stream:
            stream.until_done()
            with pytest.raises(AgentTurnResultError, match="incomplete"):
                stream.get_final_result()
    assert not server.inputs()
    assert not any(r.url.path.endswith(("/turns", "/items")) for r in server.requests)


async def test_answered_call_not_executed_from_stale_session_snapshot(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.stale_required_actions = True
    server.body = EventBody([turn_event("completed"), idle()])
    result = await attach_result(sdk)
    assert result.turn_id == "turn_root"
    assert not server.inputs()


async def test_unhandled_recovered_call_is_reported(sdk: OpenAI | AsyncOpenAI, server: AttachmentServer) -> None:
    with pytest.raises(AgentTurnResultError) as caught:
        await attach_result(sdk)
    assert caught.value.reason == "requires_action"
    action = caught.value.required_actions[0]
    assert action.type == "function_call"
    assert action.call_id == "call_test"
    assert not server.inputs()
    assert server.body.closed


async def test_raw_attach_does_not_fetch_or_retain_result_messages(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    handlers: dict[str, ToolHandler] = {"search": lambda _args: "found"}
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream("session_test", tool_handlers=handlers) as stream:
            await stream.until_done()
            assert stream._collection.collector is None
    else:
        with sdk.beta.agents.sessions.stream("session_test", tool_handlers=handlers) as stream:
            stream.until_done()
            assert stream._collection.collector is None
    assert not any(r.url.path.endswith("/items") for r in server.requests)


async def test_full_terminal_event_selects_root(sdk: OpenAI | AsyncOpenAI, server: AttachmentServer) -> None:
    server.turns = []
    server.body = EventBody(
        [turn_event("completed", "child_turn", subagent_id="child"), turn_event("completed"), idle()]
    )
    result = await attach_result(sdk)
    assert result.turn_id == "turn_root"


async def test_attach_handler_failure_submits_generic_result(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    def handler(_args: object) -> str:
        raise ValueError("SYNTHETIC_HANDLER_SECRET")

    result = await attach_result(sdk, {"search": handler})
    assert result.turn_id == "turn_root"
    assert len(server.inputs()) == 1
    assert "SYNTHETIC_HANDLER_SECRET" not in str(server.inputs())


async def test_attach_tool_submission_failure_preserves_cause(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.reject_input = True
    with pytest.raises(AgentTurnResultError) as caught:
        await attach_result(sdk, {"search": lambda _args: "found"})
    assert caught.value.reason == "observation_failed"
    assert caught.value.__cause__ is not None
    assert server.body.closed


async def test_reattach_again_after_losing_observation(sdk: OpenAI | AsyncOpenAI, server: AttachmentServer) -> None:
    server.body = EventBody([call()])
    seen: list[object] = []
    with pytest.raises(AgentTurnResultError, match="observation_failed"):
        await attach_result(sdk, {"search": lambda args: seen.append(args) or "found"})
    # A subsequent attachment receives only calls still awaiting an answer.
    server.body = EventBody([turn_event("completed"), idle()])
    result = await attach_result(sdk, {"search": lambda args: seen.append(args) or "found"})
    assert result.output_text == "earlierlater"
    assert len(seen) == 1
    assert len(server.inputs()) == 1
