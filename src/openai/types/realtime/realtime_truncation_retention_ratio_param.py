# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RealtimeTruncationRetentionRatioParam"]


class RealtimeTruncationRetentionRatioParam(TypedDict, total=False):
    retention_ratio: Required[float]
    """
    Fraction of post-instruction conversation tokens to retain (0.0 - 1.0) when the
    conversation exceeds the input token limit.
    """

    type: Required[Literal["retention_ratio"]]
    """Use retention ratio truncation."""
