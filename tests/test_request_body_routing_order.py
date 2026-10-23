from __future__ import annotations

import json
from typing import Any

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI

LARGE_PAYLOAD = "x" * (1024 * 1024)


def response_for(request: httpx2.Request) -> httpx2.Response:
    if request.url.path.endswith("/responses"):
        return httpx2.Response(
            200,
            json={
                "id": "resp_test",
                "created_at": 0,
                "model": "gpt-test",
                "object": "response",
                "output": [],
                "parallel_tool_calls": True,
                "status": "completed",
                "tool_choice": "auto",
                "tools": [],
            },
        )

    return httpx2.Response(
        200,
        json={
            "id": "chatcmpl_test",
            "choices": [],
            "created": 0,
            "model": "gpt-test",
            "object": "chat.completion",
        },
    )


def request_keys(request: httpx2.Request) -> list[str]:
    pairs: list[tuple[str, Any]] = json.loads(request.content, object_pairs_hook=lambda items: items)
    return [key for key, _ in pairs]


def assert_request_keys(
    request: httpx2.Request,
    *,
    prefix: list[str],
    absent: tuple[str, ...] = (),
) -> None:
    keys = request_keys(request)
    assert keys[: len(prefix)] == prefix
    assert not set(absent).intersection(keys)


def test_parse_helpers_prioritize_routing_fields_on_the_wire() -> None:
    requests: list[httpx2.Request] = []

    def record(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return response_for(request)

    with OpenAI(
        api_key="test-key",
        base_url="https://example.test/v1",
        http_client=httpx2.Client(transport=httpx2.MockTransport(record), trust_env=False),
    ) as client:
        client.responses.parse(
            model="gpt-test",
            stream=False,
            service_tier="default",
            input=LARGE_PAYLOAD,
        )
        client.chat.completions.parse(
            model="gpt-test",
            service_tier="default",
            messages=[{"role": "user", "content": LARGE_PAYLOAD}],
        )
        client.responses.parse(model="gpt-test", input=LARGE_PAYLOAD)
        client.chat.completions.parse(
            model="gpt-test",
            messages=[{"role": "user", "content": LARGE_PAYLOAD}],
        )

    assert_request_keys(
        requests[0],
        prefix=["model", "stream", "service_tier", "input"],
    )
    assert_request_keys(
        requests[1],
        prefix=["model", "stream", "service_tier", "messages"],
    )
    assert_request_keys(
        requests[2],
        prefix=["model", "input"],
        absent=("stream", "service_tier"),
    )
    assert_request_keys(
        requests[3],
        prefix=["model", "stream", "messages"],
        absent=("service_tier",),
    )


@pytest.mark.asyncio
async def test_async_parse_helpers_prioritize_routing_fields_on_the_wire() -> None:
    requests: list[httpx2.Request] = []

    def record(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return response_for(request)

    async with AsyncOpenAI(
        api_key="test-key",
        base_url="https://example.test/v1",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(record), trust_env=False),
    ) as client:
        await client.responses.parse(
            model="gpt-test",
            stream=False,
            service_tier="default",
            input=LARGE_PAYLOAD,
        )
        await client.chat.completions.parse(
            model="gpt-test",
            service_tier="default",
            messages=[{"role": "user", "content": LARGE_PAYLOAD}],
        )
        await client.responses.parse(model="gpt-test", input=LARGE_PAYLOAD)
        await client.chat.completions.parse(
            model="gpt-test",
            messages=[{"role": "user", "content": LARGE_PAYLOAD}],
        )

    assert_request_keys(
        requests[0],
        prefix=["model", "stream", "service_tier", "input"],
    )
    assert_request_keys(
        requests[1],
        prefix=["model", "stream", "service_tier", "messages"],
    )
    assert_request_keys(
        requests[2],
        prefix=["model", "input"],
        absent=("stream", "service_tier"),
    )
    assert_request_keys(
        requests[3],
        prefix=["model", "stream", "messages"],
        absent=("service_tier",),
    )
