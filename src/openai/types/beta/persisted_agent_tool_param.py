# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..._types import SequenceNotStr
from .persisted_mcp_transport_param import PersistedMcpTransportParam

__all__ = [
    "PersistedAgentToolParam",
    "PersistedAgentToolConfigParamFunction",
    "PersistedAgentToolConfigParamToolSearch",
    "PersistedAgentToolConfigParamProgrammaticToolCalling",
    "PersistedAgentToolConfigParamMcp",
    "PersistedAgentToolConfigParamWebSearch",
    "PersistedAgentToolConfigParamWebSearchLocation",
]


class PersistedAgentToolConfigParamFunction(TypedDict, total=False):
    """A function defined by the application."""

    description: Required[str]
    """A description of what the function does."""

    name: Required[str]
    """The name of the function."""

    parameters: Required[Dict[str, object]]
    """A JSON Schema object describing the function's arguments."""

    type: Required[Literal["function"]]
    """The type of the object. Always `function`."""

    defer_loading: bool
    """Whether this function is deferred and discovered through tool search.

    Defaults to `false`.
    """


class PersistedAgentToolConfigParamToolSearch(TypedDict, total=False):
    """Discovers deferred function tools and loads them into the model context."""

    type: Required[Literal["tool_search"]]
    """The type of the object. Always `tool_search`."""


class PersistedAgentToolConfigParamProgrammaticToolCalling(TypedDict, total=False):
    """Enables calling tools from model-generated code."""

    type: Required[Literal["programmatic_tool_calling"]]
    """The type of the object. Always `programmatic_tool_calling`."""

    enabled: bool
    """Whether tools can be called from model-generated code. Defaults to `true`."""


class PersistedAgentToolConfigParamMcp(TypedDict, total=False):
    """Tools provided by a remote MCP server without stored credentials."""

    server_label: Required[str]
    """A label used to identify the MCP server in tool calls."""

    transport: Required[PersistedMcpTransportParam]
    """The credential-free transport used to connect to the MCP server."""

    type: Required[Literal["mcp"]]
    """The type of the object. Always `mcp`."""

    allowed_tools: Optional[SequenceNotStr[str]]
    """The MCP tools the agent may call. All server tools are allowed when omitted."""

    connection_origin: Optional[Literal["service", "environment"]]
    """Where outbound MCP HTTP connections originate.

    - `service` - Uses the Managed Agents service network.
    - `environment` - Uses the session's execution environment.
    """

    credential_id: Optional[str]
    """The vault credential selected for this MCP server.

    Optional when exactly one attached credential matches the server URL.
    """

    request_metadata: Optional[Dict[str, object]]
    """Metadata included with requests to this MCP server."""

    required: bool
    """Whether this MCP server must initialize before the first turn.

    Defaults to `false`.
    """


class PersistedAgentToolConfigParamWebSearchLocation(TypedDict, total=False):
    """Approximate user location used to localize web search results."""

    city: Optional[str]
    """The city name."""

    country: Optional[str]
    """The two-letter ISO country code, such as `US`."""

    region: Optional[str]
    """The region or state name."""

    timezone: Optional[str]
    """The IANA timezone, such as `America/Los_Angeles`."""


class PersistedAgentToolConfigParamWebSearch(TypedDict, total=False):
    """Web search."""

    type: Required[Literal["web_search"]]
    """The type of the object. Always `web_search`."""

    allowed_domains: Optional[SequenceNotStr[str]]
    """Domains the search may include."""

    context_size: Optional[Literal["low", "medium", "high"]]
    """The amount of web search context made available to the model."""

    location: Optional[PersistedAgentToolConfigParamWebSearchLocation]
    """Approximate user location used to localize web search results."""

    mode: Optional[Literal["disabled", "cached", "live"]]
    """The source used for web search results.

    - `disabled` - Disables web search.
    - `cached` - Uses cached search results.
    - `live` - Searches the live web.
    """


PersistedAgentToolParam: TypeAlias = Union[
    PersistedAgentToolConfigParamFunction,
    PersistedAgentToolConfigParamToolSearch,
    PersistedAgentToolConfigParamProgrammaticToolCalling,
    PersistedAgentToolConfigParamMcp,
    PersistedAgentToolConfigParamWebSearch,
]
