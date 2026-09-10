# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["EnvironmentFile"]


class EnvironmentFile(BaseModel):
    """A live file in an execution environment."""

    environment_id: str
    """The ID of the environment containing this file."""

    object: Literal["agent.environment.file"]
    """The object type. Always `agent.environment.file`."""

    path: str
    """The absolute file path inside the environment's workspace."""

    size_bytes: int
    """The file size in bytes."""
