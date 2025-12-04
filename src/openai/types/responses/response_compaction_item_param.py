# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseCompactionItemParam"]


class ResponseCompactionItemParam(BaseModel):
    encrypted_content: str

    type: Literal["compaction"]
    """The type of the item. Always `compaction`."""

    id: Optional[str] = None
    """The ID of the compaction item."""
