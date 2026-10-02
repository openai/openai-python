# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["SafetyAlert"]


class SafetyAlert(BaseModel):
    id: str

    created_at: int

    error_type: Literal[
        "potentially_unintended_data_transfer",
        "potentially_unintended_data_access",
        "potentially_unintended_destructive_activity",
        "other",
    ]

    model: str

    object: Literal["safety.alert"]

    reason: Optional[str] = None
    """
    A customer-safe description derived from error_type, or null for zero data
    retention requests.
    """

    request_id: str

    request_paused: bool
    """Whether block registration succeeded for this request.

    This does not confirm that response execution stopped.
    """

    response_id: str
