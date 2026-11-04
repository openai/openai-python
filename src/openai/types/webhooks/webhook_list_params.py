# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["WebhookListParams"]


class WebhookListParams(TypedDict, total=False):
    after: Optional[str]
    """ID of the last webhook endpoint from the previous page."""

    limit: int
    """Maximum number of webhook endpoints to return. Defaults to 20."""
