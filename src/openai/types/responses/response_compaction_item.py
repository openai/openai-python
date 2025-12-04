# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseCompactionItem"]


class ResponseCompactionItem(BaseModel):
    id: str
    """The unique ID of the compaction item."""

    encrypted_content: str

    type: Literal["compaction"]
    """The type of the item. Always `compaction`."""

    created_by: Optional[str] = None
