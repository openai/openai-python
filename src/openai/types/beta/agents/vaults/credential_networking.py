# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import Literal, Annotated, TypeAlias

from ....._utils import PropertyInfo
from ....._models import BaseModel

__all__ = [
    "CredentialNetworking",
    "VaultCredentialNetworkingResourceUnrestricted",
    "VaultCredentialNetworkingResourceLimited",
]


class VaultCredentialNetworkingResourceUnrestricted(BaseModel):
    """Allows substitution for destinations permitted by the environment network policy.

    Requires `environment.network.access` to be `restricted`, with explicit `allowed_domains`.
    """

    type: Literal["unrestricted"]
    """The type of the object. Always `unrestricted`."""


class VaultCredentialNetworkingResourceLimited(BaseModel):
    """Allows substitution only for the listed hosts.

    The environment network policy must also allow these hosts.
    """

    allowed_hosts: List[str]
    """
    The 1 to 16 distinct allowed hostnames or IPv4 addresses, normalized to
    lowercase. Entries contain no scheme, path, port, or wildcard. IPv6 addresses
    are not supported.
    """

    type: Literal["limited"]
    """The type of the object. Always `limited`."""


CredentialNetworking: TypeAlias = Annotated[
    Union[VaultCredentialNetworkingResourceUnrestricted, VaultCredentialNetworkingResourceLimited],
    PropertyInfo(discriminator="type"),
]
