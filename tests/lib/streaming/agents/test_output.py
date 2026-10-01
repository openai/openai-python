from __future__ import annotations

import json
import traceback
from typing import Any, cast
from typing_extensions import Literal

import httpx2
import pytest
import pydantic
from pydantic import Field, HttpUrl, BaseModel

from openai import OpenAI, AsyncOpenAI, BadRequestError
from openai._compat import PYDANTIC_V1
from openai.lib.beta.agents import (
    AgentTurnResultError,
    AgentOutputParseError,
    function_tool,
    agent_text_format,
    pydantic_function_tool,
)
from openai.lib._parsing._responses import type_to_text_format_param
from tests.lib.streaming.agents.test_results import ResultServer, server as server, message
from tests.lib.streaming.agents.test_streams import EventBody, sdk as sdk, call, idle, turn_event


def _assert_matches_responses(model: type[Any]) -> dict[str, Any]:
    schema = agent_text_format(model)["schema"]
    responses_format = type_to_text_format_param(model)
    assert responses_format["type"] == "json_schema"
    assert schema == responses_format["schema"]
    return schema


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


def test_mapping_schema_matches_responses_without_mutating_tools() -> None:
    class WithMap(BaseModel):
        value: dict[str, str]

    tool = pydantic_function_tool(WithMap, handler=lambda args: args.value)
    parameters = tool.definition["parameters"]
    schema = _assert_matches_responses(WithMap)
    assert schema["properties"]["value"]["additionalProperties"] == {"type": "string"}
    assert tool.definition["parameters"] == parameters
    assert tool({"value": {"label": "example"}}) == '{"label":"example"}'


def test_schema_normalizes_defaults_without_mutating_model() -> None:
    class WithDefault(BaseModel):
        value: str = "default"

    assert agent_text_format(WithDefault)["schema"]["required"] == ["value"]
    assert WithDefault().value == "default"


def test_unique_items_matches_responses() -> None:
    class WithSet(BaseModel):
        value: set[str]

    schema = _assert_matches_responses(WithSet)
    assert schema["properties"]["value"]["uniqueItems"] is True


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


@pytest.mark.parametrize(
    "text", ["SYNTHETIC_RESPONSE_CANARY not json", '{"summary": "SYNTHETIC_RESPONSE_CANARY missing findings"}']
)
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
    assert caught.value.__cause__ is None
    assert text not in "".join(traceback.format_exception(caught.value))
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


def test_discriminated_union_matches_responses() -> None:
    schema = _assert_matches_responses(PetReport)
    assert "oneOf" in schema["properties"]["pet"]


def test_fixed_tuple_matches_responses() -> None:
    class TupleReport(BaseModel):
        coordinates: tuple[int, int]

    _assert_matches_responses(TupleReport)


class RecursiveReport(BaseModel):
    summary: str
    children: list[RecursiveReport]


def test_recursive_references_preserved() -> None:
    schema = agent_text_format(RecursiveReport)["schema"]
    assert schema["type"] == "object"
    assert "$defs" in schema or "definitions" in schema


@pytest.mark.parametrize(
    "model",
    [
        type("AnyReport", (BaseModel,), {"__annotations__": {"value": Any}}),
        type("URLReport", (BaseModel,), {"__annotations__": {"url": HttpUrl}}),
    ],
)
def test_field_types_match_responses(model: type[BaseModel]) -> None:
    _assert_matches_responses(model)


class NullableChild(BaseModel):
    value: str | None = None


class NullableReport(BaseModel):
    optional: str | None = None
    child: NullableChild | None = None
    values: list[str | None]
    choice: int | str | None = None


def test_nullable_schema_matches_responses() -> None:
    schema = _assert_matches_responses(NullableReport)
    assert schema["required"] == ["optional", "child", "values", "choice"]
    assert NullableReport(values=[None]).optional is None


@pytest.mark.skipif(PYDANTIC_V1, reason="Pydantic dataclass output requires v2, matching Responses")
async def test_pydantic_dataclass_output(sdk: OpenAI | AsyncOpenAI, server: ResultServer) -> None:
    from pydantic.dataclasses import dataclass

    @dataclass
    class DataclassReport:
        summary: str

    server.body = EventBody([turn_event("created"), message('{"summary":"done"}'), turn_event("completed"), idle()])
    assert agent_text_format(DataclassReport)["schema"]["type"] == "object"
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream(
            "session_test", input="Question", output_type=DataclassReport
        ) as stream:
            result = await stream.get_final_result()
    else:
        with sdk.beta.agents.sessions.stream("session_test", input="Question", output_type=DataclassReport) as stream:
            result = stream.get_final_result()
    assert result.output_parsed == DataclassReport(summary="done")


class NullableTree(BaseModel):
    label: str
    parent: NullableTree | None = None
    children: list[NullableTree | None]


def test_nullable_recursive_refs_and_aliases_match_responses() -> None:
    _assert_matches_responses(NullableTree)

    class Aliased(BaseModel):
        count: int | None = Field(None, alias="optionalCount")

    alias_schema = _assert_matches_responses(Aliased)
    assert alias_schema["required"] == ["optionalCount"]


class LocalURLReport(BaseModel):
    url: HttpUrl


async def test_followup_output_type_only_selects_local_parser(sdk: OpenAI | AsyncOpenAI, server: ResultServer) -> None:
    server.body = EventBody(
        [turn_event("created"), message('{"url":"https://example.com/"}'), turn_event("completed"), idle()]
    )
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream(
            "session_test", input="Question", output_type=LocalURLReport
        ) as stream:
            result = await stream.get_final_result()
    else:
        with sdk.beta.agents.sessions.stream("session_test", input="Question", output_type=LocalURLReport) as stream:
            result = stream.get_final_result()
    assert result.output_parsed is not None
    assert str(result.output_parsed.url) == "https://example.com/"
    assert "output_type" not in str(server.inputs())
    _assert_matches_responses(LocalURLReport)


@pytest.mark.parametrize("value", ['say "hello"', "two\nlines", (1, 2)])
def test_enum_literals_match_responses(value: Any) -> None:
    from enum import Enum

    enum = Enum("Example", {"A": value, "B": "other"})
    model = type("EnumReport", (BaseModel,), {"__annotations__": {"value": enum}})
    _assert_matches_responses(model)


def test_property_literals_match_responses() -> None:
    class Aliased(BaseModel):
        value: str = Field(alias='a"b')

    _assert_matches_responses(Aliased)


def test_pattern_keyed_mapping_matches_responses() -> None:
    from pydantic import constr

    key_type = cast(Any, constr)(**{("regex" if PYDANTIC_V1 else "pattern"): "^item_"})
    model = type("PatternMapping", (BaseModel,), {"__annotations__": {"values": dict[key_type, str]}})
    schema = _assert_matches_responses(model)
    assert schema["properties"]["values"]["patternProperties"] == {"^item_": {"type": "string"}}


def test_bare_mapping_and_empty_fixed_object_match_responses() -> None:
    model = type("BareMapping", (BaseModel,), {"__annotations__": {"value": dict}})
    _assert_matches_responses(model)
    empty = type("EmptyReport", (BaseModel,), {})
    assert _assert_matches_responses(empty)["properties"] == {}


@pytest.mark.parametrize("value", ['say "hello"', "two\nlines"])
def test_single_literals_match_responses(value: Any) -> None:
    model = type("LiteralReport", (BaseModel,), {"__annotations__": {"value": Literal[value]}})
    _assert_matches_responses(model)


@pytest.mark.parametrize("explicit_model", [False, True])
async def test_typed_tools_and_output_keep_distinct_schema_policies(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, explicit_model: bool
) -> None:
    class Summary(BaseModel):
        summary: str = "default"

    seen: list[str] = []

    def summarize(summary: str = "default") -> Summary:
        seen.append(summary)
        return Summary(summary=summary)

    tool = (
        pydantic_function_tool(Summary, name="search", handler=lambda args: summarize(args.summary))
        if explicit_model
        else function_tool(summarize, name="search")
    )
    parameters = tool.definition["parameters"]
    assert "summary" not in cast(list[str], parameters.get("required", []))
    output_format = agent_text_format(Summary)
    assert output_format["schema"]["required"] == ["summary"]
    assert tool.definition["parameters"] == parameters
    later_tool = pydantic_function_tool(Summary, handler=lambda args: args)
    assert "summary" not in cast(list[str], later_tool.definition["parameters"].get("required", []))
    text = '{"summary":"default"}'
    server.body = EventBody([turn_event("created"), call({}), message(text), turn_event("completed"), idle()])
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream(
            "session_test", input="Summarize the document.", tool_handlers={tool.name: tool}, output_type=Summary
        ) as stream:
            result = await stream.get_final_result()
    else:
        with sdk.beta.agents.sessions.stream(
            "session_test", input="Summarize the document.", tool_handlers={tool.name: tool}, output_type=Summary
        ) as stream:
            result = stream.get_final_result()
    assert result.output_parsed == Summary(summary="default")
    assert seen == ["default"]
    assert server.inputs()[1]["output"] == text
    assert server.inputs()[1]["success"] is True


@pytest.mark.parametrize("schema_kind", ["mapping", "root", "format"])
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_schema_is_sent_and_api_rejection_is_preserved(schema_kind: str, asynchronous: bool) -> None:
    if schema_kind == "root":
        model = (
            pydantic.create_model("ListOutput", __root__=(list[str], ...))
            if PYDANTIC_V1
            else pydantic.RootModel[list[str]]
        )
    elif schema_kind == "mapping":
        model = pydantic.create_model("MappingOutput", value=(dict[str, str], ...))
    else:
        model = LocalURLReport
    expected_schema = _assert_matches_responses(model)
    requests: list[httpx2.Request] = []
    error = {"message": "This schema is not supported", "type": "invalid_request_error", "code": "invalid_json_schema"}

    def handle(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(400, json={"error": error})

    transport = httpx2.MockTransport(handle)
    with pytest.raises(BadRequestError) as caught:
        if asynchronous:
            async with AsyncOpenAI(
                api_key="synthetic", max_retries=0, http_client=httpx2.AsyncClient(transport=transport)
            ) as client:
                await client.beta.agents.sessions.create(
                    agent={"model": "test-model"},
                    environment={"type": "none"},
                    input="Summarize the document.",
                    stream=True,
                    output_type=model,
                )
        else:
            with OpenAI(api_key="synthetic", max_retries=0, http_client=httpx2.Client(transport=transport)) as client:
                client.beta.agents.sessions.create(
                    agent={"model": "test-model"},
                    environment={"type": "none"},
                    input="Summarize the document.",
                    stream=True,
                    output_type=model,
                )
    assert caught.value.status_code == 400
    assert caught.value.body == error
    assert len(requests) == 1
    body = json.loads(requests[0].content)
    assert body["agent"]["text"]["format"] == {"type": "json_schema", "schema": expected_schema}
    assert "output_type" not in body


@pytest.mark.parametrize("model", [str, dict, object])
async def test_invalid_output_model_rejected_before_request(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, model: type[Any]
) -> None:
    with pytest.raises(TypeError, match="Pydantic"):
        if isinstance(sdk, AsyncOpenAI):
            await sdk.beta.agents.sessions.create(
                agent={"model": "test-model"},
                environment={"type": "none"},
                input="Question",
                stream=True,
                output_type=model,
            )
        else:
            sdk.beta.agents.sessions.create(
                agent={"model": "test-model"},
                environment={"type": "none"},
                input="Question",
                stream=True,
                output_type=model,
            )
    assert server.requests == []


async def test_root_model_result_uses_native_parser(sdk: OpenAI | AsyncOpenAI, server: ResultServer) -> None:
    model = (
        pydantic.create_model("ListOutput", __root__=(list[str], ...)) if PYDANTIC_V1 else pydantic.RootModel[list[str]]
    )
    server.body = EventBody([turn_event("created"), message('["one"]'), turn_event("completed"), idle()])
    if isinstance(sdk, AsyncOpenAI):
        async with sdk.beta.agents.sessions.stream("session_test", input="Question", output_type=model) as stream:
            result = await stream.get_final_result()
    else:
        with sdk.beta.agents.sessions.stream("session_test", input="Question", output_type=model) as stream:
            result = stream.get_final_result()
    assert getattr(result.output_parsed, "__root__" if PYDANTIC_V1 else "root") == ["one"]


def test_inherited_schema_conversion_errors_are_preserved() -> None:
    extra: dict[str, Any] = {"$ref": "https://example.com/schema.json"}
    config = (
        type("Config", (), {"schema_extra": extra}) if PYDANTIC_V1 else pydantic.ConfigDict(json_schema_extra=extra)
    )
    model = pydantic.create_model("ExternalReference", __config__=cast(Any, config), value=(str, ...))
    for convert in (agent_text_format, type_to_text_format_param):
        with pytest.raises(ValueError, match="Unexpected.*ref format"):
            convert(model)


@pytest.mark.parametrize("typed", [False, True], ids=["parse", "getter"])
@pytest.mark.parametrize("case", ["messages", "parts", "invalid_later", "invalid_first", "empty", "split_json"])
async def test_final_text_parts_are_parsed_independently(
    sdk: OpenAI | AsyncOpenAI, server: ResultServer, typed: bool, case: str
) -> None:
    first = '{"summary":"first","findings":["one"]}'
    second = '{"summary":"second","findings":["two"]}'
    if case == "messages":
        parts = [[first], [second]]
    elif case == "parts":
        parts = [[first, second]]
    elif case == "invalid_later":
        parts = [[first], ["invalid JSON"]]
    elif case == "invalid_first":
        parts = [["invalid JSON"], [second]]
    elif case == "split_json":
        parts = [[first[:10], first[10:]]]
    else:
        parts = []
    messages: list[dict[str, Any]] = []
    for index, texts in enumerate(parts):
        event = message(item_id=f"message_{index}", index=index)
        event["item"]["content"] = [{"type": "output_text", "text": text, "annotations": []} for text in texts]
        messages.append(event)
    server.body = EventBody([turn_event("created"), *messages, turn_event("completed"), idle()])
    should_fail = case not in ("messages", "parts")
    try:
        if isinstance(sdk, AsyncOpenAI):
            async with sdk.beta.agents.sessions.stream(
                "session_test", input="Question", output_type=Report if typed else None
            ) as stream:
                result = await stream.get_final_result()
        else:
            with sdk.beta.agents.sessions.stream(
                "session_test", input="Question", output_type=Report if typed else None
            ) as stream:
                result = stream.get_final_result()
        if not typed:
            result = result.parse(Report)
    except AgentOutputParseError as exc:
        assert should_fail
        raw = exc.result
        assert raw.output_parsed is None
    else:
        assert not should_fail
        assert result.output_parsed == Report(summary="first", findings=["one"])
        raw = result
    assert raw.output_text == "".join(text for texts in parts for text in texts)
    assert [
        [content.text for content in item.content if content.type == "output_text"] for item in raw.messages
    ] == parts
