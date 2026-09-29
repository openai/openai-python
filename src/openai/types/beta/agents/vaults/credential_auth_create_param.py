# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .credential_networking_param import CredentialNetworkingParam
from .mcp_oauth_token_endpoint_auth_create_param import McpOauthTokenEndpointAuthCreateParam

__all__ = [
    "CredentialAuthCreateParam",
    "CreateVaultCredentialAuthParamMcpOauth",
    "CreateVaultCredentialAuthParamMcpOauthRefresh",
    "CreateVaultCredentialAuthParamStaticBearer",
    "CreateVaultCredentialAuthParamEnvironmentVariable",
]


class CreateVaultCredentialAuthParamMcpOauthRefresh(TypedDict, total=False):
    """Optional refresh configuration for an HTTPS OAuth token endpoint."""

    client_id: Required[str]
    """The OAuth client ID used when requesting a new access token."""

    refresh_token: Required[str]
    """The refresh token to store.

    This secret is never returned in credential resources.
    """

    token_endpoint: Required[str]
    """
    The HTTPS OAuth token endpoint used to exchange the refresh token for a new
    access token.
    """

    token_endpoint_auth: Required[McpOauthTokenEndpointAuthCreateParam]
    """How the OAuth client authenticates to the token endpoint."""

    resource: Optional[str]
    """
    The resource URI to send to the OAuth token endpoint during refresh, if
    required.
    """

    scope: Optional[str]
    """Space-separated OAuth scopes to request during refresh, if required."""


class CreateVaultCredentialAuthParamMcpOauth(TypedDict, total=False):
    """An OAuth credential for an HTTPS MCP destination."""

    access_token: Required[str]
    """A write-only OAuth access token; never returned by credential resources."""

    mcp_server_url: Required[str]
    """The HTTPS MCP server URL authorized by this credential."""

    type: Required[Literal["mcp_oauth"]]
    """The type of the object. Always `mcp_oauth`."""

    expires_at: Optional[str]
    """When the OAuth access token expires, as an RFC 3339 timestamp, if known."""

    refresh: Optional[CreateVaultCredentialAuthParamMcpOauthRefresh]
    """Optional refresh configuration for an HTTPS OAuth token endpoint."""


class CreateVaultCredentialAuthParamStaticBearer(TypedDict, total=False):
    """A bearer token for an MCP server, without automatic OAuth refresh."""

    token: Required[str]
    """The bearer token to store.

    This secret is never returned in credential resources.
    """

    mcp_server_url: Required[str]
    """The HTTPS MCP server URL authorized by this credential."""

    type: Required[Literal["static_bearer"]]
    """The type of the object. Always `static_bearer`."""


class CreateVaultCredentialAuthParamEnvironmentVariable(TypedDict, total=False):
    """An HTTP credential for OpenAI-hosted environments only.

    The sandbox receives an environment variable containing a placeholder, not the secret. Use the placeholder unchanged in outgoing requests. The egress proxy replaces the placeholder with the secret for allowed HTTPS destinations on ports 443 and 8443. Sandbox code cannot read the real secret or use it for local computation, such as signing a request.
    """

    networking: Required[CredentialNetworkingParam]
    """The destinations where the proxy can substitute this secret.

    The environment network policy must also allow them.
    """

    secret_name: Required[str]
    """
    The environment variable name that receives the placeholder, such as
    `SERVICE_API_KEY`. Use ASCII letters, digits, and underscores, starting with a
    letter or underscore. Names starting with `CODEX_` and managed proxy or
    certificate variable names are reserved.
    """

    secret_value: Required[str]
    """The write-only secret to store.

    Never returned in credential resources or supplied directly to sandbox code.
    Must be nonempty and must not contain carriage returns, newlines, or NUL bytes.
    """

    type: Required[Literal["environment_variable"]]
    """The type of the object. Always `environment_variable`."""


CredentialAuthCreateParam: TypeAlias = Union[
    CreateVaultCredentialAuthParamMcpOauth,
    CreateVaultCredentialAuthParamStaticBearer,
    CreateVaultCredentialAuthParamEnvironmentVariable,
]
