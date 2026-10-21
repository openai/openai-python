# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .beta_inline_skill_source_param import BetaInlineSkillSourceParam

__all__ = ["BetaInlineSkillParam"]


class BetaInlineSkillParam(TypedDict, total=False):
    description: Required[str]
    """The description of the skill."""

    name: Required[str]
    """The name of the skill."""

    source: Required[BetaInlineSkillSourceParam]
    """Inline skill payload"""

    type: Required[Literal["inline"]]
    """Defines an inline skill for this request."""
