from __future__ import annotations

from typing import Iterator
from typing_extensions import override

import pytest

from openai import OpenAI, AsyncOpenAI
from openai.types.beta import AgentSessionErrorEvent
from openai.lib.beta.agents import AgentTurnResultError
from tests.lib.streaming.agents.test_results import ResultServer, collect, message, creation as creation
from tests.lib.streaming.agents.test_streams import EventBody, sdk as sdk, session, turn_event


@pytest.fixture
def server() -> ResultServer:
    return ResultServer()


@pytest.fixture(autouse=True)
def private_wire_events(sdk: OpenAI | AsyncOpenAI) -> None:
    # Match default client behavior for private frames outside the public union.
    sdk._strict_response_validation = False


def budget(session_id: str = "session_test") -> dict[str, object]:
    resource = session("budget_reached")
    resource["id"] = session_id
    return {"type": "agent.session.budget_reached", "session": resource}


class NamedEventBody(EventBody):
    @override
    def __iter__(self) -> Iterator[bytes]:
        for chunk, event in zip(super().__iter__(), self.events, strict=True):
            yield f"event: {event['type']}\n".encode() + chunk


@pytest.mark.parametrize("creation", [False, True])
@pytest.mark.parametrize("named", [False, True])
@pytest.mark.parametrize("preceding_error", [False, True])
async def test_private_budget_on_agents_entrypoints(
    sdk: OpenAI | AsyncOpenAI,
    server: ResultServer,
    creation: bool,
    named: bool,
    preceding_error: bool,
) -> None:
    error_payload = {
        "type": "server_error",
        "code": "internal_error",
        "message": "Synthetic domain failure",
        "param": "input",
    }
    events: list[dict[str, object]] = []
    if preceding_error:
        events.append({"type": "error", "session_id": "session_test", "error": error_payload})
    resource = session("budget_reached")
    events.append({"type": "agent.session.budget_reached", "session": resource})
    server.body = (NamedEventBody if named else EventBody)(events)
    if isinstance(sdk, AsyncOpenAI):
        stream = (
            await sdk.beta.agents.sessions.create(
                agent={"model": "test-model"}, environment={"type": "none"}, input="Question", stream=True
            )
            if creation
            else await sdk.beta.agents.sessions.events.stream("session_test")
        )
        async with stream:
            received = [event async for event in stream]
    else:
        stream = (
            sdk.beta.agents.sessions.create(
                agent={"model": "test-model"}, environment={"type": "none"}, input="Question", stream=True
            )
            if creation
            else sdk.beta.agents.sessions.events.stream("session_test")
        )
        with stream:
            received = list(stream)
    assert [event.type for event in received] == (["error"] if preceding_error else []) + [
        "agent.session.budget_reached"
    ]
    assert [event.event_id for event in received] == [str(index) for index in range(len(events))]
    if preceding_error:
        error = received[0]
        assert isinstance(error, AgentSessionErrorEvent)
        assert error.session_id == "session_test"
        assert error.error.model_dump() == error_payload
    snapshot = getattr(received[-1], "session", None)
    assert snapshot is not None
    assert (snapshot["id"] if isinstance(snapshot, dict) else snapshot.id) == "session_test"
    assert server.body.read_count == len(events)
    assert server.body.closed


@pytest.mark.parametrize("status", ["completed", "failed", "cancelled"])
async def test_budget_boundary_preserves_turn_outcome(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool, status: str
) -> None:
    events: list[dict[str, object]] = [turn_event("created"), message(), turn_event(status), budget()]
    if status == "completed":
        events.append({"type": "agent.session.failed", "session": session("failed")})
    server.body = EventBody(events)
    if status == "completed":
        result = await collect(sdk, creation)
        assert result.output_text == "answer"
        assert result.turn.status == "completed"
    else:
        with pytest.raises(AgentTurnResultError) as exc:
            await collect(sdk, creation, mode="iterate")
        assert exc.value.reason == status
    assert server.body.read_count == 4
    assert server.body.closed


async def test_budget_for_other_session_does_not_end_result_collection(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool
) -> None:
    server.body = EventBody(
        [
            turn_event("created"),
            message(),
            turn_event("completed"),
            budget("session_other"),
            budget(),
            {"type": "agent.session.failed", "session": session("failed")},
        ]
    )
    result = await collect(sdk, creation)
    assert result.output_text == "answer"
    assert result.session_id == "session_test"
    assert server.body.read_count == 5
    assert server.body.closed


async def test_budget_snapshot_before_turn_outcome_keeps_collecting(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool
) -> None:
    server.body = EventBody([turn_event("created"), budget(), message(), turn_event("completed"), budget()])
    result = await collect(sdk, creation)
    assert result.output_text == "answer"
    assert result.turn.status == "completed"
    assert server.body.read_count == 5
    assert server.body.closed


@pytest.mark.parametrize("session_created", [False, True])
async def test_budget_before_root_turn_stops_result_collection(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool, session_created: bool
) -> None:
    events: list[dict[str, object]] = []
    if session_created:
        events.append({"type": "agent.session.created", "session": session()})
    if session_created or not creation:
        events.append(budget("session_other"))
    events.extend(
        [
            {
                "type": "error",
                "session_id": "session_test",
                "error": {"type": "server_error", "message": "Budget exceeded"},
            },
            budget(),
            {"type": "agent.session.failed", "session": session("failed")},
        ]
    )
    server.body = EventBody(events)
    with pytest.raises(AgentTurnResultError) as exc:
        await collect(sdk, creation)
    assert exc.value.reason == "incomplete"
    assert exc.value.session_id == "session_test"
    assert exc.value.turn is None
    assert server.body.read_count == len(events) - 1
    assert server.body.closed


@pytest.mark.parametrize("snapshot", [None, {}, {"id": None}, {"id": ""}, {"id": 123}])
async def test_malformed_private_budget_snapshot_is_not_a_boundary(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool, snapshot: object
) -> None:
    server.body = EventBody(
        [
            {"type": "agent.session.budget_reached", "session": snapshot},
            {"type": "agent.session.failed", "session": session("failed")},
        ]
    )
    with pytest.raises(AgentTurnResultError) as exc:
        await collect(sdk, creation)
    assert exc.value.reason == "failed"
    assert exc.value.session_id == "session_test"
    assert server.body.read_count == 2
    assert server.body.closed
