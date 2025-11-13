# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ToolChoiceApplyPatchParam"]


class ToolChoiceApplyPatchParam(TypedDict, total=False):
    type: Required[Literal["apply_patch"]]
    """The tool to call. Always `apply_patch`."""
