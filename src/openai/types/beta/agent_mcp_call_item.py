# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .agent_function_call_status import AgentFunctionCallStatus

__all__ = ["AgentMcpCallItem"]


class AgentMcpCallItem(BaseModel):
    """A call to a tool on an MCP server."""

    id: str
    """The ID of the MCP call item."""

    arguments: object
    """The arguments passed to the MCP tool."""

    error: object
    """The error returned by the MCP tool, if any."""

    name: str
    """The name of the MCP tool."""

    output: object
    """The output returned by the MCP tool, if any."""

    server_label: str
    """The label of the MCP server."""

    status: AgentFunctionCallStatus
    """The status of the MCP tool call."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["mcp_call"]
    """The item type. Always `mcp_call`."""
