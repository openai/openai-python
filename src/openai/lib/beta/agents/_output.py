from __future__ import annotations

from typing import Any, cast
from typing_extensions import TypeVar

from pydantic import BaseModel

from ...._types import Omit
from ..._pydantic import is_basemodel_type, to_strict_json_schema
from ....types.beta.agent_text_param import AgentTextParam
from ....types.beta.text_format_param import TextFormatParamJSONSchema
from ....types.beta.agents.session_create_params import Agent


def agent_text_format(output_type: type[BaseModel]) -> TextFormatParamJSONSchema:
    """Beta: build the Agents JSON-schema format for an object-root Pydantic model."""
    if not is_basemodel_type(output_type):
        raise TypeError("Agents output_type must be a Pydantic BaseModel type")
    schema = to_strict_json_schema(output_type)
    if schema.get("type") != "object" or any(key in schema for key in ("oneOf", "anyOf", "allOf", "enum", "not")):
        raise ValueError("Agents output_type must describe an object root without schema composition")
    _validate_schema(schema)
    return {"type": "json_schema", "schema": schema}


def _validate_schema(schema: dict[str, Any]) -> None:
    # The strict-output adapter handles required fields, closed objects and refs.
    # Reject unsupported constructs rather than silently weakening their meaning.
    unsupported = {
        "unevaluatedProperties",
        "propertyNames",
        "minProperties",
        "maxProperties",
        "unevaluatedItems",
        "contains",
        "minContains",
        "maxContains",
        "uniqueItems",
        "allOf",
        "oneOf",
        "not",
        "dependentRequired",
        "dependentSchemas",
        "if",
        "then",
        "else",
        "x-guidance",
    }
    invalid = unsupported.intersection(schema)
    if invalid:
        raise ValueError(f"Unsupported Agents output schema keyword: {sorted(invalid)[0]}")
    if not any(key in schema for key in ("type", "$ref", "anyOf", "enum", "const")):
        raise ValueError("Agents output schema nodes require a concrete type, reference, enum or union")
    if "format" in schema and schema["format"] not in (
        "",
        "date-time",
        "time",
        "date",
        "duration",
        "email",
        "hostname",
        "ipv4",
        "ipv6",
        "uuid",
    ):
        raise ValueError("Unsupported Agents output schema string format")
    if schema.get("type") == "object" and schema.get("additionalProperties") is not False:
        raise ValueError("Agents output schemas require additionalProperties=false")
    if schema.get("type") == "array" and not isinstance(schema.get("items"), dict):
        raise ValueError("Agents output array schemas require an object items schema")
    for key in ("properties", "$defs", "definitions"):
        for child in schema.get(key, {}).values():
            _validate_schema(child)
    for key in ("items",):
        child = schema.get(key)
        if isinstance(child, dict):
            _validate_schema(cast(dict[str, Any], child))
    for key in ("anyOf", "oneOf", "prefixItems"):
        for child in schema.get(key, []):
            _validate_schema(child)


def with_output_schema(agent: Agent | Omit, output_type: type[BaseModel] | None) -> Agent | Omit:
    if output_type is None:
        return agent
    config = cast(Agent, {} if isinstance(agent, Omit) else dict(agent))
    text = cast(AgentTextParam, dict(config.get("text") or {}))
    if text.get("format") is not None:
        raise ValueError("Pass output_type or agent.text.format, not both")
    text["format"] = agent_text_format(output_type)
    config["text"] = text
    return config


ResponseT = TypeVar("ResponseT")


def bind_output_type(response: ResponseT, output_type: type[BaseModel] | None) -> ResponseT:
    from ._stream import AgentSessionEventStream, AsyncAgentSessionEventStream

    if isinstance(response, (AgentSessionEventStream, AsyncAgentSessionEventStream)):
        stream = cast("AgentSessionEventStream[Any] | AsyncAgentSessionEventStream[Any]", response)
        stream._collection.output_type = output_type
    return cast(ResponseT, response)
