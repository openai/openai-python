from __future__ import annotations

from typing import Any, Iterator, AsyncIterator
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, APIConnectionError
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
        self.retrieve_status: str | None = None
        self.fail_recovery_read = False
        self.complete_on_rejected_submission = False
        self.after_status: str | None = None
        self.after_turns: list[dict[str, Any]] | None = None
        self.reads = 0
        self.items: list[dict[str, Any]] = [message("earlier")["item"], message("later", item_id="later")["item"]]
        self.body = EventBody([call(), turn_event("completed"), idle()])
        self.stale_required_actions = False
        self.manual_actions: list[dict[str, Any]] = []
        self.null_item_cursor = False
        self.item_cursor_metadata = False
        self.fail_items = False
        self.fail_diagnostic = False
        self.fail_later_items = False
        self.live_turns: list[dict[str, Any]] | None = None
        self.live_after_reads = 1
        self.turn_reads = 0
        self.first_turn_status: str | None = None
        self.manual_after_reads = 0
        self.turn_list_reads = 0
        self.turns_after_list: int | None = None

    @override
    def handle(self, request: httpx2.Request) -> httpx2.Response:
        path = request.url.path
        if request.method == "POST" and self.complete_on_rejected_submission:
            self.retrieve_status = "completed"
        if request.method == "GET" and not path.endswith("/events"):
            self.requests.append(request)
            if path.endswith("/turns"):
                self.turn_list_reads += 1
                if self.turns_after_list is not None and self.turn_list_reads >= self.turns_after_list:
                    self.turns = [turn("waiting")]
                if self.body.read_count >= self.live_after_reads and self.live_turns is not None:
                    self.turns = self.live_turns
                after = request.url.params.get("after")
                # One item per page exercises existing automatic pagination.
                offset = next((i + 1 for i, item in enumerate(self.turns) if item["id"] == after), 0)
                data = self.turns[offset : offset + 1]
                return httpx2.Response(
                    200, json={"data": data, "has_more": offset + 1 < len(self.turns), "object": "list"}
                )
            if "/turns/" in path:
                self.turn_reads += 1
                turn_id = path.rsplit("/", 1)[-1]
                if self.fail_recovery_read and self.body.read_count:
                    raise httpx2.ConnectError("Synthetic durable read failure", request=request)
                status = (
                    "completed"
                    if self.after_status == "idle"
                    or any(
                        event.get("type") == "agent.session.turn.completed" and event.get("turn_id") == turn_id
                        for event in self.body.events[: self.body.read_count]
                    )
                    else "in_progress"
                )
                return httpx2.Response(
                    200,
                    json=turn(
                        "completed"
                        if turn_id == "old_turn"
                        else (
                            self.first_turn_status
                            if self.turn_reads == 1 and self.first_turn_status
                            else self.retrieve_status or status
                        ),
                        turn_id,
                        "child" if turn_id == "child_turn" else None,
                    ),
                )
            if path.endswith("/items"):
                if self.fail_items or self.fail_later_items and request.url.params.get("after"):
                    return httpx2.Response(500, json={"error": {"message": "Synthetic read failure"}})
                after = request.url.params.get("after")
                offset = next((i + 1 for i, item in enumerate(self.items) if item["id"] == after), 0)
                data = self.items[offset : offset + 1]
                payload: dict[str, Any] = {"data": data, "has_more": offset + 1 < len(self.items), "object": "list"}
                if self.item_cursor_metadata and data:
                    payload["last_id"] = data[-1]["id"]
                if self.null_item_cursor and data:
                    payload["data"] = [{**data[0], "id": None}]
                return httpx2.Response(200, json=payload)
            self.reads += 1
            if self.fail_diagnostic and self.reads > 1:
                raise httpx2.ConnectError("Synthetic diagnostic failure", request=request)
            if self.after_turns is not None:
                self.turns = self.after_turns
            pending = self.body.read_count >= self.manual_after_reads
            value = session((self.after_status or self.status) if pending else "in_progress")
            value["required_actions"] = self.manual_actions if pending else []
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
    server.live_turns = [turn()]
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
    assert not any(r.url.path.endswith("/items") for r in server.requests)


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
    assert "".join(item.output_text for item in caught.value.messages) == "earlierlater"
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


@pytest.mark.parametrize("old_root", [False, True])
async def test_new_root_completes_before_attachment_refresh(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer, old_root: bool
) -> None:
    server.turns = [turn("completed", "old_turn")] if old_root else []
    server.after_status = "idle"
    server.after_turns = [turn("completed")]
    server.body = EventBody([turn_event("completed"), idle()])
    result = await attach_result(sdk)
    assert result.turn_id == "turn_root"
    assert result.output_text == "earlierlater"
    assert server.body.read_count == 0


async def test_unchanged_old_completed_root_is_not_selected(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.turns = [turn("completed", "old_turn")]
    server.after_status = "idle"
    server.body = EventBody([])
    with pytest.raises(AgentTurnResultError, match="incomplete"):
        await attach_result(sdk)
    assert not any(request.url.path.endswith("/items") for request in server.requests)


async def test_terminal_selected_turn_settles_while_successor_is_active(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.retrieve_status = "completed"
    server.body = EventBody([call(call_id="successor_call")])
    result = await attach_result(sdk)
    assert result.turn_id == "turn_root"
    assert result.output_text == "earlierlater"
    assert server.body.read_count == 0
    assert not server.inputs()


async def test_selected_terminal_event_stops_before_successor_calls(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.body = EventBody([turn_event("completed"), call(call_id="successor_call"), idle()])
    result = await attach_result(sdk)
    assert result.turn_id == "turn_root"
    assert server.body.read_count == 1
    assert not server.inputs()


async def test_unhandled_replay_stops_without_waiting_for_batch_end(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    missing: Any = call(call_id="missing")
    missing["item"]["name"] = "unregistered"
    server.body = EventBody([missing, call(), turn_event("completed"), idle()])
    handled: list[object] = []
    with pytest.raises(AgentTurnResultError) as caught:
        await attach_result(sdk, {"search": lambda args: handled.append(args) or "found"})
    assert caught.value.reason == "requires_action"
    action = caught.value.required_actions[0]
    assert action.type == "function_call"
    assert action.call_id == "missing"
    assert server.body.read_count == 1
    assert not handled
    assert server.body.closed


async def test_new_root_finishes_between_idle_baseline_and_refresh(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.status = "idle"
    server.turns = [turn("completed", "old_turn")]
    server.after_turns = [turn("completed")]
    server.after_status = "idle"
    server.body = EventBody([])
    result = await attach_result(sdk)
    assert result.turn_id == "turn_root"
    assert result.output_text == "earlierlater"


class InterruptedBody(EventBody):
    def __init__(self, server: AttachmentServer, status: str) -> None:
        super().__init__([message("partial", item_id="observed_partial")])
        self.server = server
        self.status = status

    @override
    def __iter__(self) -> Iterator[bytes]:
        yield from super().__iter__()
        self.server.retrieve_status = self.status
        raise httpx2.ReadError("Synthetic observation disconnect")

    @override
    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in self:
            yield chunk


@pytest.mark.parametrize("terminal", ["completed", "failed"])
async def test_interrupted_observation_reconciles_exact_selected_turn(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer, terminal: str
) -> None:
    server.body = InterruptedBody(server, terminal)
    if terminal == "failed":
        with pytest.raises(AgentTurnResultError) as caught:
            await attach_result(sdk)
        assert caught.value.reason == "failed"
        assert caught.value.messages
    else:
        result = await attach_result(sdk)
        assert result.output_text == "earlierlaterpartial"
    assert len([r for r in server.requests if "/turns/" in r.url.path]) == 2
    assert server.body.closed


@pytest.mark.parametrize("read_fails", [False, True])
async def test_inconclusive_reconciliation_preserves_observation_cause(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer, read_fails: bool
) -> None:
    server.body = InterruptedBody(server, "in_progress")
    server.fail_recovery_read = read_fails
    with pytest.raises(AgentTurnResultError) as caught:
        await attach_result(sdk)
    assert caught.value.reason == "observation_failed"
    cause = caught.value.__cause__
    assert isinstance(cause, APIConnectionError)
    assert isinstance(cause.__cause__, httpx2.ReadError)
    assert str(cause.__cause__) == "Synthetic observation disconnect"
    if not read_fails:
        assert "".join(item.output_text for item in caught.value.messages) == "earlierlaterpartial"
    assert len([r for r in server.requests if "/turns/" in r.url.path]) == 2


async def test_submission_failure_is_not_hidden_by_completed_durable_turn(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.reject_input = True
    server.complete_on_rejected_submission = True
    with pytest.raises(AgentTurnResultError) as caught:
        await attach_result(sdk, {"search": lambda _args: "found"})
    assert caught.value.reason == "observation_failed"
    assert len([r for r in server.requests if "/turns/" in r.url.path]) == 1
    assert "".join(item.output_text for item in caught.value.messages) == "earlierlater"
    assert caught.value.__cause__ is not None


async def test_collected_progress_can_recover_after_observation_error(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.body = InterruptedBody(server, "completed")
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream("session_test").with_result_collection() as stream:
            with pytest.raises(APIConnectionError):
                async for _ in stream:
                    pass
            result = await stream.get_final_result()
    else:
        with sdk.beta.agents.sessions.stream("session_test").with_result_collection() as stream:
            with pytest.raises(APIConnectionError):
                list(stream)
            result = stream.get_final_result()
    assert result.output_text == "earlierlaterpartial"


@pytest.mark.parametrize("metadata", [False, True])
async def test_legacy_null_item_ids_do_not_truncate_recovered_output(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer, metadata: bool
) -> None:
    server.body = EventBody([turn_event("completed")])
    server.null_item_cursor = True
    server.item_cursor_metadata = metadata
    if metadata:
        result = await attach_result(sdk)
        assert result.output_text == "earlierlater"
    else:
        with pytest.raises(AgentTurnResultError, match="observation_failed") as caught:
            await attach_result(sdk)
        assert "advancing cursor" in str(caught.value.__cause__)


@pytest.mark.parametrize("status", ["failed", "cancelled"])
@pytest.mark.parametrize("read_fails", [False, True])
async def test_bootstrap_terminal_error_recovers_available_partial_output(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer, status: str, read_fails: bool
) -> None:
    server.retrieve_status = status
    server.fail_items = read_fails
    with pytest.raises(AgentTurnResultError) as caught:
        await attach_result(sdk)
    assert caught.value.reason == status
    if not read_fails:
        assert "".join(item.output_text for item in caught.value.messages) == "earlierlater"
    assert server.body.read_count == 0


def manual_action(kind: str, turn_id: str = "turn_root") -> dict[str, Any]:
    if kind == "environment_connection":
        return {"type": kind, "environment_id": "env_test"}
    request: dict[str, Any] = {"type": kind, "reason": "Synthetic approval"}
    if kind == "browser_authentication":
        request.update(fields=[], options=[], credential_origin="https://example.com")
    else:
        request["origin"] = "https://example.com"
    return {
        "type": "computer_use_approval_request",
        "request_id": "request_test",
        "turn_id": turn_id,
        "request": request,
    }


@pytest.mark.parametrize("kind", ["environment_connection", "browser_authentication", "browser_origin_access"])
async def test_current_manual_action_is_diagnostic_without_waiting_for_replay(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer, kind: str
) -> None:
    server.turns = [turn("waiting")]
    server.retrieve_status = "waiting"
    server.status = "requires_action"
    server.manual_actions = [manual_action(kind)]
    server.body = EventBody([])
    with pytest.raises(AgentTurnResultError, match="requires_action") as caught:
        await attach_result(sdk)
    assert caught.value.required_actions[0].type == server.manual_actions[0]["type"]
    assert server.body.read_count == 0
    assert not server.inputs()


@pytest.mark.parametrize("kind", ["environment_connection", "browser_authentication", "browser_origin_access"])
async def test_stale_manual_action_does_not_override_selected_completion(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer, kind: str
) -> None:
    server.status = "requires_action"
    server.retrieve_status = "completed"
    server.manual_actions = [manual_action(kind, "successor")]
    result = await attach_result(sdk)
    assert result.turn_id == "turn_root"
    assert server.body.read_count == 0


async def test_manual_action_from_successor_is_not_selected(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.turns = [turn("waiting")]
    server.after_turns = [turn("waiting", "successor")]
    server.retrieve_status = "waiting"
    server.status = "requires_action"
    server.manual_actions = [manual_action("environment_connection")]
    server.body = EventBody([turn_event("completed")])
    # The selected terminal SSE event remains authoritative even if a subsequent
    # GET fixture still returns the older waiting state.
    result = await attach_result(sdk)
    assert result.turn_id == "turn_root"
    assert result.output_text == "earlierlater"


async def test_terminal_failure_wins_over_partial_recovery_read_failure(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.body = InterruptedBody(server, "failed")
    server.fail_items = True
    with pytest.raises(AgentTurnResultError) as caught:
        await attach_result(sdk)
    assert caught.value.reason == "failed"
    assert caught.value.messages[0].output_text == "partial"


async def test_raw_attachment_does_not_retain_manual_request_payload(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.turns = [turn("waiting")]
    server.retrieve_status = "waiting"
    server.status = "requires_action"
    server.manual_actions = [manual_action("browser_authentication")]
    server.body = EventBody([turn_event("completed")])
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream("session_test") as stream:
            await stream.until_done()
            state = stream._attachment
            assert stream._collection.collector is None
    else:
        with sdk.beta.agents.sessions.stream("session_test") as stream:
            stream.until_done()
            state = stream._attachment
            assert stream._collection.collector is None
    assert state is not None
    assert not any(isinstance(value, (dict, list)) for value in vars(state).values())
    assert server.reads == 1  # No diagnostic refetch for raw iteration.
    assert not any(r.url.path.endswith("/items") for r in server.requests)


@pytest.mark.parametrize("baseline", ["old_turn", "newer_old_turn"])
async def test_historical_browser_request_cannot_select_prior_completed_root(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer, baseline: str
) -> None:
    server.turns = [turn("completed", baseline)]
    server.live_turns = [turn()]
    old_request: Any = call()
    old_request["turn_id"] = "old_turn"
    old_request["event_id"] = "old_request"
    old_request["item"] = {
        "type": "computer_use_approval_request",
        "id": "old_request",
        "turn_id": "old_turn",
        "request_id": "old_request",
        "request": manual_action("browser_authentication", "old_turn")["request"],
    }
    server.body = EventBody([old_request, call(), turn_event("completed")])
    handled: list[object] = []
    result = await attach_result(sdk, {"search": lambda args: handled.append(args) or "found"})
    assert result.turn_id == "turn_root"
    assert result.output_text == "earlierlater"
    assert len(handled) == 1


async def test_preentered_collection_seeds_manual_error_identity(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.turns = [turn("waiting")]
    server.retrieve_status = "waiting"
    server.status = "requires_action"
    server.manual_actions = [manual_action("browser_authentication")]
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream("session_test").with_result_collection() as stream:
            with pytest.raises(AgentTurnResultError) as raw:
                await stream.until_done()
            with pytest.raises(AgentTurnResultError) as final:
                await stream.get_final_result()
    else:
        with sdk.beta.agents.sessions.stream("session_test").with_result_collection() as stream:
            with pytest.raises(AgentTurnResultError) as raw:
                stream.until_done()
            with pytest.raises(AgentTurnResultError) as final:
                stream.get_final_result()
    assert raw.value is final.value
    assert final.value.turn_id == "turn_root"
    assert "".join(item.output_text for item in final.value.messages) == "earlierlater"


@pytest.mark.parametrize("status", ["failed", "cancelled", "in_progress"])
async def test_later_page_failure_preserves_already_recovered_messages(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer, status: str
) -> None:
    server.fail_later_items = True
    server.retrieve_status = status
    if status == "in_progress":
        server.body = InterruptedBody(server, "in_progress")
    with pytest.raises(AgentTurnResultError) as caught:
        await attach_result(sdk)
    assert caught.value.reason == ("observation_failed" if status == "in_progress" else status)
    assert any(item.output_text == "earlier" for item in caught.value.messages)
    if status == "in_progress":
        assert any(item.output_text == "partial" for item in caught.value.messages)


async def test_buffered_idle_does_not_settle_current_active_attachment(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.turns = [turn("completed", "old_turn")]
    server.live_turns = [turn()]
    server.live_after_reads = 2  # The active root is not yet visible at the stale idle frame.
    server.body = EventBody([idle(), call(), turn_event("completed")])
    calls: list[object] = []
    result = await attach_result(sdk, {"search": lambda args: calls.append(args) or "found"})
    assert result.turn_id == "turn_root"
    assert len(calls) == 1


@pytest.mark.parametrize("historical", [False, True])
async def test_environment_connection_without_active_turn_is_reported(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer, historical: bool
) -> None:
    server.turns = [turn("completed", "old_turn")] if historical else []
    server.status = "requires_action"
    server.manual_actions = [manual_action("environment_connection")]
    server.body = EventBody([])
    with pytest.raises(AgentTurnResultError, match="requires_action") as caught:
        await attach_result(sdk)
    assert caught.value.session_id == "session_test"
    assert caught.value.turn_id is None
    assert caught.value.required_actions[0].type == "environment_connection"
    assert server.body.read_count == 0
    assert not any(r.url.path.endswith("/items") for r in server.requests)


@pytest.mark.parametrize("stale_first_lookup", [False, True])
@pytest.mark.parametrize("already_selected", [False, True])
async def test_first_waiting_root_discovered_from_browser_item_checks_manual_action(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer, stale_first_lookup: bool, already_selected: bool
) -> None:
    server.turns = [turn("waiting")] if already_selected else []
    server.retrieve_status = "waiting"
    server.live_turns = [turn("waiting")]
    server.manual_after_reads = 1 if already_selected else 0
    server.status = "requires_action"
    server.manual_actions = [manual_action("browser_authentication")]
    request: Any = call()
    request["turn_id"] = None
    request["item"] = {
        "type": "computer_use_approval_request",
        "id": "request_test",
        "turn_id": "turn_root",
        "request_id": "request_test",
        "request": server.manual_actions[0]["request"],
    }
    server.live_after_reads = 2 if stale_first_lookup and not already_selected else 1
    repeated: dict[str, object] = {**request, "event_id": "second_request_observation"}
    server.body = EventBody([request, repeated] if stale_first_lookup else [request])
    with pytest.raises(AgentTurnResultError, match="requires_action") as caught:
        await attach_result(sdk)
    assert caught.value.turn_id == "turn_root"
    assert caught.value.required_actions[0].type == "computer_use_approval_request"
    assert server.body.read_count == (2 if stale_first_lookup and not already_selected else 1)


async def test_diagnostic_read_failure_retains_durable_partial_messages(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.turns = [turn("waiting")]
    server.retrieve_status = "waiting"
    server.status = "requires_action"
    server.manual_actions = [manual_action("browser_authentication")]
    server.fail_diagnostic = True
    with pytest.raises(AgentTurnResultError, match="observation_failed") as caught:
        await attach_result(sdk)
    assert caught.value.turn_id == "turn_root"
    assert "".join(item.output_text for item in caught.value.messages) == "earlierlater"
    assert isinstance(caught.value.__cause__, APIConnectionError)
    assert server.body.read_count == 0


@pytest.mark.parametrize("status", ["completed", "failed", "cancelled"])
async def test_terminal_event_survives_stale_reconciliation(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer, status: str
) -> None:
    server.retrieve_status = "in_progress"
    server.body = EventBody([turn_event(status)])
    if status == "completed":
        result = await attach_result(sdk)
        assert result.turn.status == "completed"
        assert result.output_text == "earlierlater"
    else:
        with pytest.raises(AgentTurnResultError) as caught:
            await attach_result(sdk)
        assert caught.value.reason == status
        assert caught.value.turn is not None
        assert caught.value.turn.status == status


async def test_idle_handshake_rechecks_selected_turn_after_stale_read(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.after_status = "idle"
    server.first_turn_status = "in_progress"
    server.retrieve_status = "completed"
    server.body = EventBody([])
    result = await attach_result(sdk)
    assert result.turn_id == "turn_root"
    assert result.output_text == "earlierlater"
    assert server.body.read_count == 0


async def test_idle_event_refreshes_exact_selected_turn(sdk: OpenAI | AsyncOpenAI, server: AttachmentServer) -> None:
    server.first_turn_status = "in_progress"
    server.retrieve_status = "completed"
    server.body = EventBody([idle()])
    result = await attach_result(sdk)
    assert result.turn_id == "turn_root"
    assert result.output_text == "earlierlater"
    assert server.body.read_count == 1


async def test_reconciliation_preserves_completed_sse_tail_when_items_read_lags(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.items = [message("earlier")["item"]]
    server.body = EventBody([message("later", item_id="later"), turn_event("completed")])
    result = await attach_result(sdk)
    assert result.output_text == "earlierlater"
    assert len(result.messages) == 2


async def test_unhandled_call_diagnostic_does_not_alias_yielded_arguments(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    event: Any = call()
    event["item"]["arguments"] = {"nested": {"value": "original"}}
    server.body = EventBody([event])
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream("session_test").with_result_collection() as stream:
            observed = await stream.__anext__()
            assert observed.type == "agent.session.turn.item.added" and observed.item.type == "function_call"
            observed.item.arguments["nested"]["value"] = "changed"  # type: ignore[index]
            with pytest.raises(AgentTurnResultError) as caught:
                await stream.get_final_result()
    else:
        with sdk.beta.agents.sessions.stream("session_test").with_result_collection() as stream:
            observed = next(stream)
            assert observed.type == "agent.session.turn.item.added" and observed.item.type == "function_call"
            observed.item.arguments["nested"]["value"] = "changed"  # type: ignore[index]
            with pytest.raises(AgentTurnResultError) as caught:
                stream.get_final_result()
    action = caught.value.required_actions[0]
    assert action.type == "function_call"
    assert action.arguments == {"nested": {"value": "original"}}


async def test_progress_collection_retains_distinct_unhandled_calls(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.body = EventBody([call(call_id="first"), call(call_id="second")])
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream("session_test").with_result_collection() as stream:
            await stream.__anext__()
            await stream.__anext__()
            with pytest.raises(AgentTurnResultError) as caught:
                await stream.get_final_result()
    else:
        with sdk.beta.agents.sessions.stream("session_test").with_result_collection() as stream:
            next(stream)
            next(stream)
            with pytest.raises(AgentTurnResultError) as caught:
                stream.get_final_result()
    assert [action.call_id for action in caught.value.required_actions if action.type == "function_call"] == [
        "first",
        "second",
    ]


async def test_manual_diagnostics_selects_newly_visible_waiting_root(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.turns = []
    server.turns_after_list = 3
    server.status = "requires_action"
    server.manual_actions = [manual_action("environment_connection")]
    server.body = EventBody([])
    with pytest.raises(AgentTurnResultError, match="requires_action") as caught:
        await attach_result(sdk)
    assert caught.value.turn_id == "turn_root"
    assert caught.value.required_actions[0].type == "environment_connection"
    assert server.body.read_count == 0


async def test_error_hydration_preserves_observed_completed_tail(
    sdk: OpenAI | AsyncOpenAI, server: AttachmentServer
) -> None:
    server.items = [message("earlier")["item"]]
    server.body = EventBody([message("later", item_id="later"), call()])
    with pytest.raises(AgentTurnResultError, match="requires_action") as caught:
        await attach_result(sdk)
    assert "".join(item.output_text for item in caught.value.messages) == "earlierlater"
