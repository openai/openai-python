# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["SafetyOrgAlertCreatedWebhookEvent", "Data"]


class Data(BaseModel):
    id: str
    """The safety alert ID to pass to `GET /v1/safety/alerts/{id}`."""


class SafetyOrgAlertCreatedWebhookEvent(BaseModel):
    """Sent when an approved safety alert is available for an enterprise workspace."""

    id: str
    """The unique ID of the webhook event."""

    created_at: int
    """The Unix timestamp in seconds when the event was created."""

    data: Data

    object: Literal["event"]
    """Always `event`."""

    type: Literal["safety.org_alert.created"]
    """Always `safety.org_alert.created`."""
