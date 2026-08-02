# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["BetaContainerNetworkPolicyDisabledParam"]


class BetaContainerNetworkPolicyDisabledParam(TypedDict, total=False):
    type: Required[Literal["disabled"]]
    """Disable outbound network access. Always `disabled`."""
