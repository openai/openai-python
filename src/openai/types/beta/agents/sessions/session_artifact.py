# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["SessionArtifact"]


class SessionArtifact(BaseModel):
    """An immutable file published by a completed hosted session turn."""

    id: str
    """The immutable artifact ID."""

    created_at: int
    """The Unix timestamp, in seconds, when the artifact was published."""

    environment_id: str
    """The ID of the environment that produced the artifact."""

    object: Literal["agent.session.artifact"]
    """The object type. Always `agent.session.artifact`."""

    path: str
    """The original absolute file path in the execution environment."""

    session_id: str
    """The ID of the session that owns the artifact."""

    size_bytes: int
    """The immutable artifact size in bytes."""

    turn_id: str
    """The ID of the completed turn that published the artifact."""
