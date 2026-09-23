# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["WebhookEventTypeList"]


class WebhookEventTypeList(BaseModel):
    data: List[str]
    """The webhook event types available to the authenticated project."""

    object: Literal["list"]
    """The object type, which is always list."""
