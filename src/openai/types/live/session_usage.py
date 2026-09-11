# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["SessionUsage"]


class SessionUsage(BaseModel):
    """Cumulative audio duration for a Live session.

    Values are totals for the session, not increments to sum across usage events.
    """

    seconds: float
    """The cumulative Live audio duration in seconds.

    Do not sum this value across usage events.
    """
