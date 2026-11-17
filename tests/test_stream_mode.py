from __future__ import annotations

import json
from typing import Any, Dict, Iterator, cast
from typing_extensions import Literal, override

import httpx2
import pytest

from openai import OpenAI, APIError, AsyncOpenAI, APIStatusError, APIConnectionError
from openai._models import FinalRequestOptions
from openai._streaming import Stream, AsyncStream
from openai.types.beta import AgentSessionIdleEvent, AgentSessionErrorEvent
from openai._base_client import make_request_options
from openai.lib.beta.agents import AgentSessionEventStream, AsyncAgentSessionEventStream
from openai.types.beta.agent_session_event import AgentSessionEvent
from tests.lib.streaming.agents.test_results import ResultServer, message
from tests.lib.streaming.agents.test_streams import EventBody, sdk as sdk, idle, turn_event


@pytest.fixture
def server() -> ResultServer:
    return ResultServer()


def domain_error() -> dict[str, object]:
    return {
        "type": "error",
        "event_id": "event_error",
        "session_id": "session_test",
        "error": {"type": "server_error", "code": "server_error", "message": "Synthetic session error."},
    }


class NamedEventBody(EventBody):
    def __init__(self, events: list[dict[str, object]], event_name: str | None = None) -> None:
        super().__init__(events)
        self.event_name = event_name

    @override
    def __iter__(self) -> Iterator[bytes]:
        for chunk, event in zip(super().__iter__(), self.events, strict=True):
            yield f"event: {self.event_name or event['type']}\n".encode() + chunk


@pytest.mark.parametrize("named", [False, True])
@pytest.mark.parametrize("mode", [None, "legacy", "events"])
async def test_domain_error_delivery_mode(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, named: bool, mode: Literal["legacy", "events"] | None
) -> None:
    server.body = (NamedEventBody if named else EventBody)([domain_error(), idle()])
    options = make_request_options(stream_mode=mode)
    received = []
    if isinstance(sdk, AsyncOpenAI):
        stream = await sdk.post(
            "/agents/sessions",
            cast_to=cast(Any, AgentSessionEvent),
            options=options,
            stream=True,
            stream_cls=AsyncStream[AgentSessionEvent],
        )
        if mode == "events":
            received = [event async for event in stream]
        else:
            with pytest.raises(APIError, match="Synthetic session error"):
                await stream.__anext__()
    else:
        stream = sdk.post(
            "/agents/sessions",
            cast_to=cast(Any, AgentSessionEvent),
            options=options,
            stream=True,
            stream_cls=Stream[AgentSessionEvent],
        )
        if mode == "events":
            received = list(stream)
        else:
            with pytest.raises(APIError, match="Synthetic session error"):
                next(stream)
    if mode == "events":
        assert [event.type for event in received] == ["error", "agent.session.idle"]
        assert isinstance(received[0], AgentSessionErrorEvent)
        assert isinstance(received[1], AgentSessionIdleEvent)
        assert received[0].error.message == "Synthetic session error."
        assert received[1].session.status == "idle"
        assert server.body.read_count == 2
    else:
        assert server.body.read_count == 1
    assert server.body.closed


@pytest.mark.parametrize("creation", [False, True])
async def test_agents_entrypoints_deliver_domain_errors(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool
) -> None:
    server.body = NamedEventBody([domain_error(), idle()])
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
    assert [event.type for event in received] == ["error", "agent.session.idle"]
    assert isinstance(received[0], AgentSessionErrorEvent)
    assert isinstance(received[1], AgentSessionIdleEvent)
    assert server.body.closed


async def test_completed_result_survives_domain_error(sdk: OpenAI | AsyncOpenAI, server: ResultServer) -> None:
    server.body = EventBody([turn_event("created"), message(), turn_event("completed"), domain_error(), idle()])
    options = make_request_options(stream_mode="events")
    if isinstance(sdk, AsyncOpenAI):
        stream = await sdk.post(
            "/agents/sessions",
            cast_to=cast(Any, AgentSessionEvent),
            options=options,
            stream=True,
            stream_cls=AsyncAgentSessionEventStream,
        )
        result = await stream.get_final_result()
    else:
        stream = sdk.post(
            "/agents/sessions",
            cast_to=cast(Any, AgentSessionEvent),
            options=options,
            stream=True,
            stream_cls=AgentSessionEventStream,
        )
        result = stream.get_final_result()
    assert result.turn.status == "completed"
    assert result.output_text == "answer"
    assert server.body.read_count == 5
    assert server.body.closed


@pytest.mark.parametrize("synthesize", [False, True])
@pytest.mark.parametrize("event_name", [None, "thread.custom"])
async def test_events_preserve_custom_stream_and_synthesis(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, synthesize: bool, event_name: str | None
) -> None:
    options_seen: list[FinalRequestOptions] = []

    class CustomStream(Stream[Dict[str, object]]):
        def __init__(self, *, options: FinalRequestOptions, **kwargs: Any) -> None:
            options_seen.append(options)
            super().__init__(options=options, **kwargs)

    class CustomAsyncStream(AsyncStream[Dict[str, object]]):
        def __init__(self, *, options: FinalRequestOptions, **kwargs: Any) -> None:
            options_seen.append(options)
            super().__init__(options=options, **kwargs)

    events = [domain_error(), idle()]
    server.body = NamedEventBody(events, event_name=event_name)
    options = make_request_options(stream_mode="events", synthesize_event_and_data=synthesize)
    if isinstance(sdk, AsyncOpenAI):
        stream = await sdk.post(
            "/agents/sessions",
            cast_to=Dict[str, object],
            options=options,
            stream=True,
            stream_cls=CustomAsyncStream,
        )
        assert isinstance(stream, CustomAsyncStream)
        received = [event async for event in stream]
    else:
        stream = sdk.post(
            "/agents/sessions",
            cast_to=Dict[str, object],
            options=options,
            stream=True,
            stream_cls=CustomStream,
        )
        assert isinstance(stream, CustomStream)
        received = list(stream)
    assert len(options_seen) == 1
    assert options_seen[0] is stream._options
    assert options_seen[0].stream_mode == "events"
    data = [{"event_id": str(i), **event} for i, event in enumerate(events)]
    assert received == (
        [{"event": event_name or event["type"], "data": event} for event in data] if synthesize else data
    )
    assert server.body.closed


@pytest.mark.parametrize("failure", ["http", "json", "network"])
async def test_events_preserve_failures(sdk: OpenAI | AsyncOpenAI, server: ResultServer, failure: str) -> None:
    class FailingBody(EventBody):
        @override
        def __iter__(self) -> Iterator[bytes]:
            if failure == "network":
                raise httpx2.ReadError("synthetic interrupted stream")
            yield b"data: invalid-json\n\n"

    server.body = FailingBody([])
    if failure == "http":
        path = "/agents/sessions/session_test"
        # A regular HTTP failure is handled before decoding the stream.
        server.reject_input = True
        body = {"events": [{"type": "agent.session.input.message", "content": []}]}
    else:
        path, body = "/agents/sessions", None
    expected = {"http": APIStatusError, "json": json.JSONDecodeError, "network": APIConnectionError}[failure]
    options = make_request_options(stream_mode="events")
    with pytest.raises(expected):
        if isinstance(sdk, AsyncOpenAI):
            stream = await sdk.post(
                path,
                cast_to=Dict[str, object],
                body=body,
                options=options,
                stream=True,
                stream_cls=AsyncStream[dict[str, object]],
            )
            async for _ in stream:
                pass
        else:
            stream = sdk.post(
                path,
                cast_to=Dict[str, object],
                body=body,
                options=options,
                stream=True,
                stream_cls=Stream[dict[str, object]],
            )
            list(stream)
    if failure != "http":
        assert server.body.closed
