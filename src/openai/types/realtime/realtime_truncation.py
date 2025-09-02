# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel

__all__ = ["RealtimeTruncation", "RetentionRatioTruncation"]


class RetentionRatioTruncation(BaseModel):
    retention_ratio: float
    """Fraction of pre-instruction conversation tokens to retain (0.0 - 1.0)."""

    type: Literal["retention_ratio"]
    """Use retention ratio truncation."""

    post_instructions_token_limit: Optional[int] = None
    """Optional cap on tokens allowed after the instructions."""


RealtimeTruncation: TypeAlias = Union[Literal["auto", "disabled"], RetentionRatioTruncation]
