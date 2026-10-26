from __future__ import annotations

from typing import Any, Literal

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.types.admin.organization import UsageDecisionsResponse, UsageCompletionsResponse


def payload(endpoint: str, value: int | None | Literal["omitted"]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "object": f"organization.usage.{endpoint}.result",
        "input_tokens": 200,
        "output_tokens": 20,
        "num_model_requests": 1,
        "input_cache_write_tokens": 17,
        "input_cache_write_12h_tokens": 19,
    }
    if value != "omitted":
        result["input_cache_write_30m_tokens"] = value
    return {
        "object": "page",
        "data": [{"object": "bucket", "start_time": 0, "end_time": 60, "results": [result]}],
        "has_more": False,
        "next_page": None,
    }


def assert_metric(response: UsageCompletionsResponse | UsageDecisionsResponse, expected: int | None) -> None:
    result = response.data[0].results[0]
    assert (
        result.object == "organization.usage.completions.result"
        or result.object == "organization.usage.decisions.result"
    )
    assert result.input_cache_write_30m_tokens == expected
    assert result.input_cache_write_tokens == 17
    assert result.input_cache_write_12h_tokens == 19


@pytest.mark.parametrize("endpoint", ["completions", "decisions"])
@pytest.mark.parametrize("value", [73, 0, None, "omitted"])
def test_usage_cache_write(endpoint: str, value: int | None | Literal["omitted"]) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        assert request.method == "GET"
        assert request.url.path == f"/organization/usage/{endpoint}"
        return httpx2.Response(200, json=payload(endpoint, value))

    with OpenAI(
        api_key="fake-project-key",
        admin_api_key="fake-admin-key",
        base_url="https://example.test",
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler)),
    ) as client:
        response = (
            client.admin.organization.usage.completions(start_time=0)
            if endpoint == "completions"
            else client.admin.organization.usage.decisions(start_time=0)
        )
        assert_metric(response, None if value == "omitted" else value)
    assert len(requests) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["completions", "decisions"])
@pytest.mark.parametrize("value", [73, 0, None, "omitted"])
async def test_async_usage_cache_write(endpoint: str, value: int | None | Literal["omitted"]) -> None:
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        assert request.method == "GET"
        assert request.url.path == f"/organization/usage/{endpoint}"
        return httpx2.Response(200, json=payload(endpoint, value))

    async with AsyncOpenAI(
        api_key="fake-project-key",
        admin_api_key="fake-admin-key",
        base_url="https://example.test",
        max_retries=0,
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler)),
    ) as client:
        response = (
            await client.admin.organization.usage.completions(start_time=0)
            if endpoint == "completions"
            else await client.admin.organization.usage.decisions(start_time=0)
        )
        assert_metric(response, None if value == "omitted" else value)
    assert len(requests) == 1
