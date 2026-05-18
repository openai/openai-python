# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from ....._types import SequenceNotStr

__all__ = ["ModelPermissionUpdateParams"]


class ModelPermissionUpdateParams(TypedDict, total=False):
    mode: Required[Literal["allow_list", "deny_list"]]
    """The model permissions mode to apply."""

    model_ids: Required[SequenceNotStr[str]]
    """The model IDs included in this permissions policy."""
