# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["DeletedWebhookEndpoint"]


class DeletedWebhookEndpoint(BaseModel):
    id: str
    """The ID of the deleted webhook endpoint."""

    deleted: bool
    """Whether the endpoint was deleted."""

    object: Literal["webhook_endpoint.deleted"]
    """The object type, which is always webhook_endpoint.deleted."""
