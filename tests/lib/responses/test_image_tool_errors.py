from __future__ import annotations

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.types.beta.beta_response_output_item import ImageGenerationCall as BetaImageGenerationCall
from openai.types.responses.response_output_item import ImageGenerationCall


@pytest.mark.parametrize("beta", [False, True])
@pytest.mark.parametrize("sync", [False, True])
@pytest.mark.parametrize("shape", ["values", "nulls", "no_moderation", "no_error"])
async def test_image_tool_error_transport(beta: bool, sync: bool, shape: str) -> None:
    error: dict[str, object] = {
        "code": "moderation_blocked",
        "param": "input[0]",
        "type": "image_tool_error",
        "message": "Synthetic moderation failure",
        "moderation_details": {"moderation_stage": "output", "categories": ["synthetic_future_category"]},
    }
    if shape == "nulls":
        error.update(code=None, param=None)
    if shape == "no_moderation":
        del error["moderation_details"]
    item: dict[str, object] = {
        "id": "img_synthetic",
        "type": "image_generation_call",
        "status": "failed",
        "result": None,
    }
    if shape != "no_error":
        item["error"] = error
    requests: list[httpx2.Request] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        assert request.method == "GET"
        assert request.url.path == "/responses/resp_synthetic"
        assert request.url.params.get("beta") == ("true" if beta else None)
        return httpx2.Response(200, json={"id": "resp_synthetic", "output": [item]})

    transport = httpx2.MockTransport(respond)
    if sync:
        with OpenAI(
            api_key="fake-test-key", base_url="https://example.test", http_client=httpx2.Client(transport=transport)
        ) as client:
            result = (client.beta.responses if beta else client.responses).retrieve("resp_synthetic")
    else:
        async with AsyncOpenAI(
            api_key="fake-test-key",
            base_url="https://example.test",
            http_client=httpx2.AsyncClient(transport=transport),
        ) as async_client:
            result = await (async_client.beta.responses if beta else async_client.responses).retrieve("resp_synthetic")

    assert len(requests) == 1
    call = result.output[0]
    assert isinstance(call, (ImageGenerationCall, BetaImageGenerationCall))
    if shape == "no_error":
        assert call.error is None
        return
    assert call.error is not None
    assert call.error.code == (None if shape == "nulls" else "moderation_blocked")
    assert call.error.param == (None if shape == "nulls" else "input[0]")
    assert call.error.type == "image_tool_error"
    assert call.error.message == "Synthetic moderation failure"
    if shape == "no_moderation":
        assert call.error.moderation_details is None
    else:
        assert call.error.moderation_details is not None
        assert call.error.moderation_details.moderation_stage == "output"
        assert call.error.moderation_details.categories == ["synthetic_future_category"]
