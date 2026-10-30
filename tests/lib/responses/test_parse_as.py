from __future__ import annotations

import json
from typing_extensions import assert_type

import pytest
from pydantic import BaseModel

from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from openai.types.responses import ResponseConfigurationUpdateItem, ResponseConfigurationUpdateItemParamParam
from openai.lib._parsing._responses import type_to_text_format_param

from ...conftest import base_url


class ShortAnswer(BaseModel):
    answer: str


class DetailedAnswer(ShortAnswer):
    evidence: str


def _detailed_update() -> ResponseConfigurationUpdateItemParamParam:
    fmt = type_to_text_format_param(DetailedAnswer)
    assert fmt["type"] == "json_schema"
    return {"type": "configuration_update", "text": {"format": fmt}}


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("client,async_client", [(False, False)], indirect=True)
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_parse_as_on_continuation(
    client: OpenAI, async_client: AsyncOpenAI, respx2_mock: MockRouter, sync: bool
) -> None:
    text = '{"answer":"yes","evidence":"the receipt"}'
    route = respx2_mock.post("/responses").respond(
        json={"output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}]}
    )
    if sync:
        response = client.responses.parse(
            previous_response_id="resp_previous", input="Explain.", text_format=ShortAnswer, parse_as=DetailedAnswer
        )
    else:
        response = await async_client.responses.parse(
            previous_response_id="resp_previous", input="Explain.", text_format=ShortAnswer, parse_as=DetailedAnswer
        )

    assert_type(response.output_parsed, DetailedAnswer | None)
    assert response.output_parsed == DetailedAnswer(answer="yes", evidence="the receipt")
    body = json.loads(route.calls.last.request.content)
    assert body["text"]["format"] == type_to_text_format_param(ShortAnswer)
    assert body["previous_response_id"] == "resp_previous"
    assert "parse_as" not in body


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("client", [False], indirect=True)
def test_parse_as_does_not_send_a_top_level_schema(client: OpenAI, respx2_mock: MockRouter) -> None:
    update = _detailed_update()
    text = '{"answer":"yes","evidence":"the receipt"}'
    route = respx2_mock.post("/responses").respond(
        json={"output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}]}
    )
    response = client.responses.parse(input=[update], parse_as=DetailedAnswer)

    assert response.output_parsed == DetailedAnswer(answer="yes", evidence="the receipt")
    assert json.loads(route.calls.last.request.content) == {"input": [update]}


@pytest.mark.respx2(base_url=base_url)
@pytest.mark.parametrize("client", [False], indirect=True)
def test_visible_format_updates(client: OpenAI, respx2_mock: MockRouter) -> None:
    detailed = _detailed_update()
    reasoning: ResponseConfigurationUpdateItemParamParam = {
        "type": "configuration_update",
        "reasoning": {"effort": "high"},
    }
    reset: ResponseConfigurationUpdateItemParamParam = {
        "type": "configuration_update",
        "text": {"format": {"type": "text"}},
    }
    route = respx2_mock.post("/responses").respond(
        json={"output": [{"type": "message", "content": [{"type": "output_text", "text": "plain text"}]}]}
    )
    with pytest.raises(TypeError, match="Pass parse_as"):
        client.responses.parse(text_format=ShortAnswer, input=[detailed, reasoning])
    assert not route.called

    response = client.responses.parse(text_format=ShortAnswer, input=[detailed, reset, reasoning])
    assert response.output_text == "plain text"
    assert response.output_parsed is None

    with pytest.raises(TypeError, match="plain-text format update"):
        client.responses.parse(text_format=ShortAnswer, parse_as=DetailedAnswer, input=[reset])
    assert route.call_count == 1

    response_text = client.responses.parse(previous_response_id="resp_reset", text_format=ShortAnswer, parse_as=None)
    assert_type(response_text.output_parsed, None)
    assert response_text.output_parsed is None


@pytest.mark.respx2(base_url=base_url)
def test_list_input_items_preserves_format_updates(client: OpenAI, respx2_mock: MockRouter) -> None:
    items = [
        {"id": "cnfu_schema", **_detailed_update()},
        {
            "id": "cnfu_reset",
            "type": "configuration_update",
            "reasoning": {"effort": "high"},
            "text": {"format": {"type": "text"}},
        },
        {"id": "cnfu_reason", "type": "configuration_update", "reasoning": {"effort": "low"}},
    ]
    respx2_mock.get("/responses/resp_test/input_items").respond(
        json={"object": "list", "data": items, "first_id": "cnfu_schema", "last_id": "cnfu_reason", "has_more": False}
    )

    detailed, reset, reasoning = client.responses.input_items.list("resp_test").data
    assert isinstance(detailed, ResponseConfigurationUpdateItem) and detailed.text is not None
    assert detailed.text.format.type == "json_schema"
    assert detailed.text.format.name == "DetailedAnswer"
    assert isinstance(reset, ResponseConfigurationUpdateItem) and reset.text is not None
    assert reset.text.format.type == "text"
    assert isinstance(reasoning, ResponseConfigurationUpdateItem) and reasoning.text is None
    assert [item.to_dict() for item in (detailed, reset, reasoning)] == items
