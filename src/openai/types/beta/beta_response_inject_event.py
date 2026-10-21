# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_response_input_item import BetaResponseInputItem

__all__ = ["BetaResponseInjectEvent"]


class BetaResponseInjectEvent(BaseModel):
    """
    Injects input items into an active response over a WebSocket connection.
    The items are validated and committed atomically. Currently, the server
    accepts client-owned tool outputs that resume a waiting agent.
    """

    input: List[BetaResponseInputItem]
    """Input items to inject into the active response."""

    response_id: str
    """The ID of the active response that should receive the input."""

    type: Literal["response.inject"]
    """The event discriminator. Always `response.inject`."""
