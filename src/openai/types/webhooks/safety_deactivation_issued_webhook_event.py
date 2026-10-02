# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["SafetyDeactivationIssuedWebhookEvent", "Data"]


class Data(BaseModel):
    id: str
    """The safety case ID to pass to `GET /v1/safety/cases/{id}`."""


class SafetyDeactivationIssuedWebhookEvent(BaseModel):
    """
    Sent when a deactivation is issued for a safety identifier in your organization.
    """

    id: str
    """The unique ID of the webhook event."""

    created_at: int
    """The Unix timestamp in seconds when the event was created."""

    data: Data

    object: Literal["event"]
    """Always `event`."""

    type: Literal["safety.deactivation_issued"]
    """Always `safety.deactivation_issued`."""
