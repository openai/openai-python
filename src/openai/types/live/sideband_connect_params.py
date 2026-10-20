# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["SidebandConnectParams"]


class SidebandConnectParams(TypedDict, total=False):
    graceful_close: bool
    """Opt in to the graceful WebSocket closing handshake when the session ends.

    The server may also enable this behavior by default.
    """
