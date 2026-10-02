# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseCompactionCompactingEvent"]


class ResponseCompactionCompactingEvent(BaseModel):
    """Emitted when new summary content is sampled for a compaction trigger.

    Contains no summary content.
    """

    item_id: str
    """The ID of the compaction output item."""

    output_index: int
    """The index of the compaction output item."""

    sequence_number: int
    """The sequence number of the event that was emitted."""

    type: Literal["response.compaction.compacting"]
    """The type of the event, always `response.compaction.compacting`."""
