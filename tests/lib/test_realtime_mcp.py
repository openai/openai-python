from __future__ import annotations

import os
import json
from typing import Protocol, cast

import httpx
import pytest
from respx import MockRouter

from openai import OpenAI, AsyncOpenAI

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class MockRequestCall(Protocol):
    request: httpx.Request


@pytest.mark.respx(base_url=base_url)
def test_realtime_calls_accept_sends_mcp_tools(client: OpenAI, respx_mock: MockRouter) -> None:
    respx_mock.post("/realtime/calls/call_123/accept").mock(return_value=httpx.Response(204))

    client.realtime.calls.accept(
        "call_123",
        type="realtime",
        tools=[
            {
                "type": "mcp",
                "server_label": "search",
                "server_url": "https://example.com/mcp",
                "allowed_tools": ["lookup"],
                "headers": {"x-api-key": "test-key"},
                "require_approval": "never",
            }
        ],
    )

    calls = cast("list[MockRequestCall]", respx_mock.calls)
    assert json.loads(calls[0].request.content) == {
        "type": "realtime",
        "tools": [
            {
                "type": "mcp",
                "server_label": "search",
                "server_url": "https://example.com/mcp",
                "allowed_tools": ["lookup"],
                "headers": {"x-api-key": "test-key"},
                "require_approval": "never",
            }
        ],
    }


@pytest.mark.respx(base_url=base_url)
async def test_async_realtime_calls_accept_sends_mcp_tools(async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
    respx_mock.post("/realtime/calls/call_123/accept").mock(return_value=httpx.Response(204))

    await async_client.realtime.calls.accept(
        "call_123",
        type="realtime",
        tools=[
            {
                "type": "mcp",
                "server_label": "search",
                "server_url": "https://example.com/mcp",
                "allowed_tools": {"tool_names": ["lookup"]},
                "require_approval": {"never": {"tool_names": ["lookup"]}},
            }
        ],
    )

    calls = cast("list[MockRequestCall]", respx_mock.calls)
    assert json.loads(calls[0].request.content) == {
        "type": "realtime",
        "tools": [
            {
                "type": "mcp",
                "server_label": "search",
                "server_url": "https://example.com/mcp",
                "allowed_tools": {"tool_names": ["lookup"]},
                "require_approval": {"never": {"tool_names": ["lookup"]}},
            }
        ],
    }
