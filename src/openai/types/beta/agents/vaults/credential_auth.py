# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ....._utils import PropertyInfo
from ....._models import BaseModel
from .credential_networking import CredentialNetworking
from .mcp_oauth_token_endpoint_auth import McpOauthTokenEndpointAuth

__all__ = [
    "CredentialAuth",
    "VaultCredentialAuthResourceMcpOauth",
    "VaultCredentialAuthResourceMcpOauthRefresh",
    "VaultCredentialAuthResourceStaticBearer",
    "VaultCredentialAuthResourceEnvironmentVariable",
]


class VaultCredentialAuthResourceMcpOauthRefresh(BaseModel):
    """Public refresh metadata without refresh tokens or OAuth client secrets."""

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
    """Public refresh metadata without refresh tokens or OAuth client secrets."""

    type: Literal["mcp_oauth"]
    """The type of the object. Always `mcp_oauth`."""


class VaultCredentialAuthResourceStaticBearer(BaseModel):
    """Metadata for a bearer-token credential, without automatic OAuth refresh."""

    mcp_server_url: str
    """The HTTPS MCP server URL authorized by this credential."""

    type: Literal["static_bearer"]
    """The type of the object. Always `static_bearer`."""


class VaultCredentialAuthResourceEnvironmentVariable(BaseModel):
    """Metadata for an HTTP credential used only in OpenAI-hosted environments.

    Sandbox code receives a placeholder. The proxy substitutes the secret for allowed HTTPS destinations on ports 443 and 8443. The real secret is not available to sandbox code for local computation and is never returned in this resource.
    """

    networking: CredentialNetworking
    """
    The destinations where the proxy can substitute the secret, subject to the
    environment network policy.
    """

    secret_name: str
    """The environment variable name that receives the placeholder in the sandbox."""

    type: Literal["environment_variable"]
    """The type of the object. Always `environment_variable`."""


CredentialAuth: TypeAlias = Annotated[
    Union[
        VaultCredentialAuthResourceMcpOauth,
        VaultCredentialAuthResourceStaticBearer,
        VaultCredentialAuthResourceEnvironmentVariable,
    ],
    PropertyInfo(discriminator="type"),
]
