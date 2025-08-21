# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import TypedDict

from ..shared_params.metadata import Metadata
from ..responses.response_input_item_param import ResponseInputItemParam

__all__ = ["ConversationCreateParams"]


class ConversationCreateParams(TypedDict, total=False):
    items: Optional[Iterable[ResponseInputItemParam]]
    """
    Initial items to include in the conversation context. You may add up to 20 items
    at a time.
    """

    metadata: Optional[Metadata]
    """Set of 16 key-value pairs that can be attached to an object.

    Useful for storing additional information about the object in a structured
    format.
    """
