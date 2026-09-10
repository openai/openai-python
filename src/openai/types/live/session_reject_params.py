# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SessionRejectParams"]


class SessionRejectParams(TypedDict, total=False):
    status_code: Required[int]
    """SIP rejection status sent to the caller. This field is required."""
