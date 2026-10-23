# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["WebhookEndpoint"]


class WebhookEndpoint(BaseModel):
    id: str
    """The unique ID of the webhook endpoint."""

    created_at: int
    """The Unix timestamp when the endpoint was created."""

    event_types: List[str]
    """The event types that trigger deliveries to this endpoint."""

    name: str
    """The human-readable name of the endpoint."""

    object: Literal["webhook_endpoint"]
    """The object type, which is always webhook_endpoint."""

    signing_secret_hint: Optional[str] = None
    """A masked hint for the endpoint's signing secret."""

    url: str
    """The HTTPS URL that receives webhook deliveries."""

    updated_at: Optional[int] = None
    """The Unix timestamp of the last endpoint configuration or signing-secret change.

    Initialized at creation; tests and unchanged updates do not advance it.
    """
