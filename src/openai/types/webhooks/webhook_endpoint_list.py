# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .webhook_endpoint import WebhookEndpoint

__all__ = ["WebhookEndpointList"]


class WebhookEndpointList(BaseModel):
    data: List[WebhookEndpoint]
    """The webhook endpoints in this page."""

    first_id: Optional[str] = None
    """The ID of the first endpoint in this page."""

    has_more: bool
    """Whether more webhook endpoints are available."""

    last_id: Optional[str] = None
    """The ID of the last endpoint in this page."""

    object: Literal["list"]
    """The object type, which is always list."""
