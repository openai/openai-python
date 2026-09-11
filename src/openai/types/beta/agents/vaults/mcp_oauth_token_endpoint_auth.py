# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ....._utils import PropertyInfo
from ....._models import BaseModel

__all__ = [
    "McpOauthTokenEndpointAuth",
    "McpOauthTokenEndpointAuthResourceNone",
    "McpOauthTokenEndpointAuthResourceClientSecretBasic",
    "McpOauthTokenEndpointAuthResourceClientSecretPost",
]


class McpOauthTokenEndpointAuthResourceNone(BaseModel):
    """Sends the client ID without a client secret."""

    type: Literal["none"]
    """The type of the object. Always `none`."""


class McpOauthTokenEndpointAuthResourceClientSecretBasic(BaseModel):
    """Sends the client ID and secret using HTTP Basic authentication."""

    type: Literal["client_secret_basic"]
    """The type of the object. Always `client_secret_basic`."""


class McpOauthTokenEndpointAuthResourceClientSecretPost(BaseModel):
    """Sends the client ID and secret in the token request body."""

    type: Literal["client_secret_post"]
    """The type of the object. Always `client_secret_post`."""


McpOauthTokenEndpointAuth: TypeAlias = Annotated[
    Union[
        McpOauthTokenEndpointAuthResourceNone,
        McpOauthTokenEndpointAuthResourceClientSecretBasic,
        McpOauthTokenEndpointAuthResourceClientSecretPost,
    ],
    PropertyInfo(discriminator="type"),
]
