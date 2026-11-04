from __future__ import annotations

import json

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from openai.types.beta.agents.session_update_params import SessionUpdateParams

CASES: list[SessionUpdateParams] = [
    {},
    {"agent": {}},
    {"agent": {"reasoning": {}}},
    {"agent": {"model": ""}},
    {"agent": {"model": "gpt-5", "reasoning": {"effort": "low"}, "service_tier": "priority"}},
    {"agent": {"reasoning": {"effort": None}, "service_tier": None}},
    {"metadata": {"purpose": "test"}},
    {"metadata": None},
    {"metadata": {}},
]


@pytest.mark.parametrize("body", CASES)
def test_session_update_body(respx2_mock: MockRouter, body: SessionUpdateParams) -> None:
    route = respx2_mock.post("https://example.test/v1/agents/sessions/session_test").mock(
        return_value=httpx2.Response(200, json={})
    )

    with OpenAI(
        base_url="https://example.test/v1",
        api_key="test-key",
        http_client=httpx2.Client(trust_env=False),
    ) as client:
        client.beta.agents.sessions.with_raw_response.update("session_test", **body)

    assert route.call_count == 1
    assert json.loads(route.calls.last.request.content) == body


@pytest.mark.parametrize("body", CASES)
async def test_async_session_update_body(respx2_mock: MockRouter, body: SessionUpdateParams) -> None:
    route = respx2_mock.post("https://example.test/v1/agents/sessions/session_test").mock(
        return_value=httpx2.Response(200, json={})
    )

    async with AsyncOpenAI(
        base_url="https://example.test/v1",
        api_key="test-key",
        http_client=httpx2.AsyncClient(trust_env=False),
    ) as async_client:
        await async_client.beta.agents.sessions.with_raw_response.update("session_test", **body)

    assert route.call_count == 1
    assert json.loads(route.calls.last.request.content) == body
