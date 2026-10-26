# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ....._models import BaseModel
from .automation_invocation_source import AutomationInvocationSource

__all__ = ["AutomationInvocation", "Error"]


class Error(BaseModel):
    """The permanent delivery failure, or null when no failure occurred."""

    code: str
    """A machine-readable error code."""

    message: str
    """A public explanation of the delivery failure."""


class AutomationInvocation(BaseModel):
    """One attempted delivery by an automation."""

    id: str
    """The invocation ID."""

    automation_id: str
    """The automation that owns the invocation."""

    created_at: int
    """The creation time as a Unix timestamp in seconds."""

    error: Optional[Error] = None
    """The permanent delivery failure, or null when no failure occurred."""

    object: Literal["agent.automation.invocation"]
    """Always `agent.automation.invocation`."""

    scheduled_at: Optional[int] = None
    """
    The intended occurrence as a Unix timestamp in seconds, or null for manual runs.
    """

    session_id: Optional[str] = None
    """The target or newly created session ID, or null before one is available."""

    skip_reason: Optional[Literal["pending_delivery"]] = None
    """Why an occurrence was skipped, or null when it was not skipped."""

    source: AutomationInvocationSource
    """Whether the invocation was manual or scheduled."""

    status: Literal["queued", "completed", "failed", "skipped"]
    """Delivery status; completed does not mean the agent's work has finished."""
