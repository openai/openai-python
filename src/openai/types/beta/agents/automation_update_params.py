# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

from .automation_target_param import AutomationTargetParam

__all__ = ["AutomationUpdateParams"]


class AutomationUpdateParams(TypedDict, total=False):
    expression: str
    """Only accepted for periodic automations."""

    metadata: Dict[str, str]
    """Replaces all metadata; omit to leave unchanged."""

    name: str

    run_at: int
    """
    A future Unix timestamp in seconds; accepted only before a one-time scheduled
    invocation exists.
    """

    target: AutomationTargetParam
    """Replaces the complete target, retaining its type and any creator session."""

    timezone: str
    """Only accepted for periodic automations."""
