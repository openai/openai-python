from __future__ import annotations

import json
from typing import Any

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from openai.lib.streaming.chat import ChatCompletionStreamEvent

from ...conftest import base_url

USAGE = {"prompt_tokens": 9, "completion_tokens": 2, "total_tokens": 11}
FINGERPRINT = "fp_test"


def moderation_report() -> dict[str, Any]:
    def result(*, flagged: bool) -> dict[str, Any]:
        return {
            "type": "moderation_results",
            "model": "test-moderation",
            "results": [
                {
                    "type": "moderation_result",
                    "model": "test-moderation",
                    "flagged": flagged,
                    "categories": {"violence": flagged},
                    "category_scores": {"violence": 0.75 if flagged else 0.0},
                    "category_applied_input_types": {"violence": ["text"]},
                }
            ],
        }

    return {"input": result(flagged=False), "output": result(flagged=True)}


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.respx2(base_url=base_url)
async def test_stream_retains_usage_and_fingerprint_reported_before_a_trailing_chunk(
    sync: bool,
    client: OpenAI,
    async_client: AsyncOpenAI,
    respx2_mock: MockRouter,
) -> None:
    """`usage` and `system_fingerprint` must survive a later chunk that omits them.

    A provider can report usage on one chunk and then send a trailing metadata
    chunk (a moderation report, for instance) that carries neither. Moderation
    already retains the last report across such a chunk; usage and the
    fingerprint have to behave the same way or the final completion loses
    billing data the stream did deliver.
    """
    chunks: list[dict[str, Any]] = [
        {
            "id": "chatcmpl-test",
            "object": "chat.completion.chunk",
            "created": 0,
            "model": "test-model",
            "system_fingerprint": FINGERPRINT,
            "usage": USAGE,
            "choices": [{"index": 0, "delta": {"role": "assistant", "content": "o"}, "finish_reason": None}],
        },
        {
            "id": "chatcmpl-test",
            "object": "chat.completion.chunk",
            "created": 0,
            "model": "test-model",
            "choices": [{"index": 0, "delta": {"content": "k"}, "finish_reason": "stop"}],
        },
        {
            "id": "chatcmpl-test",
            "object": "chat.completion.chunk",
            "created": 0,
            "model": "test-model",
            "choices": [],
            "moderation": moderation_report(),
        },
    ]
    respx2_mock.post("/chat/completions").mock(
        return_value=httpx2.Response(
            200,
            headers={"content-type": "text/event-stream"},
            content="".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks) + "data: [DONE]\n\n",
        )
    )

    snapshots: list[Any] = []
    fingerprints: list[Any] = []

    def record(event: ChatCompletionStreamEvent[Any]) -> None:
        if event.type == "chunk":
            snapshots.append(None if event.snapshot.usage is None else event.snapshot.usage.total_tokens)
            fingerprints.append(event.snapshot.system_fingerprint)

    if sync:
        with client.chat.completions.stream(model="test-model", messages=[]) as stream:
            for event in stream:
                record(event)
            completion = stream.get_final_completion()
    else:
        async with async_client.chat.completions.stream(model="test-model", messages=[]) as async_stream:
            async for event in async_stream:
                record(event)
            completion = await async_stream.get_final_completion()

    # every snapshot after the reporting chunk keeps the values, including the
    # one built from the trailing moderation chunk that carries neither
    assert snapshots == [11, 11, 11]
    assert fingerprints == [FINGERPRINT, FINGERPRINT, FINGERPRINT]

    assert completion.usage is not None
    assert completion.usage.total_tokens == 11
    assert completion.usage.prompt_tokens == 9
    assert completion.usage.completion_tokens == 2
    assert completion.system_fingerprint == FINGERPRINT

    # the content and the moderation report are unaffected
    assert completion.choices[0].message.content == "ok"
    assert completion.choices[0].finish_reason == "stop"
    assert completion.moderation is not None
