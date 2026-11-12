# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, TypedDict

from .project_optional_service_tier import ProjectOptionalServiceTier

__all__ = ["ServiceTierSettingUpdateParams"]


class ServiceTierSettingUpdateParams(TypedDict, total=False):
    default: Literal["standard", "fast", "scale"]
    """Default tier for requests that omit service_tier or use auto."""

    enabled_tiers: Union[Literal["all"], Iterable[ProjectOptionalServiceTier]]
    """Additional service tiers enabled for this project.

    "all" includes future tiers. An empty array allows only Standard. Organization
    policy and eligibility still apply.
    """
