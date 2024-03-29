# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RetrievalTool"]


class RetrievalTool(BaseModel):
    type: Literal["retrieval"]
    """The type of tool being defined: `retrieval`"""
