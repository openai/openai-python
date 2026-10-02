# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "McpOauthTokenEndpointAuthCreateParam",
    "CreateMcpOauthTokenEndpointAuthParamNone",
    "CreateMcpOauthTokenEndpointAuthParamClientSecretBasic",
    "CreateMcpOauthTokenEndpointAuthParamClientSecretPost",
]


class CreateMcpOauthTokenEndpointAuthParamNone(TypedDict, total=False):
    """Sends the client ID without a client secret."""

    type: Required[Literal["none"]]
    """The type of the object. Always `none`."""


class CreateMcpOauthTokenEndpointAuthParamClientSecretBasic(TypedDict, total=False):
    """Sends the client ID and secret using HTTP Basic authentication."""

    client_secret: Required[str]
    """The OAuth client secret to store. Never returned in credential resources."""

    type: Required[Literal["client_secret_basic"]]
    """The type of the object. Always `client_secret_basic`."""


class CreateMcpOauthTokenEndpointAuthParamClientSecretPost(TypedDict, total=False):
    """Sends the client ID and secret in the token request body."""

    client_secret: Required[str]
    """The OAuth client secret to store. Never returned in credential resources."""

    type: Required[Literal["client_secret_post"]]
    """The type of the object. Always `client_secret_post`."""


McpOauthTokenEndpointAuthCreateParam: TypeAlias = Union[
    CreateMcpOauthTokenEndpointAuthParamNone,
    CreateMcpOauthTokenEndpointAuthParamClientSecretBasic,
    CreateMcpOauthTokenEndpointAuthParamClientSecretPost,
]
