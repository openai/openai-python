# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .agent_function_call_output_param import AgentFunctionCallOutputParam
from .agent_session_input_message_param import AgentSessionInputMessageParam

__all__ = [
    "AgentSessionInputParam",
    "SessionInputParamAgentSessionInputMessage",
    "SessionInputParamAgentSessionInputCancel",
    "SessionInputParamAgentSessionInputToolResult",
]


class SessionInputParamAgentSessionInputMessage(TypedDict, total=False):
    """Adds one or more user messages and starts a turn."""

    input: Required[Iterable[AgentSessionInputMessageParam]]
    """The user messages to add to the session."""

    type: Required[Literal["agent.session.input.message"]]
    """The type of the object. Always `agent.session.input.message`."""


class SessionInputParamAgentSessionInputCancel(TypedDict, total=False):
    """Cancels the session's active turn."""

    type: Required[Literal["agent.session.input.cancel"]]
    """The type of the object. Always `agent.session.input.cancel`."""


class SessionInputParamAgentSessionInputToolResult(TypedDict, total=False):
    """Submits the result of a function call."""

    call_id: Required[str]
    """The ID of the function call."""

    success: Required[bool]
    """Whether the function call succeeded."""

    turn_id: Required[str]
    """The ID of the turn that requested the function call."""

    type: Required[Literal["agent.session.input.tool_result"]]
    """The type of the object. Always `agent.session.input.tool_result`."""

    error: Optional[str]
    """The error message when the call failed."""

    output: Optional[AgentFunctionCallOutputParam]
    """A function result represented as text or supported model-input content."""


AgentSessionInputParam: TypeAlias = Union[
    SessionInputParamAgentSessionInputMessage,
    SessionInputParamAgentSessionInputCancel,
    SessionInputParamAgentSessionInputToolResult,
]
