# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .mcp_oauth_token_endpoint_auth_rotate_param import McpOauthTokenEndpointAuthRotateParam

__all__ = [
    "CredentialAuthRotateParam",
    "RotateVaultCredentialAuthParamMcpOauth",
    "RotateVaultCredentialAuthParamMcpOauthRefresh",
    "RotateVaultCredentialAuthParamStaticBearer",
    "RotateVaultCredentialAuthParamEnvironmentVariable",
]


class RotateVaultCredentialAuthParamMcpOauthRefresh(TypedDict, total=False):
    """Optional write-only refresh-token and client-secret updates."""

    refresh_token: Optional[str]
    """The replacement refresh token.

    Omit or pass `null` to keep the stored token. This secret is never returned in
    resources.
    """

    scope: Optional[str]
    """Replacement space-separated OAuth scopes for refresh requests.

    Omit to keep the scopes, or pass `null` to stop sending a scope parameter.
    """

    token_endpoint_auth: Optional[McpOauthTokenEndpointAuthRotateParam]
    """Client-secret updates for the existing token endpoint authentication method."""


class RotateVaultCredentialAuthParamMcpOauth(TypedDict, total=False):
    """Rotate an OAuth credential for an HTTPS MCP destination."""

    type: Required[Literal["mcp_oauth"]]
    """The type of the object. Always `mcp_oauth`."""

    access_token: Optional[str]
    """A write-only replacement OAuth access token."""

    expires_at: Optional[str]
    """The replacement expiry as an RFC 3339 timestamp, or `null` to clear it.

    Omitting this field preserves the expiry unless a new access token is supplied,
    in which case the expiry is cleared.
    """

    refresh: Optional[RotateVaultCredentialAuthParamMcpOauthRefresh]
    """Optional write-only refresh-token and client-secret updates."""


class RotateVaultCredentialAuthParamStaticBearer(TypedDict, total=False):
    """Replace the bearer token for the credential's MCP server."""

    token: Required[str]
    """The replacement bearer token.

    This secret is never returned in credential resources.
    """

    type: Required[Literal["static_bearer"]]
    """The type of the object. Always `static_bearer`."""


class RotateVaultCredentialAuthParamEnvironmentVariable(TypedDict, total=False):
    """Replace the secret for an OpenAI-hosted environment credential.

    The environment variable name and networking configuration remain unchanged.
    """

    secret_value: Required[str]
    """The write-only replacement secret.

    Never returned in credential resources or supplied directly to sandbox code.
    Must be nonempty and must not contain carriage returns, newlines, or NUL bytes.
    """

    type: Required[Literal["environment_variable"]]
    """The type of the object. Always `environment_variable`."""


CredentialAuthRotateParam: TypeAlias = Union[
    RotateVaultCredentialAuthParamMcpOauth,
    RotateVaultCredentialAuthParamStaticBearer,
    RotateVaultCredentialAuthParamEnvironmentVariable,
]
