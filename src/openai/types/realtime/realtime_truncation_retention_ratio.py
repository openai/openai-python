# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RealtimeTruncationRetentionRatio"]


class RealtimeTruncationRetentionRatio(BaseModel):
    retention_ratio: float
    """
    Fraction of post-instruction conversation tokens to retain (0.0 - 1.0) when the
    conversation exceeds the input token limit.
    """

    type: Literal["retention_ratio"]
    """Use retention ratio truncation."""
