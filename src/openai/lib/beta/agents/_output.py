from __future__ import annotations

from typing import Any, cast, get_origin
from typing_extensions import TypeVar

import pydantic

from ...._types import Omit
from ...._compat import PYDANTIC_V1
from ..._pydantic import resolve_ref, is_basemodel_type, to_strict_json_schema, is_dataclass_like_type
from ....types.beta.agent_text_param import AgentTextParam
from ....types.beta.text_format_param import TextFormatParamJSONSchema
from ....types.beta.agents.session_create_params import Agent


def validate_output_type(output_type: type[Any]) -> None:
    if not is_basemodel_type(output_type) and not (is_dataclass_like_type(output_type) and not PYDANTIC_V1):
        raise TypeError("Agents output_type must be a Pydantic model or a Pydantic v2 dataclass")


def agent_text_format(output_type: type[Any]) -> TextFormatParamJSONSchema:
    """Beta: build the Agents JSON-schema format for an object-root Pydantic model."""
    if is_basemodel_type(output_type):
        schema = to_strict_json_schema(output_type)
        if PYDANTIC_V1:
            _restore_v1_nullability(output_type, schema)
    elif is_dataclass_like_type(output_type) and not PYDANTIC_V1:
        schema = to_strict_json_schema(pydantic.TypeAdapter(output_type))
    else:
        raise TypeError("Agents output_type must be a Pydantic model or a Pydantic v2 dataclass")
    if schema.get("type") != "object" or any(key in schema for key in ("oneOf", "anyOf", "allOf", "enum", "not")):
        raise ValueError("Agents output_type must describe an object root without schema composition")
    _validate_schema(schema)
    return {"type": "json_schema", "schema": schema}


def _validate_schema(schema: dict[str, Any]) -> None:
    # The strict-output adapter handles required fields, closed objects and refs.
    # Reject unsupported constructs rather than silently weakening their meaning.
    unsupported = {
        "patternProperties",
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
    for value in [*schema.get("properties", {}), *schema.get("enum", [])]:
        if isinstance(value, (dict, list, tuple)):
            raise ValueError("Agents output schema enums require scalar values")
        if isinstance(value, str) and ('"' in value or "\n" in value):
            raise ValueError("Agents output schema enum strings and property names cannot contain quotes or newlines")
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
    if schema.get("type") == "object" and not isinstance(schema.get("properties"), dict):
        raise ValueError("Agents output object schemas require explicit properties; free-form mappings are unsupported")
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


def with_output_schema(agent: Agent | Omit, output_type: type[Any] | None) -> Agent | Omit:
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


def bind_output_type(response: ResponseT, output_type: type[Any] | None) -> ResponseT:
    from ._stream import AgentSessionEventStream, AsyncAgentSessionEventStream

    if isinstance(response, (AgentSessionEventStream, AsyncAgentSessionEventStream)):
        stream = cast("AgentSessionEventStream[Any] | AsyncAgentSessionEventStream[Any]", response)
        stream._collection.output_type = output_type
    return cast(ResponseT, response)


def _restore_v1_nullability(model: type[Any], schema: dict[str, Any]) -> None:
    # Pydantic v1 omits null from Optional field schemas. Restore it before
    # publishing a required-field strict schema, without changing model defaults.
    visited: set[tuple[type[Any], int]] = set()

    def model_fields(model_type: type[Any], node: dict[str, Any]) -> None:
        if "$ref" in node:
            node = cast(dict[str, Any], resolve_ref(root=schema, ref=node["$ref"]))
        key = (model_type, id(node))
        if key in visited:
            return
        visited.add(key)
        fields = cast(Any, model_type).__fields__
        if "__root__" in fields:
            field_schema(fields["__root__"], node)
        else:
            for field in fields.values():
                child = node.get("properties", {}).get(field.alias)
                if child is not None:
                    field_schema(field, child)

    def field_schema(field: Any, node: dict[str, Any]) -> None:
        if field.allow_none and field.type_ is not type(None):
            if "anyOf" in node:
                if not any(child.get("type") == "null" for child in node["anyOf"]):
                    node["anyOf"].append({"type": "null"})
            else:
                original = dict(node)
                node.clear()
                node["anyOf"] = [original, {"type": "null"}]
                node = original
        if node.get("type") == "array" and field.sub_fields and isinstance(node.get("items"), dict):
            field_schema(field.sub_fields[0], node["items"])
        elif "anyOf" in node and field.sub_fields:
            for child_field, child_schema in zip(field.sub_fields, node["anyOf"], strict=False):
                field_schema(child_field, child_schema)
        elif get_origin(field.type_) is None and isinstance(field.type_, type) and is_basemodel_type(field.type_):
            model_fields(field.type_, node)

    model_fields(model, schema)
