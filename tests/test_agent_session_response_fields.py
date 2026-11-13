from __future__ import annotations

import httpx2
import pytest

from openai import OpenAI
from openai.types.beta.agent_session import RequiredActionSessionRequiredActionResourceMcpApprovalRequest


@pytest.mark.parametrize("mode", ["value", "null", "omitted"])
def test_agent_session_response_fields(mode: str) -> None:
    request = {
        "type": "mcp_tool_call",
        "server_label": "synthetic-server",
        "name": "synthetic-tool" if mode == "value" else None,
        "arguments": {"query": "synthetic-query"} if mode == "value" else None,
        "message": "Synthetic approval",
    }
    session: dict[str, object] = {
        "id": "session_test",
        "object": "agent.session",
        "required_actions": [
            {"type": "mcp_approval_request", "request_id": "request_test", "turn_id": "turn_test", "request": request}
        ],
    }
    turn: dict[str, object] = {"id": "turn_test", "object": "agent.session.turn"}
    if mode != "omitted":
        session["prompt_cache_options"] = {"ttl": "12h"} if mode == "value" else None
        turn["prompt_cache_options"] = {"ttl": "30m"} if mode == "value" else None
    paths: list[str] = []

    def respond(http_request: httpx2.Request) -> httpx2.Response:
        paths.append(http_request.url.path)
        return httpx2.Response(200, json=turn if http_request.url.path.endswith("/turns/turn_test") else session)

    with OpenAI(
        api_key="fake-test-key",
        base_url="https://example.test",
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(respond), trust_env=False),
    ) as client:
        actual_session = client.beta.agents.sessions.retrieve("session_test")
        actual_turn = client.beta.agents.sessions.turns.retrieve("turn_test", session_id="session_test")

    assert paths == ["/agents/sessions/session_test", "/agents/sessions/session_test/turns/turn_test"]
    action = actual_session.required_actions[0]
    assert isinstance(action, RequiredActionSessionRequiredActionResourceMcpApprovalRequest)
    assert action.request.name == ("synthetic-tool" if mode == "value" else None)
    assert action.request.arguments == ({"query": "synthetic-query"} if mode == "value" else None)
    if mode == "value":
        assert (actual_session.prompt_cache_options.ttl if actual_session.prompt_cache_options else None) == "12h"
        assert (actual_turn.prompt_cache_options.ttl if actual_turn.prompt_cache_options else None) == "30m"
    else:
        assert actual_session.prompt_cache_options is None
        assert actual_turn.prompt_cache_options is None
