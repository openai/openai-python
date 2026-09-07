from __future__ import annotations

from typing import Literal

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI


def cancel_response(request: httpx2.Request) -> httpx2.Response:
    assert request.method == "POST"
    assert request.url == httpx2.URL("https://example.test/v1/evals/eval_test/runs/evalrun_test/cancel")
    return httpx2.Response(200, json={"id": "evalrun_test", "eval_id": "eval_test", "status": "canceled"})


@pytest.mark.parametrize("response_mode", ["parsed", "raw", "streaming"])
def test_sync_cancel_endpoint(response_mode: Literal["parsed", "raw", "streaming"]) -> None:
    with OpenAI(
        api_key="test-key",
        base_url="https://example.test/v1",
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(cancel_response), trust_env=False),
    ) as client:
        if response_mode == "parsed":
            run = client.evals.runs.cancel("evalrun_test", eval_id="eval_test")
        elif response_mode == "raw":
            run = client.evals.runs.with_raw_response.cancel("evalrun_test", eval_id="eval_test").parse()
        else:
            with client.evals.runs.with_streaming_response.cancel("evalrun_test", eval_id="eval_test") as response:
                run = response.parse()

    assert run.id == "evalrun_test"
    assert run.status == "canceled"


@pytest.mark.parametrize("response_mode", ["parsed", "raw", "streaming"])
async def test_async_cancel_endpoint(response_mode: Literal["parsed", "raw", "streaming"]) -> None:
    async with AsyncOpenAI(
        api_key="test-key",
        base_url="https://example.test/v1",
        max_retries=0,
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(cancel_response), trust_env=False),
    ) as client:
        if response_mode == "parsed":
            run = await client.evals.runs.cancel("evalrun_test", eval_id="eval_test")
        elif response_mode == "raw":
            raw_response = await client.evals.runs.with_raw_response.cancel("evalrun_test", eval_id="eval_test")
            run = raw_response.parse()
        else:
            async with client.evals.runs.with_streaming_response.cancel(
                "evalrun_test", eval_id="eval_test"
            ) as response:
                run = await response.parse()

    assert run.id == "evalrun_test"
    assert run.status == "canceled"
