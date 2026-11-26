# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from ....._types import SequenceNotStr

__all__ = ["SpendLimitUpdateParams", "NotificationChannel"]


class SpendLimitUpdateParams(TypedDict, total=False):
    currency: Required[Literal["USD"]]
    """The currency for the threshold amount. Currently, only `USD` is supported."""

    interval: Required[Literal["month"]]
    """The time interval for evaluating spend against the threshold.

    Currently, only `month` is supported.
    """

    threshold_amount: Required[int]
    """The hard spend limit amount, in cents."""

    notification_channel: Optional[NotificationChannel]
    """Configure email notifications when the spend limit is reached.

    Leave this out to keep the current settings, or send null to reset to owner-only
    notifications.
    """


class NotificationChannel(TypedDict, total=False):
    """Configure email notifications when the spend limit is reached.

    Leave this out to keep the current settings, or send null to reset to owner-only notifications.
    """

    type: Required[Literal["email"]]

    recipients: SequenceNotStr[str]
    """Additional email recipients.

    Omit to keep them unchanged; send [] to clear them.
    """

    subject_prefix: Optional[str]
    """Email subject prefix.

    Omit to keep it unchanged; send null or an empty string to clear it.
    """
