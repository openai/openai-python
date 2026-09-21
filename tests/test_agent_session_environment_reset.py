from __future__ import annotations

import json

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.types.beta import AgentSessionEnvironmentResetEvent


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("strict", [False, True], ids=["loose", "strict"])
@pytest.mark.parametrize(("turn_id", "reset_count"), [(None, 0), ("turn_synthetic", 7)])
async def test_session_environment_reset_stream(
    sync: bool, strict: bool, turn_id: str | None, reset_count: int
) -> None:
    payload = {
        "type": "agent.session.environment.reset",
        "event_id": "event_synthetic",
        "session_id": "session_synthetic",
        "environment_id": "environment_synthetic",
        "turn_id": turn_id,
        "reset_count": reset_count,
    }

    def handler(request: httpx2.Request) -> httpx2.Response:
        assert request.method == "GET"
        assert request.url.path == "/v1/agents/sessions/session_synthetic/events"
        return httpx2.Response(
            200,
            headers={"content-type": "text/event-stream"},
            content=f"data: {json.dumps(payload)}\n\n",
        )

    if sync:
        with OpenAI(
            api_key="synthetic",
            base_url="https://sdk-test.example/v1",
            max_retries=0,
            _strict_response_validation=strict,
            http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
        ) as client:
            with client.beta.agents.sessions.events.stream("session_synthetic") as stream:
                events = list(stream)
            assert stream.response.is_closed
    else:
        async with AsyncOpenAI(
            api_key="synthetic",
            base_url="https://sdk-test.example/v1",
            max_retries=0,
            _strict_response_validation=strict,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False),
        ) as async_client:
            async with await async_client.beta.agents.sessions.events.stream("session_synthetic") as async_stream:
                events = [event async for event in async_stream]
            assert async_stream.response.is_closed

    assert len(events) == 1
    event = events[0]
    assert isinstance(event, AgentSessionEnvironmentResetEvent)
    assert event.type == "agent.session.environment.reset"
    assert event.event_id == "event_synthetic"
    assert event.session_id == "session_synthetic"
    assert event.environment_id == "environment_synthetic"
    assert event.turn_id == turn_id
    assert event.reset_count == reset_count
    assert event.to_dict() == payload
