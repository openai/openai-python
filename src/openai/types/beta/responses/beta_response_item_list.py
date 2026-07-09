# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from ...._models import BaseModel
from ..beta_response_item import BetaResponseItem

__all__ = ["BetaResponseItemList"]


class BetaResponseItemList(BaseModel):
    """A list of Response items."""

    data: List[BetaResponseItem]
    """A list of items used to generate this response."""

    first_id: str
    """The ID of the first item in the list."""

    has_more: bool
    """Whether there are more items available."""

    last_id: str
    """The ID of the last item in the list."""

    object: Literal["list"]
    """The type of object returned, must be `list`."""
