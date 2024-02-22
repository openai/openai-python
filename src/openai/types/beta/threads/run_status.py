# File generated from our OpenAPI spec by Stainless.

from typing_extensions import Literal

__all__ = ["RunStatus"]

RunStatus = Literal[
    "queued", "in_progress", "requires_action", "cancelling", "cancelled", "failed", "completed", "expired"
]
