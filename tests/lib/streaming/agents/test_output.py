from __future__ import annotations

import json
from typing import Any
from typing_extensions import Literal

import pytest
from pydantic import Field, BaseModel

from openai import OpenAI, AsyncOpenAI
from openai.lib.beta.agents import AgentTurnResultError, AgentOutputParseError, agent_text_format
from tests.lib.streaming.agents.test_results import ResultServer, server as server, message
from tests.lib.streaming.agents.test_streams import EventBody, sdk as sdk, idle, turn_event


class Report(BaseModel):
    summary: str
    findings: list[str]


class NestedReport(BaseModel):
    report: Report
    alternative: Report | None


def test_agents_format() -> None:
    format = agent_text_format(NestedReport)
    assert set(format) == {"type", "schema"}
    assert format["type"] == "json_schema"
    schema = format["schema"]
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["report", "alternative"]
    assert "name" not in format and "strict" not in format


def test_schema_rejects_open_objects() -> None:
    class WithMap(BaseModel):
        value: dict[str, str]

    with pytest.raises(ValueError, match="additionalProperties"):
        agent_text_format(WithMap)


def test_schema_normalizes_defaults_without_mutating_model() -> None:
    class WithDefault(BaseModel):
        value: str = "default"

    assert agent_text_format(WithDefault)["schema"]["required"] == ["value"]
    assert WithDefault().value == "default"


def test_schema_rejects_unsupported_unique_items() -> None:
    class WithSet(BaseModel):
        value: set[str]

    with pytest.raises(ValueError, match="uniqueItems"):
        agent_text_format(WithSet)


@pytest.mark.parametrize("creation", [False, True])
@pytest.mark.parametrize("progress", [False, True])
async def test_typed_result(sdk: OpenAI | AsyncOpenAI, server: ResultServer, creation: bool, progress: bool) -> None:
    text = '{"summary":"done","findings":["one"]}'
    server.body = EventBody([turn_event("created"), message(text), turn_event("completed"), idle()])
    agent: Any = {"model": "test-model", "text": {"verbosity": "low"}}
    if isinstance(sdk, AsyncOpenAI):
        stream = (
            (
                await sdk.beta.agents.sessions.create(
                    agent=agent,
                    environment={"type": "none"},
                    input="Question",
                    stream=True,
                    output_type=Report,
                )
            )
            if creation
            else sdk.beta.agents.sessions.stream("session_test", input="Question", output_type=Report)
        )
        async with stream:
            if progress:
                stream.with_result_collection()
                async for _ in stream:
                    pass
            result = await stream.get_final_result()
            assert await stream.get_final_result() is result
    else:
        stream = (
            sdk.beta.agents.sessions.create(
                agent=agent,
                environment={"type": "none"},
                input="Question",
                stream=True,
                output_type=Report,
            )
            if creation
            else sdk.beta.agents.sessions.stream("session_test", input="Question", output_type=Report)
        )
        with stream:
            if progress:
                stream.with_result_collection()
                for _ in stream:
                    pass
            result = stream.get_final_result()
            assert stream.get_final_result() is result
    assert result.output_parsed == Report(summary="done", findings=["one"])
    assert result.output_text == text
    assert result.turn_id == "turn_root"
    assert result.messages[0].output_text == text
    assert agent == {"model": "test-model", "text": {"verbosity": "low"}}
    bodies = [json.loads(request.content) for request in server.requests if request.method == "POST"]
    assert all("output_type" not in body for body in bodies)
    if creation:
        assert bodies[0]["agent"]["text"] == {"verbosity": "low", "format": agent_text_format(Report)}
    else:
        assert all("agent" not in body for body in bodies)


@pytest.mark.parametrize("text", ["not json", '{"summary": "missing findings"}'])
async def test_parse_error_preserves_successful_raw_result(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, text: str
) -> None:
    server.body = EventBody([turn_event("created"), message(text), turn_event("completed"), idle()])
    with pytest.raises(AgentOutputParseError) as caught:
        if isinstance(sdk, AsyncOpenAI):
            async with sdk.beta.agents.sessions.stream("session_test", input="Question", output_type=Report) as stream:
                await stream.get_final_result()
        else:
            with sdk.beta.agents.sessions.stream("session_test", input="Question", output_type=Report) as stream:
                stream.get_final_result()
    assert caught.value.result.output_text == text
    assert caught.value.result.turn.status == "completed"
    assert caught.value.result.output_parsed is None
    assert caught.value.__cause__ is not None
    assert server.body.closed


async def test_hosted_failure_not_parse_failure(sdk: OpenAI | AsyncOpenAI, server: ResultServer) -> None:
    server.body = EventBody([turn_event("created"), message("not json"), turn_event("failed"), idle()])
    with pytest.raises(AgentTurnResultError, match="failed"):
        if isinstance(sdk, AsyncOpenAI):
            async with sdk.beta.agents.sessions.stream("session_test", input="Question", output_type=Report) as stream:
                await stream.get_final_result()
        else:
            with sdk.beta.agents.sessions.stream("session_test", input="Question", output_type=Report) as stream:
                stream.get_final_result()


async def test_conflicting_format_rejected_before_request(sdk: OpenAI | AsyncOpenAI, server: ResultServer) -> None:
    with pytest.raises(ValueError, match="not both"):
        if isinstance(sdk, AsyncOpenAI):
            await sdk.beta.agents.sessions.create(
                agent={"model": "test", "text": {"format": {"type": "text"}}},
                environment={"type": "none"},
                input="Question",
                stream=True,
                output_type=Report,
            )
        else:
            sdk.beta.agents.sessions.create(
                agent={"model": "test", "text": {"format": {"type": "text"}}},
                environment={"type": "none"},
                input="Question",
                stream=True,
                output_type=Report,
            )
    assert server.requests == []


class Cat(BaseModel):
    kind: Literal["cat"]
    lives: int


class Dog(BaseModel):
    kind: Literal["dog"]
    name: str


class PetReport(BaseModel):
    pet: Cat | Dog = Field(discriminator="kind")


def test_discriminated_union_rejected() -> None:
    with pytest.raises(ValueError, match="oneOf"):
        agent_text_format(PetReport)


def test_fixed_tuple_rejected() -> None:
    class TupleReport(BaseModel):
        coordinates: tuple[int, int]

    with pytest.raises(ValueError, match="items"):
        agent_text_format(TupleReport)


class RecursiveReport(BaseModel):
    summary: str
    children: list[RecursiveReport]


def test_recursive_references_preserved() -> None:
    schema = agent_text_format(RecursiveReport)["schema"]
    assert schema["type"] == "object"
    assert "$defs" in schema or "definitions" in schema
