from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Dict, Mapping, cast

from ._types import ToolOutput
from ...._exceptions import BadRequestError
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
