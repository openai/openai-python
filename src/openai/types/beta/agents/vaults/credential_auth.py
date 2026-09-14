# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ....._utils import PropertyInfo
from ....._models import BaseModel
from .mcp_oauth_token_endpoint_auth import McpOauthTokenEndpointAuth

__all__ = [
    "CredentialAuth",
    "VaultCredentialAuthResourceMcpOauth",
    "VaultCredentialAuthResourceMcpOauthRefresh",
    "VaultCredentialAuthResourceStaticBearer",
]


class VaultCredentialAuthResourceMcpOauthRefresh(BaseModel):
    """
    Configuration used to refresh an MCP OAuth access token, excluding secret values.
    """

    client_id: str
    """The OAuth client ID used when requesting a new access token."""

    resource: Optional[str] = None
    """
    The resource URI sent to the OAuth token endpoint during refresh, if configured.
    """

    scope: Optional[str] = None
    """Space-separated OAuth scopes requested during refresh, if configured."""

    token_endpoint: str
    """The HTTPS OAuth token endpoint used for refresh."""

    token_endpoint_auth: McpOauthTokenEndpointAuth
    """
    How the OAuth client authenticates to the token endpoint, excluding its client
    secret.
    """


class VaultCredentialAuthResourceMcpOauth(BaseModel):
    """
    Public metadata for an OAuth credential; tokens and client secrets are never returned.
    """

    expires_at: Optional[str] = None
    """When the OAuth access token expires, as an RFC 3339 timestamp, if known."""

    mcp_server_url: str
    """The HTTPS MCP server URL authorized by this credential."""

    refresh: Optional[VaultCredentialAuthResourceMcpOauthRefresh] = None
    """
    Configuration used to refresh an MCP OAuth access token, excluding secret
    values.
    """

    type: Literal["mcp_oauth"]
    """The type of the object. Always `mcp_oauth`."""


class VaultCredentialAuthResourceStaticBearer(BaseModel):
    """Metadata for a bearer-token credential, without automatic OAuth refresh."""

    mcp_server_url: str
    """The HTTPS MCP server URL authorized by this credential."""

    type: Literal["static_bearer"]
    """The type of the object. Always `static_bearer`."""


CredentialAuth: TypeAlias = Annotated[
    Union[VaultCredentialAuthResourceMcpOauth, VaultCredentialAuthResourceStaticBearer],
    PropertyInfo(discriminator="type"),
]
