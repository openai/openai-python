from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from typing_extensions import TypeVar

import pydantic

from ._schema import model_schema
from ...._types import Omit
from ...._compat import PYDANTIC_V1
from ..._pydantic import is_basemodel_type, is_dataclass_like_type
from ....types.beta.agent_text_param import AgentTextParam
from ....types.beta.text_format_param import TextFormatParamJSONSchema
from ....types.beta.agents.session_create_params import Agent

if TYPE_CHECKING:
    from ...streaming.agents._dispatch import ToolDispatcher, AsyncToolDispatcher


def validate_output_type(output_type: type[Any]) -> None:
    if not is_basemodel_type(output_type) and not (is_dataclass_like_type(output_type) and not PYDANTIC_V1):
        raise TypeError("Agents output_type must be a Pydantic model or a Pydantic v2 dataclass")


def agent_text_format(output_type: type[Any]) -> TextFormatParamJSONSchema:
    """Beta: build the Agents JSON-schema format for a Pydantic model."""
    validate_output_type(output_type)
    if is_basemodel_type(output_type):
        schema = model_schema(output_type, strict=True)
    else:
        schema = model_schema(pydantic.TypeAdapter(output_type), strict=True)
    return {"type": "json_schema", "schema": schema}


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


def bind_output_type(
    response: ResponseT, output_type: type[Any] | None, dispatcher: ToolDispatcher | AsyncToolDispatcher | None = None
) -> ResponseT:
    from ._stream import AgentSessionEventStream, AsyncAgentSessionEventStream

    if isinstance(response, (AgentSessionEventStream, AsyncAgentSessionEventStream)):
        stream = cast("AgentSessionEventStream[Any] | AsyncAgentSessionEventStream[Any]", response)
        stream._collection.output_type = output_type
        if isinstance(stream, AgentSessionEventStream):
            stream._dispatcher = cast("ToolDispatcher | None", dispatcher)
        else:
            stream._dispatcher = cast("AsyncToolDispatcher | None", dispatcher)
    return cast(ResponseT, response)
