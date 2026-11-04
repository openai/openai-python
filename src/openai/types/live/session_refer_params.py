# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SessionReferParams"]


class SessionReferParams(TypedDict, total=False):
    target_uri: Required[str]
    """
    Nonblank URI for the SIP Refer-To header, such as tel:+14155550123 or
    sip:agent@example.com.
    """
