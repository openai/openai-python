# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict, List, Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = ["PersistedMcpTransport", "PersistedMcpTransportResourceHTTP", "PersistedMcpTransportResourceStdio"]


class PersistedMcpTransportResourceHTTP(BaseModel):
    """Connects to an MCP server over HTTP."""

    headers: Dict[str, str]
    """Non-secret HTTP headers sent to the MCP server."""

    server_url: str
    """The URL of the MCP server."""

    type: Literal["http"]
    """The type of the object. Always `http`."""


class PersistedMcpTransportResourceStdio(BaseModel):
    """Starts an MCP server as a local process."""

    args: List[str]
    """Arguments passed to the MCP server command."""

    command: str
    """The command used to start the MCP server."""

    cwd: str
    """The working directory used to start the MCP server."""

    env_vars: List[str]
    """Environment variable names inherited from the execution environment."""

    type: Literal["stdio"]
    """The type of the object. Always `stdio`."""


PersistedMcpTransport: TypeAlias = Annotated[
    Union[PersistedMcpTransportResourceHTTP, PersistedMcpTransportResourceStdio], PropertyInfo(discriminator="type")
]
