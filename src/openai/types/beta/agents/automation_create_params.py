# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .automation_target_param import AutomationTargetParam
from .automation_metadata_param import AutomationMetadataParam

__all__ = ["AutomationCreateParams", "CreateAutomationParamsPeriodic", "CreateAutomationParamsOnce"]


class CreateAutomationParamsPeriodic(TypedDict, total=False):
    expression: Required[str]

    name: Required[str]

    target: Required[AutomationTargetParam]

    timezone: Required[str]

    type: Required[Literal["periodic"]]

    metadata: AutomationMetadataParam


class CreateAutomationParamsOnce(TypedDict, total=False):
    name: Required[str]

    run_at: Required[int]

    target: Required[AutomationTargetParam]

    type: Required[Literal["once"]]

    metadata: AutomationMetadataParam


AutomationCreateParams: TypeAlias = Union[CreateAutomationParamsPeriodic, CreateAutomationParamsOnce]
