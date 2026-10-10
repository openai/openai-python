# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["WebhookUpdateParams"]


class WebhookUpdateParams(TypedDict, total=False):
    event_types: List[
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
            "agent.environment.ready",
            "agent.environment.failed",
            "agent.session.created",
            "agent.session.action_required",
            "agent.session.in_progress",
            "agent.session.idle",
            "agent.session.failed",
            "safety.alert.created",
            "agent.environment.suspended",
            "agent.environment.expired",
        ]
    ]
    """The complete set of event types that should trigger deliveries."""

    name: str
    """A new human-readable name for the webhook endpoint."""

    url: str
    """A new HTTPS URL that receives webhook deliveries."""
