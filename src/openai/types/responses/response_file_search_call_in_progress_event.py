# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseFileSearchCallInProgressEvent"]


class ResponseFileSearchCallInProgressEvent(BaseModel):
    item_id: str
    """The ID of the output item that the file search call is initiated."""

    output_index: int
    """The index of the output item that the file search call is initiated."""

    type: Literal["response.file_search_call.in_progress"]
    """The type of the event. Always `response.file_search_call.in_progress`."""
