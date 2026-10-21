# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_local_skill import BetaLocalSkill

__all__ = ["BetaLocalEnvironment"]


class BetaLocalEnvironment(BaseModel):
    type: Literal["local"]
    """Use a local computer environment."""

    skills: Optional[List[BetaLocalSkill]] = None
    """An optional list of skills."""
