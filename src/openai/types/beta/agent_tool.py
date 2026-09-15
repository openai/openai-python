# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .mcp_transport import McpTransport

__all__ = [
    "AgentTool",
    "AgentToolResourceFunction",
    "AgentToolResourceProgrammaticToolCalling",
    "AgentToolResourceMcp",
    "AgentToolResourceWebSearch",
    "AgentToolResourceWebSearchLocation",
]


class AgentToolResourceFunction(BaseModel):
    """A function defined by the application."""

    defer_loading: bool
    """Whether the function is deferred and discovered through tool search."""

    description: str
    """A description of what the function does."""

    name: str
    """The name of the function."""

    parameters: Dict[str, object]
    """A JSON Schema object describing the function's arguments."""

    type: Literal["function"]
    """The type of the object. Always `function`."""


class AgentToolResourceProgrammaticToolCalling(BaseModel):
    """Enables calling tools from model-generated code."""

    enabled: bool
    """Whether tools can be called from model-generated code."""

    type: Literal["programmatic_tool_calling"]
    """The type of the object. Always `programmatic_tool_calling`."""


class AgentToolResourceMcp(BaseModel):
    """Tools provided by a remote MCP server."""

    allowed_tools: Optional[List[str]] = None
    """The MCP tools the agent may call."""

    connection_origin: Literal["service", "environment"]
    """Where outbound MCP HTTP connections originate."""

    credential_id: Optional[str] = None
    """The attached vault credential selected for this MCP server, if any.

    Optional when exactly one attached credential matches the server URL.
    """

    request_metadata: Dict[str, object]
    """Metadata included with requests to this MCP server."""

    required: bool
    """Whether this MCP server must initialize before the first turn."""

    server_label: str
    """A label used to identify the MCP server in tool calls."""

    transport: McpTransport
    """The transport used to connect to the MCP server."""

    type: Literal["mcp"]
    """The type of the object. Always `mcp`."""


class AgentToolResourceWebSearchLocation(BaseModel):
    """Approximate user location used to localize web search results."""

    city: Optional[str] = None
    """The city name."""

    country: Optional[str] = None
    """The two-letter ISO country code, such as `US`."""

    region: Optional[str] = None
    """The region or state name."""

    timezone: Optional[str] = None
    """The IANA timezone, such as `America/Los_Angeles`."""


class AgentToolResourceWebSearch(BaseModel):
    """Web search."""

    allowed_domains: Optional[List[str]] = None
    """Allowed search domains, or `null` when the search is unrestricted."""

    context_size: Literal["low", "medium", "high"]
    """The amount of search context made available to the model. Defaults to `medium`."""

    location: Optional[AgentToolResourceWebSearchLocation] = None
    """Approximate user location used to localize web search results."""

    mode: Literal["disabled", "cached", "live"]
    """The source used for web search results."""

    type: Literal["web_search"]
    """The type of the object. Always `web_search`."""


AgentTool: TypeAlias = Annotated[
    Union[
        AgentToolResourceFunction,
        AgentToolResourceProgrammaticToolCalling,
        AgentToolResourceMcp,
        AgentToolResourceWebSearch,
    ],
    PropertyInfo(discriminator="type"),
]
