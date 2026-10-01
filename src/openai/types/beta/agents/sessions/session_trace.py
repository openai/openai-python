# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import builtins
from typing import Dict
from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["SessionTrace"]


class SessionTrace(BaseModel):
    id: str
    """The root turn ID. Use this ID as the pagination anchor."""

    created_at: int
    """The Unix timestamp in seconds when the root turn was created."""

    object: Literal["agent.session.trace"]
    """The object type, which is always `agent.session.trace`."""

    otlp: Dict[str, builtins.object]
    """An OTLP JSON ExportTraceServiceRequest containing resourceSpans.

    Only currently published data is returned; later trace updates are not awaited.
    """

    session_id: str
    """The session that owns this trace."""
