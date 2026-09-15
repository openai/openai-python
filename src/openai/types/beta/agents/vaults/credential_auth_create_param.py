# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .mcp_oauth_token_endpoint_auth_create_param import McpOauthTokenEndpointAuthCreateParam

__all__ = [
    "CredentialAuthCreateParam",
    "CreateVaultCredentialAuthParamMcpOauth",
    "CreateVaultCredentialAuthParamMcpOauthRefresh",
    "CreateVaultCredentialAuthParamStaticBearer",
]


class CreateVaultCredentialAuthParamMcpOauthRefresh(TypedDict, total=False):
    """Configuration for refreshing the access token of an MCP OAuth credential."""

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
    """Configuration for refreshing the access token of an MCP OAuth credential."""


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


CredentialAuthCreateParam: TypeAlias = Union[
    CreateVaultCredentialAuthParamMcpOauth, CreateVaultCredentialAuthParamStaticBearer
]
