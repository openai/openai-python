# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

from ..._types import SequenceNotStr
from .beta_container_network_policy_domain_secret_param import BetaContainerNetworkPolicyDomainSecretParam

__all__ = ["BetaContainerNetworkPolicyAllowlistParam"]


class BetaContainerNetworkPolicyAllowlistParam(TypedDict, total=False):
    allowed_domains: Required[SequenceNotStr[str]]
    """A list of allowed domains when type is `allowlist`."""

    type: Required[Literal["allowlist"]]
    """Allow outbound network access only to specified domains. Always `allowlist`."""

    domain_secrets: Iterable[BetaContainerNetworkPolicyDomainSecretParam]
    """Optional domain-scoped secrets for allowlisted domains."""
