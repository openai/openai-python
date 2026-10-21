# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import dataclasses
from typing_extensions import TypedDict

from .._types import Query, Headers


@dataclasses.dataclass(frozen=True)
class ReconnectingEvent:
    """Information about a reconnection attempt, passed to the ``on_reconnecting`` handler."""

    attempt: int
    """Which retry attempt this is (1-based)."""

    max_attempts: int
    """Total attempts that will be made."""

    delay: float
    """Delay in seconds before this attempt connects."""

    close_code: int
    """The WebSocket close code that triggered reconnection."""

    extra_query: Query
    """The current query parameters."""

    extra_headers: Headers
    """The current headers."""


class ReconnectingOverrides(TypedDict, total=False):
    """Optional overrides returned from the ``on_reconnecting`` handler
    to customize the next reconnection attempt."""

    extra_query: Query
    """If provided, assigns the query parameters for the next connection."""

    extra_headers: Headers
    """If provided, assigns the headers for the next connection."""

    abort: bool
    """If set to ``True``, will stop attempting to reconnect."""


# RFC 6455 §7.4.1
_RECOVERABLE_CLOSE_CODES: frozenset[int] = frozenset(
    {
        1001,  # Going away (server shutting down)
        1005,  # No status code (abnormal)
        1006,  # Abnormal closure (network drop)
        1011,  # Internal server error
        1012,  # Service restart
        1013,  # Try again later
        1015,  # TLS handshake failure
    }
)


def is_recoverable_close(code: int) -> bool:
    """Return ``True`` if the WebSocket close *code* is worth retrying."""
    return code in _RECOVERABLE_CLOSE_CODES
