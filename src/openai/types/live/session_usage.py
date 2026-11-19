# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["SessionUsage"]


class SessionUsage(BaseModel):
    """Cumulative billable duration for a Live session.

    Eligible WebRTC sessions also report the active and paused breakdown. Do not sum values across usage events.
    """

    seconds: float
    """The cumulative billable duration in whole seconds.

    When present, the active and paused breakdown adds up to this total.
    """

    active_seconds: Optional[int] = None
    """
    The remaining billable seconds attributed to active audio and any unused prepaid
    duration.
    """

    paused_seconds: Optional[int] = None
    """
    Billable time attributed to paused inference at the configured rate, rounded
    down to whole seconds.
    """
