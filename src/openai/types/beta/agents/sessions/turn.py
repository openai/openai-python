# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ....._models import BaseModel
from ...token_usage import TokenUsage
from ...session_turn_error import SessionTurnError

__all__ = ["Turn"]


class Turn(BaseModel):
    """The canonical public representation of a session turn."""

    id: str
    """The ID of the turn."""

    agent_id: str
    """The ID of the agent that ran the turn."""

    completed_at: Optional[int] = None
    """The Unix timestamp, in seconds, when the turn reached a terminal state."""

    created_at: int
    """The Unix timestamp, in seconds, used to order the turn by creation time.

    Subagent turns use their start time, falling back to completion time or the
    subagent opening time when the preceding timestamps are unavailable.
    """

    error: Optional[SessionTurnError] = None
    """A customer-safe error describing why a session request failed."""

    object: Literal["agent.session.turn"]
    """The object type. Always `agent.session.turn`."""

    session_id: str
    """The ID of the session that owns the turn."""

    started_at: Optional[int] = None
    """The Unix timestamp, in seconds, when the turn started."""

    status: Literal["queued", "in_progress", "waiting", "completed", "failed", "cancelled"]
    """The current status of the turn.

    - `queued` - The turn is waiting to start.
    - `in_progress` - The turn is in progress.
    - `waiting` - The turn is waiting for external input.
    - `completed` - The turn completed successfully.
    - `failed` - The turn failed.
    - `cancelled` - The turn was cancelled.
    """

    subagent_id: Optional[str] = None
    """The ID of the subagent that ran the turn, if applicable."""

    usage: Optional[TokenUsage] = None
    """Recorded token usage for a session or turn.

    Usage is best effort and may change.
    """
