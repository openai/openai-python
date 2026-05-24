# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ProjectSpendAlert", "NotificationChannel"]


class NotificationChannel(BaseModel):
    """Email notification settings for a spend alert."""

    recipients: List[str]
    """Email addresses that receive the spend alert notification."""

    type: Literal["email"]
    """The notification channel type. Currently only `email` is supported."""

    subject_prefix: Optional[str] = None
    """Optional subject prefix for alert emails."""


class ProjectSpendAlert(BaseModel):
    """Represents a spend alert configured at the project level."""

    id: str
    """The identifier, which can be referenced in API endpoints."""

    currency: Literal["USD"]
    """The currency for the threshold amount."""

    interval: Literal["month"]
    """The time interval for evaluating spend against the threshold."""

    notification_channel: NotificationChannel
    """Email notification settings for a spend alert."""

    object: Literal["project.spend_alert"]
    """The object type, which is always `project.spend_alert`."""

    threshold_amount: int
    """The alert threshold amount, in cents."""
