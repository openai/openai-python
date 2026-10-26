# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentSessionEnvironmentState", "Error"]


class Error(BaseModel):
    """The error reported while preparing the environment, if any."""

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
    """The error reported while preparing the environment, if any."""

    status: Literal["pending", "ready", "connected", "disconnected", "suspended", "expired", "failed"]
    """The environment's connection status.

    - `pending` - The environment is being prepared.
    - `ready` - The environment is ready to connect.
    - `connected` - The environment is connected.
    - `disconnected` - The environment is disconnected.
    - `suspended` - The environment is stopped and can be resumed from its private
      checkpoint.
    - `expired` - The environment and its private checkpoint have expired.
    - `failed` - The environment failed to connect.
    """

    type: str
    """The environment type."""
