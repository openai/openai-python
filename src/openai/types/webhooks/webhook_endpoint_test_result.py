# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["WebhookEndpointTestResult"]


class WebhookEndpointTestResult(BaseModel):
    event_type: str
    """The event type sent in the test."""

    object: Literal["webhook_endpoint.test"]
    """The object type, which is always webhook_endpoint.test."""

    status_code: int
    """The HTTP status code returned by the endpoint."""

    success: Literal[True]
    """Whether the test request completed.

    Always true for returned results; use status_code to determine the endpoint
    response.
    """

    webhook_endpoint_id: str
    """The ID of the webhook endpoint that received the test."""
