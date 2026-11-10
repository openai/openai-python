# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["EventStreamParams"]


class EventStreamParams(TypedDict, total=False):
    include_obfuscation: bool
    """Whether to include obfuscation padding in events on this connection.

    Defaults to `true`.
    """
