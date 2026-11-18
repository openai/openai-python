from __future__ import annotations

from typing import Iterator
from typing_extensions import override

import pytest

from openai import OpenAI, AsyncOpenAI
from openai.types.beta import AgentSessionIdleEvent, AgentSessionErrorEvent
from tests.lib.streaming.agents.test_results import ResultServer
from tests.lib.streaming.agents.test_streams import EventBody, sdk as sdk, session


@pytest.fixture
def server() -> ResultServer:
    return ResultServer()


class NamedEventBody(EventBody):
    @override
    def __iter__(self) -> Iterator[bytes]:
        for chunk, event in zip(super().__iter__(), self.events, strict=True):
            yield f"event: {event['type']}\n".encode() + chunk


@pytest.mark.parametrize("creation", [False, True])
@pytest.mark.parametrize("named", [False, True])
async def test_typed_error_on_agents_entrypoints(
    sdk: OpenAI | AsyncOpenAI,
    server: ResultServer,
    creation: bool,
    named: bool,
) -> None:
    sdk._strict_response_validation = False
    error_payload = {
        "type": "server_error",
        "code": "internal_error",
        "message": "Synthetic domain failure",
        "param": "input",
    }
    events: list[dict[str, object]] = [
        {"type": "error", "session_id": "session_test", "error": error_payload},
        {"type": "agent.session.future_state", "session": {"id": "session_test"}},
        {"type": "agent.session.idle", "session": session("idle")},
    ]
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
    assert [event.type for event in received] == ["error", "agent.session.future_state", "agent.session.idle"]
    assert [event.event_id for event in received] == [str(index) for index in range(len(events))]
    error = received[0]
    assert isinstance(error, AgentSessionErrorEvent)
    assert error.session_id == "session_test"
    assert error.error.model_dump() == error_payload
    assert isinstance(received[-1], AgentSessionIdleEvent)
    assert received[-1].session.id == "session_test"
    assert received[-1].session.status == "idle"
    assert server.body.read_count == len(events)
    assert server.body.closed
