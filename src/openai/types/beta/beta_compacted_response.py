# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_response_usage import BetaResponseUsage
from .beta_response_output_item import BetaResponseOutputItem

__all__ = ["BetaCompactedResponse"]


class BetaCompactedResponse(BaseModel):
    id: str
    """The unique identifier for the compacted response."""

    created_at: int
    """Unix timestamp (in seconds) when the compacted conversation was created."""

    object: Literal["response.compaction"]
    """The object type. Always `response.compaction`."""

    output: List[BetaResponseOutputItem]
    """The compacted list of output items.

    This is a list of all user messages, followed by a single compaction item.
    """

    usage: BetaResponseUsage
    """
    Token accounting for the compaction pass, including cached, reasoning, and total
    tokens.
    """
