# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["DemoAPIListParams"]


class DemoAPIListParams(TypedDict, total=False):
    limit: int
    """The maximum number of widgets to return."""

    status: Literal["pending", "active", "archived"]
    """Filters widgets by their current status."""
