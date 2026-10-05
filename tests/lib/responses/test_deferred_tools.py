from __future__ import annotations

import json
from typing import Any, cast

import httpx2
import pytest
from pydantic import BaseModel

import openai
from openai._types import Omit
from openai.types.responses import ToolParam

from .test_commentary_parsing import _response


class LookupItem(BaseModel):
    """Look up a catalog item."""

    item_id: str


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("compatibility", [False, True])
@pytest.mark.parametrize("defer_loading", [openai.omit, False, True])
async def test_deferred_typed_tool_request_and_parsing(
    asynchronous: bool, streaming: bool, compatibility: bool, defer_loading: bool | Omit
) -> None:
    if compatibility:
        tool: Any = openai.pydantic_function_tool(LookupItem, name="lookup_item")
        if defer_loading is not openai.omit:
            tool["function"]["defer_loading"] = defer_loading
        # Applicable options added to the compatibility definition must survive conversion.
        tool["function"]["allowed_callers"] = ["direct"]
        tool["function"]["output_schema"] = {"type": "object"}
    else:
        tool = openai.pydantic_responses_function_tool(LookupItem, name="lookup_item", defer_loading=defer_loading)
    tools: list[ToolParam] = [{"type": "tool_search"}, cast(ToolParam, tool)]
    item = {
        "id": "fc_test",
        "call_id": "call_test",
        "type": "function_call",
        "name": "lookup_item",
        "arguments": '{"item_id":"A123"}',
        "status": "completed",
    }

    def respond(request: httpx2.Request) -> httpx2.Response:
        submitted = json.loads(request.content)["tools"][1]
        assert submitted["name"] == "lookup_item"
        assert submitted["description"] == "Look up a catalog item."
        assert submitted["parameters"]["additionalProperties"] is False
        assert submitted["strict"] is True
        if defer_loading is openai.omit:
            assert "defer_loading" not in submitted
        else:
            assert submitted["defer_loading"] is defer_loading
        if compatibility:
            assert submitted["allowed_callers"] == ["direct"]
            assert submitted["output_schema"] == {"type": "object"}
        if not streaming:
            return httpx2.Response(200, json=_response([item]))
        events = [
            {"type": "response.created", "response": _response([])},
            {"type": "response.output_item.added", "output_index": 0, "item": item},
            {"type": "response.output_item.done", "output_index": 0, "item": item},
            {"type": "response.completed", "response": _response([item])},
        ]
        body = "".join(f"data: {json.dumps({**event, 'sequence_number': i})}\n\n" for i, event in enumerate(events))
        return httpx2.Response(200, text=body, headers={"content-type": "text/event-stream"})

    transport = httpx2.MockTransport(respond)
    if asynchronous:
        async with openai.AsyncOpenAI(
            api_key="synthetic", http_client=httpx2.AsyncClient(transport=transport, trust_env=False)
        ) as client:
            if streaming:
                async with client.responses.stream(model="test-model", input="Look up A123", tools=tools) as stream:
                    response = await stream.get_final_response()
            else:
                response = await client.responses.parse(model="test-model", input="Look up A123", tools=tools)
    else:
        with openai.OpenAI(
            api_key="synthetic", http_client=httpx2.Client(transport=transport, trust_env=False)
        ) as sync_client:
            if streaming:
                with sync_client.responses.stream(model="test-model", input="Look up A123", tools=tools) as sync_stream:
                    response = sync_stream.get_final_response()
            else:
                response = sync_client.responses.parse(model="test-model", input="Look up A123", tools=tools)
    call = response.output[0]
    assert call.type == "function_call"
    assert isinstance(call.parsed_arguments, LookupItem)
    assert call.parsed_arguments.item_id == "A123"


@pytest.mark.parametrize("streaming", [False, True])
def test_deferred_tool_configuration_errors_are_api_errors(streaming: bool) -> None:
    def reject(request: httpx2.Request) -> httpx2.Response:
        assert json.loads(request.content)["tools"][0]["defer_loading"] is True
        return httpx2.Response(
            400, json={"error": {"message": "Unsupported tool configuration", "type": "invalid_request_error"}}
        )

    # Deliberately omit tool search: the SDK forwards the option and leaves validation to the API.
    tool = openai.pydantic_responses_function_tool(LookupItem, defer_loading=True)
    with openai.OpenAI(
        api_key="synthetic", http_client=httpx2.Client(transport=httpx2.MockTransport(reject), trust_env=False)
    ) as client:
        with pytest.raises(openai.BadRequestError, match="Unsupported tool configuration"):
            if streaming:
                with client.responses.stream(model="test-model", input="Find A123", tools=[tool]) as stream:
                    stream.get_final_response()
            else:
                client.responses.parse(model="test-model", input="Find A123", tools=[tool])
