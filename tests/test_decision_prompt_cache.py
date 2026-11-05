from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Optional, get_type_hints
from typing_extensions import Literal, Required

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.types.decision_input_text_param import PromptCacheBreakpoint as TextBreakpoint, DecisionInputTextParam
from openai.types.decision_input_image_param import PromptCacheBreakpoint as ImageBreakpoint, DecisionInputImageParam
from openai.types.decision_prompt_cache_breakpoint_param import DecisionPromptCacheBreakpointParam

if TYPE_CHECKING:
    old_text: TextBreakpoint = {"mode": "explicit"}
    old_image: ImageBreakpoint = {"mode": "explicit"}
    shared_from_text: DecisionPromptCacheBreakpointParam = old_text
    shared_from_image: DecisionPromptCacheBreakpointParam = old_image
    text: DecisionInputTextParam = {
        "type": "input_text",
        "text": "synthetic",
        "prompt_cache_breakpoint": shared_from_image,
    }
    image: DecisionInputImageParam = {
        "type": "input_image",
        "image_url": "https://example.test/image.png",
        "prompt_cache_breakpoint": shared_from_text,
    }


def test_legacy_breakpoint_exports() -> None:
    for cls in (TextBreakpoint, ImageBreakpoint, DecisionPromptCacheBreakpointParam):
        assert cls(mode="explicit") == {"mode": "explicit"}
        assert get_type_hints(cls, include_extras=True)["mode"] == Required[Literal["explicit"]]
    assert TextBreakpoint.__module__ == "openai.types.decision_input_text_param"
    assert ImageBreakpoint.__module__ == "openai.types.decision_input_image_param"


def test_shared_breakpoint_annotations() -> None:
    for cls in (DecisionInputTextParam, DecisionInputImageParam):
        assert get_type_hints(cls)["prompt_cache_breakpoint"] == Optional[DecisionPromptCacheBreakpointParam]


def request_body(mode: str) -> dict[str, Any]:
    content: list[dict[str, Any]] = [
        {"type": "input_text", "text": "synthetic"},
        {"type": "input_image", "image_url": "https://example.test/image.png"},
    ]
    body: dict[str, Any] = {
        "model": "synthetic-model",
        "input": [{"role": "user", "content": content}],
        "questions": [{"instructions": "Synthetic question", "type": "predicate"}],
    }
    if mode != "omitted":
        body["prompt_cache_key"] = None if mode == "nulls" else "synthetic-key"
        body["prompt_cache_options"] = None if mode == "nulls" else {"mode": mode, "ttl": "30m"}
        for part in content:
            part["prompt_cache_breakpoint"] = None if mode == "nulls" else {"mode": "explicit"}
    return body


def capture_request(request: httpx2.Request, captured: list[dict[str, Any]]) -> httpx2.Response:
    assert request.method == "POST"
    assert str(request.url) == "https://example.test/decisions"
    captured.append(json.loads(request.content))
    return httpx2.Response(
        200, json={"id": "decision_synthetic", "answers": [], "model": "synthetic-model", "usage": {}}
    )


@pytest.mark.parametrize("mode", ["explicit", "implicit", "nulls", "omitted"])
def test_sync_request(mode: str) -> None:
    captured: list[dict[str, Any]] = []
    body = request_body(mode)
    with OpenAI(
        api_key="fake-test-key",
        base_url="https://example.test",
        max_retries=0,
        http_client=httpx2.Client(
            transport=httpx2.MockTransport(lambda request: capture_request(request, captured)), trust_env=False
        ),
    ) as client:
        client.decisions.create(**body)
    assert captured == [body]


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["explicit", "implicit", "nulls", "omitted"])
async def test_async_request(mode: str) -> None:
    captured: list[dict[str, Any]] = []
    body = request_body(mode)
    async with AsyncOpenAI(
        api_key="fake-test-key",
        base_url="https://example.test",
        max_retries=0,
        http_client=httpx2.AsyncClient(
            transport=httpx2.MockTransport(lambda request: capture_request(request, captured)), trust_env=False
        ),
    ) as client:
        await client.decisions.create(**body)
    assert captured == [body]
