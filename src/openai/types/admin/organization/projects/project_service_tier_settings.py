# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import Literal

from ....._models import BaseModel
from .project_optional_service_tier import ProjectOptionalServiceTier

__all__ = ["ProjectServiceTierSettings"]


class ProjectServiceTierSettings(BaseModel):
    default: Literal["standard", "fast", "scale"]
    """Default tier for requests that omit service_tier or use auto."""

    enabled_tiers: Union[Literal["all"], List[ProjectOptionalServiceTier]]
    """Additional service tiers enabled for this project.

    "all" includes future tiers. An empty array allows only Standard. Organization
    policy and eligibility still apply.
    """

    object: Literal["project.service_tier_settings"]
