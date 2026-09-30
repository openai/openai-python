from typing import Callable

import httpx2

from openai import OpenAI, AsyncOpenAI
from openai.pagination import SyncTokenPage, AsyncTokenPage

TOKEN = "synthetic:token/+="


def page_handler(requests: list[httpx2.Request]) -> Callable[[httpx2.Request], httpx2.Response]:
    def handle(request: httpx2.Request) -> httpx2.Response:
        index = len(requests)
        requests.append(request)
        assert index < 2, "iteration must stop at the terminal page"
        assert request.url.path == "/v1/agents/environments/env_test/files"
        assert dict(request.url.params) == {
            "path": "/workspace/test",
            "order": "asc",
            "limit": "1",
            **({"page": TOKEN} if index else {}),
        }
        assert request.headers["x-pagination-test"] == "preserved"
        assert request.headers["openai-beta"] == "agents=v1"
        return httpx2.Response(
            200,
            json={
                "object": "page",
                "data": [
                    {
                        "object": "agent.environment.file",
                        "environment_id": "env_test",
                        "path": f"/workspace/test/{index}.txt",
                        "size_bytes": 1,
                    }
                ],
                "next": TOKEN if index == 0 else None,
                "has_more": index == 0,
            },
        )

    return handle


def test_sync_files_token_pagination() -> None:
    requests: list[httpx2.Request] = []
    with OpenAI(
        api_key="synthetic",
        base_url="https://sdk-test.example/v1",
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(page_handler(requests)), trust_env=False),
    ) as client:
        page = client.beta.agents.environments.files.list(
            "env_test",
            path="/workspace/test",
            order="asc",
            limit=1,
            extra_headers={"x-pagination-test": "preserved"},
        )
        assert isinstance(page, SyncTokenPage)
        assert [file.path for file in page] == ["/workspace/test/0.txt", "/workspace/test/1.txt"]
    assert len(requests) == 2


async def test_async_files_token_pagination() -> None:
    requests: list[httpx2.Request] = []
    async with AsyncOpenAI(
        api_key="synthetic",
        base_url="https://sdk-test.example/v1",
        max_retries=0,
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(page_handler(requests)), trust_env=False),
    ) as client:
        page = await client.beta.agents.environments.files.list(
            "env_test",
            path="/workspace/test",
            order="asc",
            limit=1,
            extra_headers={"x-pagination-test": "preserved"},
        )
        assert isinstance(page, AsyncTokenPage)
        assert [file.path async for file in page] == ["/workspace/test/0.txt", "/workspace/test/1.txt"]
    assert len(requests) == 2
