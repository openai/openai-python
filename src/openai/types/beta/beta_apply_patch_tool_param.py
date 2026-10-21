# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["BetaApplyPatchToolParam"]


class BetaApplyPatchToolParam(TypedDict, total=False):
    """Allows the assistant to create, delete, or update files using unified diffs."""

    type: Required[Literal["apply_patch"]]
    """The type of the tool. Always `apply_patch`."""

    allowed_callers: Optional[List[Literal["direct", "programmatic"]]]
    """The tool invocation context(s)."""
