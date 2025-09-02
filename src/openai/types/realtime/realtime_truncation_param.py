# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["RealtimeTruncationParam", "RetentionRatioTruncation"]


class RetentionRatioTruncation(TypedDict, total=False):
    retention_ratio: Required[float]
    """Fraction of pre-instruction conversation tokens to retain (0.0 - 1.0)."""

    type: Required[Literal["retention_ratio"]]
    """Use retention ratio truncation."""

    post_instructions_token_limit: Optional[int]
    """Optional cap on tokens allowed after the instructions."""


RealtimeTruncationParam: TypeAlias = Union[Literal["auto", "disabled"], RetentionRatioTruncation]
