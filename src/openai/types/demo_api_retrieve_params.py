# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DemoAPIRetrieveParams"]


class DemoAPIRetrieveParams(TypedDict, total=False):
    include_history: bool
    """Whether to include the widget's status history."""
