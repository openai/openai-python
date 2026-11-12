from __future__ import annotations

import json
from typing import Any

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from openai.lib.streaming.chat import ChatCompletionStreamEvent
from openai.types.chat.chat_completion import Moderation

from ...conftest import base_url


def moderation_result(*, flagged: bool) -> dict[str, Any]:
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


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("scenario", ["flagged", "error", "input_error", "initial", "replacement", "unmoderated"])
@pytest.mark.respx2(base_url=base_url)
async def test_stream_moderation(
    sync: bool,
    scenario: str,
    client: OpenAI,
    async_client: AsyncOpenAI,
    respx2_mock: MockRouter,
) -> None:
    success = {"input": moderation_result(flagged=False), "output": moderation_result(flagged=True)}
    error = {
        "input": moderation_result(flagged=True),
        "output": {"type": "error", "code": "test_error", "message": "Synthetic moderation error"},
    }
    if scenario == "input_error":
        error = {"input": error["output"], "output": moderation_result(flagged=False)}
    initial = error if scenario in {"initial", "replacement"} else None
    final_report = (
        error if scenario in {"error", "input_error"} else success if scenario in {"flagged", "replacement"} else None
    )
    expected = final_report or initial
    choices: list[dict[str, Any]] = [
        {"index": 0, "delta": {"role": "assistant", "content": "o"}, "finish_reason": None},
        {"index": 0, "delta": {"content": "k"}, "finish_reason": "stop"},
    ]
    chunks: list[dict[str, Any]] = [
        {
            "id": "chatcmpl-test",
            "object": "chat.completion.chunk",
            "created": 0,
            "model": "test-model",
            "choices": [choices[index]] if index < 2 else [],
        }
        for index in range(4)
    ]
    if initial is not None:
        chunks[0]["moderation"] = initial
    if final_report is not None:
        chunks[2]["moderation"] = final_report
    chunks[3]["moderation"] = None
    chunks[3]["usage"] = {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
    respx2_mock.post("/chat/completions").mock(
        return_value=httpx2.Response(
            200,
            headers={"content-type": "text/event-stream"},
            content="".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks) + "data: [DONE]\n\n",
        )
    )

    event_types: list[str] = []
    raw_reports: list[Any] = []
    snapshots: list[Any] = []

    def record(event: ChatCompletionStreamEvent[Any]) -> None:
        event_types.append(event.type)
        if event.type == "chunk":
            raw_reports.append(event.chunk.moderation.to_dict() if event.chunk.moderation is not None else None)
            moderation = event.snapshot.moderation
            if moderation is not None:
                assert isinstance(moderation, Moderation)
            snapshots.append(moderation.to_dict() if moderation is not None else None)

    if sync:
        raw_chunks = list(client.chat.completions.create(model="test-model", messages=[], stream=True))
        with client.chat.completions.stream(model="test-model", messages=[]) as stream:
            for event in stream:
                record(event)
            completion = stream.get_final_completion()
    else:
        raw_stream = await async_client.chat.completions.create(model="test-model", messages=[], stream=True)
        raw_chunks = [chunk async for chunk in raw_stream]
        async with async_client.chat.completions.stream(model="test-model", messages=[]) as async_stream:
            async for event in async_stream:
                record(event)
            completion = await async_stream.get_final_completion()

    assert raw_reports == [initial, None, final_report, None]
    assert raw_reports == [chunk.moderation.to_dict() if chunk.moderation is not None else None for chunk in raw_chunks]
    assert snapshots == [initial, initial, expected, expected]
    if expected is None:
        assert completion.moderation is None
    else:
        assert isinstance(completion.moderation, Moderation)
        assert completion.moderation.to_dict() == expected
    assert completion.choices[0].message.content == "ok"
    assert completion.choices[0].finish_reason == "stop"
    assert completion.usage is not None
    assert completion.usage.total_tokens == 2
    assert event_types == ["chunk", "content.delta", "chunk", "content.delta", "content.done", "chunk", "chunk"]
