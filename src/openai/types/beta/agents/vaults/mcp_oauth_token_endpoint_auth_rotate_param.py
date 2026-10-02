# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "McpOauthTokenEndpointAuthRotateParam",
    "RotateMcpOauthTokenEndpointAuthParamClientSecretBasic",
    "RotateMcpOauthTokenEndpointAuthParamClientSecretPost",
]


class RotateMcpOauthTokenEndpointAuthParamClientSecretBasic(TypedDict, total=False):
    """Updates credentials sent using HTTP Basic authentication."""

    type: Required[Literal["client_secret_basic"]]
    """The type of the object. Always `client_secret_basic`."""

    client_secret: Optional[str]
    """The replacement OAuth client secret.

    Omit or pass `null` to keep the stored secret. This secret is never returned in
    resources.
    """


class RotateMcpOauthTokenEndpointAuthParamClientSecretPost(TypedDict, total=False):
    """Updates credentials sent in the token request body."""

    type: Required[Literal["client_secret_post"]]
    """The type of the object. Always `client_secret_post`."""

    client_secret: Optional[str]
    """The replacement OAuth client secret.

    Omit or pass `null` to keep the stored secret. This secret is never returned in
    resources.
    """


McpOauthTokenEndpointAuthRotateParam: TypeAlias = Union[
    RotateMcpOauthTokenEndpointAuthParamClientSecretBasic, RotateMcpOauthTokenEndpointAuthParamClientSecretPost
]
