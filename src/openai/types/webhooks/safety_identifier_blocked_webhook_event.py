# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["SafetyIdentifierBlockedWebhookEvent", "Data"]


class Data(BaseModel):
    """Event data payload."""

    safety_category: str
    """The safety category that triggered the block, such as `bio` or `cyber`."""

    safety_identifier: str
    """The stable safety identifier associated with the blocked request."""

    model: Optional[str] = None
    """The model used for the blocked request, if available."""

    project_id: Optional[str] = None
    """The project associated with the blocked request, if available."""

    request_id: Optional[str] = None
    """The OpenAI request ID for the blocked request, if available."""


class SafetyIdentifierBlockedWebhookEvent(BaseModel):
    """Sent when a request associated with a safety identifier has been blocked."""

    id: str
    """The unique ID of the event."""

    created_at: int
    """The Unix timestamp (in seconds) of when the request was blocked."""

    data: Data
    """Event data payload."""

    type: Literal["safety_identifier.blocked"]
    """The type of the event. Always `safety_identifier.blocked`."""

    object: Optional[Literal["event"]] = None
    """The object of the event. Always `event`."""
