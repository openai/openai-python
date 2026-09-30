# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

from ..responses.response_includable import ResponseIncludable

__all__ = ["ItemRetrieveParams"]


class ItemRetrieveParams(TypedDict, total=False):
    conversation_id: Required[str]

    include: List[ResponseIncludable]
    """Additional fields to include in the response.

    See the `include` parameter for
    [listing Conversation items above](https://developers.openai.com/api/reference/resources/conversations/subresources/items/methods/list#%28resource%29%20conversations.items%20%3E%20%28method%29%20list%20%3E%20%28params%29%20default%20%3E%20%28param%29%20include%20%3E%20%28schema%29)
    for more information.
    """
