# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

__all__ = ["WebhookCreateParams"]


class WebhookCreateParams(TypedDict, total=False):
    event_types: Required[
        List[
            Literal[
                "batch.completed",
                "batch.failed",
                "batch.expired",
                "batch.cancelled",
                "response.completed",
                "response.failed",
                "response.cancelled",
                "response.incomplete",
                "eval.run.succeeded",
                "eval.run.failed",
                "eval.run.canceled",
                "fine_tuning.job.succeeded",
                "fine_tuning.job.failed",
                "fine_tuning.job.cancelled",
                "realtime.call.incoming",
                "video.completed",
                "video.failed",
                "safety.alert.created",
            ]
        ]
    ]
    """The event types that trigger deliveries to this endpoint."""

    name: Required[str]
    """A human-readable name for the webhook endpoint."""

    url: Required[str]
    """The HTTPS URL that receives webhook deliveries."""
