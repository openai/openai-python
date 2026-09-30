# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentSessionDeleted"]


class AgentSessionDeleted(BaseModel):
    """A Managed Agents session removed from the public API.

    Physical cleanup may continue asynchronously.
    """

    id: str
    """The ID of the deleted session."""

    deleted: bool
    """Whether the session has been removed from the public API.

    Always `true`. Physical cleanup may still be in progress.
    """

    object: Literal["agent.session.deleted"]
    """The object type. Always `agent.session.deleted`."""
