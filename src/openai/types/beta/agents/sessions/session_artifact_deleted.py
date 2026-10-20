# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["SessionArtifactDeleted"]


class SessionArtifactDeleted(BaseModel):
    """Confirmation that an immutable session artifact was deleted."""

    id: str
    """The ID of the deleted session artifact."""

    deleted: bool
    """Whether the session artifact was deleted. Always `true`."""

    object: Literal["agent.session.artifact.deleted"]
    """The object type. Always `agent.session.artifact.deleted`."""
