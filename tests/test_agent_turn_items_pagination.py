from typing import Callable

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI


def turn_pages(requests: list[httpx2.Request], final_item_type: str) -> Callable[[httpx2.Request], httpx2.Response]:
    def handle(request: httpx2.Request) -> httpx2.Response:
        index = len(requests)
        requests.append(request)
        assert index < 2, "must not request another page after has_more: false"
        assert request.url.path == "/v1/agents/sessions/session_test/turns/turn_test/items"
        assert dict(request.url.params) == {
            "order": "asc",
            "limit": "1",
            **({"after": "response:cursor/+first"} if index else {}),
        }
        return httpx2.Response(
            200,
            json={
                "object": "list",
                "data": [
                    {
                        "id": None if index == 0 else "terminal_item",
                        "type": final_item_type if index == 0 else "message",
                        "turn_id": "turn_test",
                        "role": "user",
                        "status": "completed",
                        "content": [],
                    }
                ],
                "last_id": "response:cursor/+first" if index == 0 else "valid_but_terminal_cursor",
                "has_more": index == 0,
            },
        )

    return handle


@pytest.mark.parametrize("final_item_type", ["message", "future_item_type"])
def test_root_turn_items_follow_response_cursor(final_item_type: str) -> None:
    requests: list[httpx2.Request] = []
    with OpenAI(
        api_key="synthetic",
        base_url="https://sdk-test.example/v1",
        max_retries=0,
        http_client=httpx2.Client(
            transport=httpx2.MockTransport(turn_pages(requests, final_item_type)), trust_env=False
        ),
    ) as client:
        items = list(
            client.beta.agents.sessions.turns.items.list("turn_test", session_id="session_test", order="asc", limit=1)
        )
        assert [item.id for item in items] == [None, "terminal_item"]
    assert len(requests) == 2


@pytest.mark.parametrize("final_item_type", ["message", "future_item_type"])
async def test_async_root_turn_items_follow_response_cursor(final_item_type: str) -> None:
    requests: list[httpx2.Request] = []
    async with AsyncOpenAI(
        api_key="synthetic",
        base_url="https://sdk-test.example/v1",
        max_retries=0,
        http_client=httpx2.AsyncClient(
            transport=httpx2.MockTransport(turn_pages(requests, final_item_type)), trust_env=False
        ),
    ) as client:
        page = await client.beta.agents.sessions.turns.items.list(
            "turn_test", session_id="session_test", order="asc", limit=1
        )
        assert [item.id async for item in page] == [None, "terminal_item"]
    assert len(requests) == 2
