# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..._types import SequenceNotStr

__all__ = ["McpTransportParam", "McpTransportConfigParamHTTP", "McpTransportConfigParamStdio"]


class McpTransportConfigParamHTTP(TypedDict, total=False):
    """Connects to an MCP server over HTTP."""

    server_url: Required[str]
    """The URL of the MCP server."""

    type: Required[Literal["http"]]
    """The type of the object. Always `http`."""

    authorization: Optional[str]
    """The authorization value sent to the MCP server, if any."""

    headers: Optional[Dict[str, str]]
    """Additional HTTP headers sent to the MCP server."""


class McpTransportConfigParamStdio(TypedDict, total=False):
    """Starts an MCP server as a local process."""

    command: Required[str]
    """The command used to start the MCP server."""

    cwd: Required[str]
    """The working directory used to start the MCP server."""

    type: Required[Literal["stdio"]]
    """The type of the object. Always `stdio`."""

    args: Optional[SequenceNotStr[str]]
    """Arguments passed to the MCP server command."""

    env: Optional[Dict[str, str]]
    """Environment variables set for the MCP server process."""

    env_vars: Optional[SequenceNotStr[str]]
    """Environment variable names to inherit from the selected execution environment."""


McpTransportParam: TypeAlias = Union[McpTransportConfigParamHTTP, McpTransportConfigParamStdio]
