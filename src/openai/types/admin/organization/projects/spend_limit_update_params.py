# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["SpendLimitUpdateParams"]


class SpendLimitUpdateParams(TypedDict, total=False):
    currency: Required[Literal["USD"]]
    """The currency for the threshold amount. Currently, only `USD` is supported."""

    interval: Required[Literal["month"]]
    """The time interval for evaluating spend against the threshold.

    Currently, only `month` is supported.
    """

    threshold_amount: Required[int]
    """The hard spend limit amount, in cents."""
