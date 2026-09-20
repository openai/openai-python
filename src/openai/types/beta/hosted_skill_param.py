# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .inline_capability_source_param import InlineCapabilitySourceParam

__all__ = ["HostedSkillParam", "HostedSkillParamSkillReference", "HostedSkillParamInline"]


class HostedSkillParamSkillReference(TypedDict, total=False):
    """References a skill uploaded through the Skills API."""

    skill_id: Required[str]
    """The ID of the skill created through `/v1/skills`."""

    type: Required[Literal["skill_reference"]]
    """The type of the object. Always `skill_reference`."""

    version: Optional[str]
    """
    The skill version, a positive integer or `latest`; omission selects the default.
    """


class HostedSkillParamInline(TypedDict, total=False):
    """Supplies a skill ZIP directly in the session request."""

    description: Required[str]
    """The skill description declared in `SKILL.md`."""

    name: Required[str]
    """The skill name declared in `SKILL.md`."""

    source: Required[InlineCapabilitySourceParam]
    """Provides ZIP bytes encoded with standard base64."""

    type: Required[Literal["inline"]]
    """The type of the object. Always `inline`."""


HostedSkillParam: TypeAlias = Union[HostedSkillParamSkillReference, HostedSkillParamInline]
