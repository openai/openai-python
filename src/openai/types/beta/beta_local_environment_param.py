# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

from .beta_local_skill_param import BetaLocalSkillParam

__all__ = ["BetaLocalEnvironmentParam"]


class BetaLocalEnvironmentParam(TypedDict, total=False):
    type: Required[Literal["local"]]
    """Use a local computer environment."""

    skills: Iterable[BetaLocalSkillParam]
    """An optional list of skills."""
