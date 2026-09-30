from __future__ import annotations

from typing import Any, Iterator, cast
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.lib.beta.agents import AgentTurnResult, AgentTurnResultError
from openai.lib.streaming.agents import AgentSessionStream, AsyncAgentSessionStream
from tests.lib.streaming.agents.test_streams import Server, EventBody, sdk as sdk, call, idle, session, turn_event


class ResultServer(Server):
    @override
    def handle(self, request: httpx2.Request) -> httpx2.Response:
        if request.method == "POST" and request.url.path.endswith("/sessions"):
            self.requests.append(request)
            return httpx2.Response(200, headers={"content-type": "text/event-stream"}, stream=self.body)
        return super().handle(request)


@pytest.fixture
def server() -> ResultServer:
    return ResultServer()


@pytest.fixture(params=[False, True], ids=["followup", "creation"])
def creation(request: pytest.FixtureRequest) -> bool:
    return bool(request.param)


def message(
    text: str = "answer",
    *,
    item_id: str = "message_a",
    index: int = 0,
    turn_id: str = "turn_root",
    phase: str | None = "final_answer",
    kind: str = "done",
) -> dict[str, Any]:
    return {
        "type": f"agent.session.turn.item.{kind}",
        "session_id": "session_test",
        "turn_id": turn_id,
        "output_index": index,
        "item": {
            "id": item_id,
            "turn_id": turn_id,
            "type": "message",
            "role": "assistant",
            "phase": phase,
            "status": "completed" if kind == "done" else "in_progress",
            "content": [{"type": "output_text", "text": text, "annotations": []}],
        },
    }


async def collect(sdk: OpenAI | AsyncOpenAI, creation: bool, *, mode: str = "getter", **kwargs: Any) -> AgentTurnResult:
    if isinstance(sdk, AsyncOpenAI):
        async_stream = (
            (
                await sdk.beta.agents.sessions.create(
                    agent={"model": "test-model"}, environment={"type": "none"}, input="Question", stream=True
                )
            )
            if creation
            else sdk.beta.agents.sessions.stream("session_test", input="Question", **kwargs)
        )
        async with async_stream:
            if mode != "getter":
                async_stream.with_result_collection()
            if mode == "iterate":
                async for _ in async_stream:
                    pass
            elif mode == "resume":
                async for event in async_stream:
                    if event.type in ("agent.session.in_progress", "agent.session.turn.completed"):
                        break
            elif mode == "drain":
                assert isinstance(async_stream, AsyncAgentSessionStream)
                await async_stream.until_done()
            result = await async_stream.get_final_result()
            assert await async_stream.get_final_result() is result
            return result
    stream = (
        sdk.beta.agents.sessions.create(
            agent={"model": "test-model"}, environment={"type": "none"}, input="Question", stream=True
        )
        if creation
        else sdk.beta.agents.sessions.stream("session_test", input="Question", **kwargs)
    )
    with stream:
        if mode != "getter":
            stream.with_result_collection()
        if mode == "iterate":
            for _ in stream:
                pass
        elif mode == "resume":
            for event in stream:
                if event.type in ("agent.session.in_progress", "agent.session.turn.completed"):
                    break
        elif mode == "drain":
            assert isinstance(stream, AgentSessionStream)
            stream.until_done()
        result = stream.get_final_result()
        assert stream.get_final_result() is result
        return result


@pytest.mark.parametrize("mode", ["getter", "iterate", "drain"])
async def test_result_selects_ordered_final_messages(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool, mode: str
) -> None:
    if creation and mode == "drain":
        pytest.skip("Only the existing follow-up helper exposes until_done")
    server.body = EventBody(
        [
            idle(),
            turn_event("created"),
            message("unfinished", kind="added"),
            message("ignored commentary", item_id="commentary", phase="commentary"),
            turn_event("created", "child", subagent_id="child_agent"),
            message("ignored child", item_id="child_answer", turn_id="child"),
            turn_event("completed", "child", subagent_id="child_agent"),
            message("second", item_id="message_b", index=2),
            message("first", index=1),
            message("first", index=1),
            turn_event("completed"),
            idle(),
        ]
    )
    result = await collect(sdk, creation, mode=mode)
    assert result.session_id == "session_test"
    assert result.turn_id == "turn_root"
    assert result.turn.status == "completed"
    assert result.output_text == "firstsecond"
    assert [m.id for m in result.messages] == ["message_a", "message_b"]
    assert result.messages[0].content[0].type == "output_text"
    assert server.body.closed


async def test_empty_success(sdk: OpenAI | AsyncOpenAI, creation: bool) -> None:
    result = await collect(sdk, creation)
    assert result.output_text == ""
    assert result.messages == []


@pytest.mark.parametrize("status", ["failed", "cancelled"])
async def test_unsuccessful_turn(sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool, status: str) -> None:
    server.body = EventBody([turn_event("created"), message(), turn_event(status), idle()])
    with pytest.raises(AgentTurnResultError) as exc:
        await collect(sdk, creation)
    assert exc.value.reason == status
    assert exc.value.turn_id == "turn_root"
    assert exc.value.messages[0].output_text == "answer"
    assert server.body.closed


@pytest.mark.parametrize("tail", [[], [turn_event("completed")]])
async def test_incomplete_answer(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool, tail: list[dict[str, Any]]
) -> None:
    server.body = EventBody([turn_event("created"), *tail])
    with pytest.raises(AgentTurnResultError) as exc:
        await collect(sdk, creation)
    assert exc.value.reason in ("incomplete", "observation_failed")
    assert exc.value.turn_id == "turn_root"


async def test_legacy_null_phase_is_collected(sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool) -> None:
    server.body = EventBody([turn_event("created"), message(phase=None), turn_event("completed"), idle()])
    result = await collect(sdk, creation)
    assert result.output_text == "answer"
    assert result.messages[0].phase is None


async def test_unhandled_action(sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool) -> None:
    state = session("requires_action")
    state["required_actions"] = [
        {
            "type": "function_call",
            "turn_id": "turn_root",
            "name": "search",
            "call_id": "call_test",
            "arguments": {"query": "test"},
        }
    ]
    server.body = EventBody(
        [turn_event("created"), call(), {"type": "agent.session.requires_action", "session": state}]
    )
    with pytest.raises(AgentTurnResultError) as exc:
        await collect(sdk, creation)
    assert exc.value.reason == "requires_action"
    assert exc.value.required_actions[0].type == "function_call"
    assert server.body.closed


async def test_getter_dispatches_existing_handler_once(sdk: OpenAI | AsyncOpenAI, server: ResultServer) -> None:
    seen: list[object] = []

    def handler(arguments: object) -> str:
        seen.append(arguments)
        return "found"

    server.body = EventBody([turn_event("created"), call(), message(), turn_event("completed"), idle()])
    result = await collect(sdk, False, tool_handlers={"search": handler})
    assert result.output_text == "answer"
    assert seen == [{"query": "test"}]
    assert len(server.inputs()) == 2


async def test_explicit_close_is_not_success(sdk: OpenAI | AsyncOpenAI, creation: bool) -> None:
    if isinstance(sdk, AsyncOpenAI):
        async_stream = (
            await sdk.beta.agents.sessions.create(
                agent={"model": "test-model"}, environment={"type": "none"}, input="Question", stream=True
            )
            if creation
            else sdk.beta.agents.sessions.stream("session_test", input="Question")
        )
        async with async_stream:
            await async_stream.close()
            with pytest.raises(AgentTurnResultError):
                await async_stream.get_final_result()
    else:
        stream = (
            sdk.beta.agents.sessions.create(
                agent={"model": "test-model"}, environment={"type": "none"}, input="Question", stream=True
            )
            if creation
            else sdk.beta.agents.sessions.stream("session_test", input="Question")
        )
        with stream:
            stream.close()
            with pytest.raises(AgentTurnResultError):
                stream.get_final_result()


class BrokenBody(EventBody):
    @override
    def __iter__(self) -> Iterator[bytes]:
        yield from super().__iter__()
        raise httpx2.ReadError("synthetic interrupted connection")


async def test_transport_error_retains_partial_answer(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool
) -> None:
    server.body = BrokenBody([turn_event("created"), message()])
    with pytest.raises(AgentTurnResultError) as exc:
        await collect(sdk, creation)
    assert exc.value.reason == "observation_failed"
    assert exc.value.__cause__ is not None
    assert exc.value.turn is not None and exc.value.turn.status == "in_progress"
    assert exc.value.messages[0].output_text == "answer"


async def test_result_stops_at_first_turn_boundary(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool
) -> None:
    server.body = EventBody(
        [
            turn_event("created"),
            message(),
            turn_event("completed"),
            idle(),
            turn_event("created", "later"),
            message("later answer", turn_id="later"),
        ]
    )
    result = await collect(sdk, creation)
    assert result.output_text == "answer"
    assert server.body.read_count == 4


async def test_late_added_snapshot_does_not_reopen_completed_message(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool
) -> None:
    server.body = EventBody(
        [turn_event("created"), message(), message("stale", kind="added", phase=None), turn_event("completed"), idle()]
    )
    result = await collect(sdk, creation)
    assert result.output_text == "answer"


async def test_later_stream_error_does_not_poison_completed_result(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer
) -> None:
    from openai import APIConnectionError

    server.body = BrokenBody(
        [
            turn_event("created"),
            message(),
            turn_event("completed"),
            idle(),
            turn_event("created", "later"),
            turn_event("failed", "later"),
        ]
    )
    if isinstance(sdk, AsyncOpenAI):
        async with await sdk.beta.agents.sessions.create(
            agent={"model": "test-model"}, environment={"type": "none"}, input="Question", stream=True
        ) as async_stream:
            async_stream.with_result_collection()
            with pytest.raises(APIConnectionError):
                async for _ in async_stream:
                    pass
            result = await async_stream.get_final_result()
    else:
        with sdk.beta.agents.sessions.create(
            agent={"model": "test-model"}, environment={"type": "none"}, input="Question", stream=True
        ) as stream:
            stream.with_result_collection()
            with pytest.raises(APIConnectionError):
                for _ in stream:
                    pass
            result = stream.get_final_result()
    assert result.turn_id == "turn_root"
    assert result.output_text == "answer"


@pytest.mark.parametrize("initial_phase", [None, "final_answer"])
async def test_completed_commentary_is_excluded(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool, initial_phase: str | None
) -> None:
    server.body = EventBody(
        [
            turn_event("created"),
            message(kind="added", phase=initial_phase),
            message(phase="commentary"),
            turn_event("completed"),
            idle(),
        ]
    )
    result = await collect(sdk, creation)
    assert result.messages == []
    assert result.output_text == ""


def test_collector_transfers_messages_into_cached_result() -> None:
    from openai._models import construct_type
    from openai.lib.beta.agents._result import AgentTurnResultCollector
    from openai.types.beta.agent_session_event import AgentSessionEvent

    collector = AgentTurnResultCollector()
    for index, data in enumerate([turn_event("created"), message(), turn_event("completed"), idle()]):
        collector.accept(
            cast(AgentSessionEvent, construct_type(type_=AgentSessionEvent, value={"event_id": str(index), **data}))
        )
    original_message = collector.messages()[0]
    result = collector.result()
    assert result.messages[0] is original_message
    assert collector.messages() == []  # The stream no longer retains a duplicate message collection.
    assert collector.result() is result
    assert result.output_text == "answer"


@pytest.mark.parametrize(
    "phase,turn_id,expected",
    [("final_answer", "turn_root", "answer"), ("commentary", "turn_root", ""), ("final_answer", "child", "")],
)
async def test_only_completed_message_snapshots_supply_text(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool, phase: str, turn_id: str, expected: str
) -> None:
    text_event: dict[str, object] = {
        "type": "agent.session.turn.output_text.delta",
        "session_id": "session_test",
        "turn_id": None,
        "item_id": "message_a",
        "output_index": 0,
        "content_index": 0,
        "delta": "answer",
    }
    server.body = EventBody(
        [
            turn_event("created"),
            text_event,
            message(phase=phase, turn_id=turn_id),
            {**text_event, "event_id": "late-text"},
            turn_event("completed"),
            idle(),
        ]
    )
    result = await collect(sdk, creation)
    assert result.output_text == expected


def test_error_transfers_partial_payloads_and_is_cached() -> None:
    from openai._models import construct_type
    from openai.lib.beta.agents._result import AgentTurnResultCollector
    from openai.types.beta.agent_session_event import AgentSessionEvent

    state = session("requires_action")
    state["required_actions"] = [
        {
            "type": "function_call",
            "turn_id": "turn_root",
            "name": "search",
            "call_id": "call_test",
            "arguments": {"query": "test"},
        }
    ]
    collector = AgentTurnResultCollector()
    for index, data in enumerate(
        [turn_event("created"), message(), {"type": "agent.session.requires_action", "session": state}]
    ):
        collector.accept(
            cast(AgentSessionEvent, construct_type(type_=AgentSessionEvent, value={"event_id": str(index), **data}))
        )
    original_message = collector.messages()[0]
    original_actions = collector.required_actions
    original_turn = collector.turn
    with pytest.raises(AgentTurnResultError) as exc:
        collector.check_outcome()
    error = exc.value
    assert error.messages[0] is original_message
    assert error.required_actions is original_actions
    assert error.turn is original_turn
    assert collector.turn is None and collector.messages() == [] and collector.required_actions == []
    with pytest.raises(AgentTurnResultError) as repeated:
        collector.result()
    assert repeated.value is error


@pytest.mark.parametrize("resumed", [True, False])
async def test_resolved_action_is_not_reported_again(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool, resumed: bool
) -> None:
    state = session("requires_action")
    state["required_actions"] = [
        {
            "type": "function_call",
            "turn_id": "turn_root",
            "name": "search",
            "call_id": "call_test",
            "arguments": {"query": "test"},
        }
    ]
    events: list[dict[str, object]] = [
        turn_event("created"),
        {"type": "agent.session.requires_action", "session": state},
    ]
    if resumed:
        events.append({"type": "agent.session.in_progress", "session": session("in_progress")})
    events.extend([message(), turn_event("completed"), idle()])
    server.body = EventBody(events)
    result = await collect(sdk, creation, mode="resume")
    assert result.output_text == "answer"


async def test_raw_iteration_does_not_collect_output(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool
) -> None:
    events = [message("x" * 8192, item_id=f"message_{index}", index=index) for index in range(1024)]
    server.body = EventBody([turn_event("created"), *events, turn_event("completed"), idle()])
    if isinstance(sdk, AsyncOpenAI):
        async_stream = (
            await sdk.beta.agents.sessions.create(
                agent={"model": "test-model"}, environment={"type": "none"}, input="Question", stream=True
            )
            if creation
            else sdk.beta.agents.sessions.stream("session_test", input="Question")
        )
        async with async_stream:
            async for _ in async_stream:
                assert async_stream._collection.collector is None
            read_count = server.body.read_count
            with pytest.raises(RuntimeError, match="with_result_collection"):
                await async_stream.get_final_result()
            assert server.body.read_count == read_count
    else:
        stream = (
            sdk.beta.agents.sessions.create(
                agent={"model": "test-model"}, environment={"type": "none"}, input="Question", stream=True
            )
            if creation
            else sdk.beta.agents.sessions.stream("session_test", input="Question")
        )
        with stream:
            for _ in stream:
                assert stream._collection.collector is None
            read_count = server.body.read_count
            with pytest.raises(RuntimeError, match="with_result_collection"):
                stream.get_final_result()
            assert server.body.read_count == read_count


async def test_late_collection_opt_in_does_not_consume_events(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool
) -> None:
    if isinstance(sdk, AsyncOpenAI):
        async_stream = (
            await sdk.beta.agents.sessions.create(
                agent={"model": "test-model"}, environment={"type": "none"}, input="Question", stream=True
            )
            if creation
            else sdk.beta.agents.sessions.stream("session_test", input="Question")
        )
        async with async_stream:
            await async_stream.__anext__()
            with pytest.raises(RuntimeError, match="before consuming events"):
                async_stream.with_result_collection()
            with pytest.raises(RuntimeError, match="before consuming events"):
                await async_stream.get_final_result()
            assert server.body.read_count == 1
    else:
        stream = (
            sdk.beta.agents.sessions.create(
                agent={"model": "test-model"}, environment={"type": "none"}, input="Question", stream=True
            )
            if creation
            else sdk.beta.agents.sessions.stream("session_test", input="Question")
        )
        with stream:
            next(stream)
            with pytest.raises(RuntimeError, match="before consuming events"):
                stream.with_result_collection()
            with pytest.raises(RuntimeError, match="before consuming events"):
                stream.get_final_result()
            assert server.body.read_count == 1
