# File generated from our OpenAPI spec by Stainless.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RetrievalTool"]


class RetrievalTool(BaseModel):
    type: Literal["retrieval"]
    """The type of tool being defined: `retrieval`"""
