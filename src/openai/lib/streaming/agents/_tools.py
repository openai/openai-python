from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Dict, Mapping, cast

from ._types import ToolOutput, ToolHandler, AsyncToolHandler
from ...._utils import maybe_transform
from ...._exceptions import BadRequestError
from ...._utils._json import openapi_dumps
from ...beta.agents._tool_error import AgentToolError, ToolErrorStage
from ....types.beta.agent_function_call_item import AgentFunctionCallItem
from ....types.beta.agent_session_input_param import SessionInputParamAgentSessionInputToolResult
from ....types.beta.agent_function_call_output_param import AgentFunctionCallOutputParam


def arguments(call: AgentFunctionCallItem) -> Dict[str, Any]:
    value = json.loads(call.arguments) if isinstance(call.arguments, str) else deepcopy(call.arguments)
    if not isinstance(value, dict):
        raise ValueError("Function arguments must be a JSON object")
    return cast(Dict[str, Any], value)


def result_event(call: AgentFunctionCallItem, output: ToolOutput) -> SessionInputParamAgentSessionInputToolResult:
    if isinstance(output, Mapping):
        output = json.dumps(dict(output), separators=(",", ":"))
    # Materialize iterators here so serialization failures produce a failed tool result.
    if output is not None and not isinstance(output, str):
        output = list(output)
    # Use the same content normalization as events.create before checking JSON encoding.
    output = maybe_transform(output, AgentFunctionCallOutputParam)
    openapi_dumps(output)
    return {
        "type": "agent.session.input.tool_result",
        "turn_id": call.turn_id,
        "call_id": call.call_id,
        "success": True,
        "output": cast(AgentFunctionCallOutputParam, output) if output is not None else None,
    }


def failed_event(call: AgentFunctionCallItem) -> SessionInputParamAgentSessionInputToolResult:
    return {
        "type": "agent.session.input.tool_result",
        "turn_id": call.turn_id,
        "call_id": call.call_id,
        "success": False,
        # Do not send exception text, which may include application secrets, to the model.
        "error": "Tool handler failed.",
    }


def is_pending_call_race(error: BadRequestError, call_id: str) -> bool:
    # The item event can arrive before the server registers the pending call.
    # Match only this known registration race; other HTTP failures propagate.
    raw_body = error.body
    body = cast(Dict[str, object], raw_body) if isinstance(raw_body, dict) else {}
    return (
        body.get("code") == "invalid_request_error" and body.get("message") == f"Unknown pending tool call: {call_id}"
    )


class ToolInvocation:
    def __init__(self, session_id: str, call: AgentFunctionCallItem) -> None:
        self.session_id = session_id
        self.call = call
        self.stage: ToolErrorStage = "arguments"

    def set_stage(self, stage: ToolErrorStage) -> None:
        self.stage = stage

    def invoke(self, handler: ToolHandler | AsyncToolHandler) -> Any:
        from ...beta.agents._tools import FunctionTool

        parsed = arguments(self.call)
        self.stage = "execution"
        if isinstance(handler, FunctionTool):
            tool = cast(FunctionTool[Any], handler)
            tool_type = cast(type[FunctionTool[Any]], FunctionTool)
            if type(tool).__call__ is tool_type.__call__:
                return tool._call(parsed, self.set_stage)
        return cast(AsyncToolHandler, handler)(parsed)

    def failure(self, error: Exception) -> AgentToolError:
        return AgentToolError(
            error=error,
            tool_name=self.call.name,
            session_id=self.session_id,
            turn_id=self.call.turn_id,
            call_id=self.call.call_id,
            stage=self.stage,
        )
