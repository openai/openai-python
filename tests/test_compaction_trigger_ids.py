from __future__ import annotations

import json
from typing import Any

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.types.beta.beta_response_input_item import CompactionTrigger as BetaCompactionTrigger
from openai.types.beta.beta_response_input_item_param import CompactionTrigger as BetaCompactionTriggerParam
from openai.types.responses.response_input_item_param import CompactionTrigger


@pytest.mark.parametrize("beta", [False, True])
@pytest.mark.parametrize("fields", [{}, {"id": None}, {"id": ""}, {"id": "msg_transport_compat"}])
def test_compaction_trigger_ids_cross_transport(beta: bool, fields: dict[str, Any]) -> None:
    trigger: dict[str, Any] = {"type": "compaction_trigger", **fields}
    if beta:
        trigger["agent"] = {"agent_name": "assistant"}
    calls: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        calls.append(request)
        assert request.url.path == "/v1/responses/resp_compat"
        return httpx2.Response(
            200,
            json={"id": "resp_compat", "object": "response", "instructions": [trigger], "output": []},
        )

    with OpenAI(
        api_key="synthetic-key",
        base_url="https://example.invalid/v1",
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handle)),
    ) as client:
        result = client.beta.responses.retrieve("resp_compat") if beta else client.responses.retrieve("resp_compat")
        assert isinstance(result.instructions, list)
        item = result.instructions[0]
        assert item.type == "compaction_trigger"
        assert item.id == fields.get("id")
        assert ("id" in item.model_fields_set) == ("id" in fields)
        if beta:
            assert isinstance(item, BetaCompactionTrigger)
            assert item.agent is not None
            assert item.agent.agent_name == "assistant"
    assert len(calls) == 1
    assert calls[0].method == "GET"


@pytest.mark.parametrize("beta", [False, True])
@pytest.mark.parametrize("fields", [{}, {"id": None}, {"id": ""}, {"id": "msg_request_compat"}])
def test_compaction_trigger_request_compatibility(beta: bool, fields: dict[str, Any]) -> None:
    # Existing callers can still construct a trigger with only its discriminator.
    legacy: CompactionTrigger = {"type": "compaction_trigger"}
    trigger: BetaCompactionTriggerParam = {**legacy}
    if "id" in fields:
        trigger["id"] = fields["id"]
    if beta:
        trigger["agent"] = {"agent_name": "assistant"}
    bodies: list[dict[str, Any]] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        assert request.method == "POST"
        assert request.url.path == "/v1/responses"
        bodies.append(json.loads(request.content))
        return httpx2.Response(200, json={"id": "resp_compat", "object": "response", "output": []})

    with OpenAI(
        api_key="synthetic-key",
        base_url="https://example.invalid/v1",
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handle)),
    ) as client:
        if beta:
            client.beta.responses.create(model="gpt-4o", input=[trigger])
        else:
            client.responses.create(model="gpt-4o", input=[trigger])
    assert len(bodies) == 1
    assert bodies[0]["input"] == [trigger]


@pytest.mark.parametrize("beta", [False, True])
@pytest.mark.parametrize("fields", [{}, {"id": None}, {"id": ""}, {"id": "msg_transport_compat"}])
async def test_async_compaction_trigger_transport(beta: bool, fields: dict[str, Any]) -> None:
    trigger: BetaCompactionTriggerParam = {"type": "compaction_trigger"}
    if "id" in fields:
        trigger["id"] = fields["id"]
    if beta:
        trigger["agent"] = {"agent_name": "assistant"}
    methods: list[str] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        methods.append(request.method)
        assert request.url.params.get("beta") == ("true" if beta else None)
        if request.method == "POST":
            assert request.url.path == "/v1/responses"
            assert json.loads(request.content)["input"] == [trigger]
        else:
            assert request.method == "GET"
            assert request.url.path == "/v1/responses/resp_compat"
        return httpx2.Response(
            200,
            json={"id": "resp_compat", "object": "response", "instructions": [trigger], "output": []},
        )

    async with AsyncOpenAI(
        api_key="synthetic-key",
        base_url="https://example.invalid/v1",
        max_retries=0,
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handle)),
    ) as client:
        result = (
            await client.beta.responses.retrieve("resp_compat")
            if beta
            else await client.responses.retrieve("resp_compat")
        )
        assert isinstance(result.instructions, list)
        item = result.instructions[0]
        assert item.type == "compaction_trigger"
        assert item.id == fields.get("id")
        assert ("id" in item.model_fields_set) == ("id" in fields)
        if beta:
            assert isinstance(item, BetaCompactionTrigger)
            assert item.agent is not None
            assert item.agent.agent_name == "assistant"
            await client.beta.responses.create(model="gpt-4o", input=[trigger])
        else:
            await client.responses.create(model="gpt-4o", input=[trigger])
    assert methods == ["GET", "POST"]
