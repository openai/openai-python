# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentSessionEnvironmentState", "Error"]


class Error(BaseModel):
    """An error reported while preparing a session environment."""

    code: str
    """A machine-readable error code."""

    message: str
    """A human-readable error message."""

    type: str
    """The error type."""


class AgentSessionEnvironmentState(BaseModel):
    """The current state of a session environment."""

    id: str
    """The public ID of the environment."""

    error: Optional[Error] = None
    """An error reported while preparing a session environment."""

    status: Literal["pending", "ready", "connected", "disconnected", "failed"]
    """The environment's connection status.

    - `pending` - The environment is being prepared.
    - `ready` - The environment is ready to connect.
    - `connected` - The environment is connected.
    - `disconnected` - The environment is disconnected.
    - `failed` - The environment failed to connect.
    """

    type: str
    """The environment type."""
