# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict
from typing_extensions import Literal

from ...._models import BaseModel
from .automation_target import AutomationTarget
from .automation_created_by import AutomationCreatedBy

__all__ = ["PeriodicAutomation"]


class PeriodicAutomation(BaseModel):
    """Fields shared by periodic and one-time automations."""

    id: str
    """The automation ID."""

    created_at: int
    """The creation time as a Unix timestamp in seconds."""

    created_by: AutomationCreatedBy
    """Service-recorded provenance; callers cannot supply this field."""

    expression: str
    """The cron expression determining scheduled occurrences."""

    metadata: Dict[str, str]
    """Custom string key-value pairs attached to the automation."""

    name: str
    """The automation's display name."""

    object: Literal["agent.automation"]
    """Always `agent.automation`."""

    status: Literal["active", "paused"]
    """Whether scheduled delivery is active or paused."""

    target: AutomationTarget
    """The session configuration or existing session receiving invocations."""

    timezone: str
    """The timezone used to interpret the expression."""

    type: Literal["periodic"]
    """The type of the object. Always `periodic`."""
