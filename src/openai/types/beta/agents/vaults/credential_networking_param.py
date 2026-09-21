# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ....._types import SequenceNotStr

__all__ = [
    "CredentialNetworkingParam",
    "VaultCredentialNetworkingParamUnrestricted",
    "VaultCredentialNetworkingParamLimited",
]


class VaultCredentialNetworkingParamUnrestricted(TypedDict, total=False):
    """Allows substitution for destinations permitted by the environment network policy.

    Requires `environment.network.access` to be `restricted`, with explicit `allowed_domains`.
    """

    type: Required[Literal["unrestricted"]]
    """The type of the object. Always `unrestricted`."""


class VaultCredentialNetworkingParamLimited(TypedDict, total=False):
    """Allows substitution only for the listed hosts.

    The environment network policy must also allow these hosts.
    """

    allowed_hosts: Required[SequenceNotStr[str]]
    """
    The 1 to 16 distinct allowed hostnames or IPv4 addresses, normalized to
    lowercase. Entries contain no scheme, path, port, or wildcard. IPv6 addresses
    are not supported.
    """

    type: Required[Literal["limited"]]
    """The type of the object. Always `limited`."""


CredentialNetworkingParam: TypeAlias = Union[
    VaultCredentialNetworkingParamUnrestricted, VaultCredentialNetworkingParamLimited
]
