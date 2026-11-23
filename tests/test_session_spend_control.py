from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.types.beta import AgentSessionBudgetReachedEvent
from tests.lib.streaming.agents.test_streams import session


class BudgetServer:
    def __init__(self) -> None:
        self.payload: dict[str, object] = {**session(), "spend_control": {"limit": None, "consumed": 987}}
        self.streaming = False
        self.requests: list[dict[str, object]] = []

    def handle(self, request: httpx2.Request) -> httpx2.Response:
        if request.method == "POST":
            self.requests.append(json.loads(request.content))
        if self.streaming:
            return httpx2.Response(
                200, headers={"content-type": "text/event-stream"}, content=f"data: {json.dumps(self.payload)}\n\n"
            )
        return httpx2.Response(200, json=self.payload)


@pytest.fixture
def budget_server() -> BudgetServer:
    return BudgetServer()


@pytest.fixture(params=[False, True], ids=["sync", "async"])
async def budget_client(
    request: pytest.FixtureRequest, budget_server: BudgetServer
) -> AsyncIterator[OpenAI | AsyncOpenAI]:
    transport = httpx2.MockTransport(budget_server.handle)
    if request.param:
        async with AsyncOpenAI(
            api_key="synthetic",
            max_retries=0,
            _strict_response_validation=True,
            http_client=httpx2.AsyncClient(transport=transport, trust_env=False),
        ) as client:
            yield client
    else:
        with OpenAI(
            api_key="synthetic",
            max_retries=0,
            _strict_response_validation=True,
            http_client=httpx2.Client(transport=transport, trust_env=False),
        ) as client:
            yield client


@pytest.mark.parametrize("values", [(4321, 987), (None, 987), (None, None), (None, 0)])
async def test_session_spend_control_response(
    budget_client: OpenAI | AsyncOpenAI,
    budget_server: BudgetServer,
    values: tuple[int | None, int | None],
) -> None:
    limit, consumed = values
    budget_server.payload = {**session(), "spend_control": {"limit": limit, "consumed": consumed}}
    if isinstance(budget_client, AsyncOpenAI):
        result = await budget_client.beta.agents.sessions.create(
            environment={"type": "none"}, spend_control={"limit": limit}
        )
    else:
        result = budget_client.beta.agents.sessions.create(environment={"type": "none"}, spend_control={"limit": limit})
    assert budget_server.requests[0]["spend_control"] == {"limit": limit}
    assert result.spend_control.limit == limit
    assert result.spend_control.consumed == consumed


@pytest.mark.parametrize("update", [{}, None, {"limit": None}, {"limit": 4321}])
async def test_session_spend_control_update(
    budget_client: OpenAI | AsyncOpenAI, budget_server: BudgetServer, update: dict[str, int | None] | None
) -> None:
    if isinstance(budget_client, AsyncOpenAI):
        if update is None:
            await budget_client.beta.agents.sessions.update("session_test", spend_control=None)
        elif update:
            await budget_client.beta.agents.sessions.update("session_test", spend_control={"limit": update["limit"]})
        else:
            await budget_client.beta.agents.sessions.update("session_test")
    elif update is None:
        budget_client.beta.agents.sessions.update("session_test", spend_control=None)
    elif update:
        budget_client.beta.agents.sessions.update("session_test", spend_control={"limit": update["limit"]})
    else:
        budget_client.beta.agents.sessions.update("session_test")
    assert budget_server.requests == ([{}] if update == {} else [{"spend_control": update}])


@pytest.mark.parametrize("creation", [False, True])
@pytest.mark.parametrize("limit", [4321, None])
async def test_typed_budget_event(
    budget_client: OpenAI | AsyncOpenAI, budget_server: BudgetServer, creation: bool, limit: int | None
) -> None:
    budget_server.payload = {
        "type": "agent.session.budget_reached",
        "event_id": "event_budget",
        "session": {**session("budget_reached"), "spend_control": {"limit": limit, "consumed": 4987}},
    }
    budget_server.streaming = True
    if isinstance(budget_client, AsyncOpenAI):
        stream = (
            await budget_client.beta.agents.sessions.create(
                environment={"type": "none"}, stream=True, spend_control={"limit": limit}
            )
            if creation
            else await budget_client.beta.agents.sessions.events.stream("session_test")
        )
        async with stream:
            events = [event async for event in stream]
    else:
        stream = (
            budget_client.beta.agents.sessions.create(
                environment={"type": "none"}, stream=True, spend_control={"limit": limit}
            )
            if creation
            else budget_client.beta.agents.sessions.events.stream("session_test")
        )
        with stream:
            events = list(stream)
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, AgentSessionBudgetReachedEvent)
    assert event.session.status == "budget_reached"
    assert event.session.spend_control.limit == limit
    assert event.session.spend_control.consumed == 4987
    if creation:
        assert budget_server.requests[0]["spend_control"] == {"limit": limit}
