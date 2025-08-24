# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["TopLogProb"]


class TopLogProb(BaseModel):
    token: str

    bytes: List[int]

    logprob: float
