# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["SpendAlertCreateParams", "NotificationChannel"]


class SpendAlertCreateParams(TypedDict, total=False):
    currency: Required[Literal["USD"]]
    """The currency for the threshold amount."""

    interval: Required[Literal["month"]]
    """The time interval for evaluating spend against the threshold."""

    notification_channel: Required[NotificationChannel]
    """Email notification settings for a spend alert."""

    threshold_amount: Required[int]
    """The alert threshold amount, in cents."""


class NotificationChannel(TypedDict, total=False):
    """Email notification settings for a spend alert."""

    recipients: Required[SequenceNotStr[str]]
    """Email addresses that receive the spend alert notification."""

    type: Required[Literal["email"]]
    """The notification channel type. Currently only `email` is supported."""

    subject_prefix: Optional[str]
    """Optional subject prefix for alert emails."""
