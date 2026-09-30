# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["HostedEnvironmentFileID"]


class HostedEnvironmentFileID(BaseModel):
    """A file copied from the OpenAI Files API."""

    id: str
    """The session-scoped ID of the file in the execution environment."""

    file_id: str
    """The ID of the uploaded file."""

    path: str
    """The file's absolute path inside the environment."""

    size_bytes: int
    """The decoded file size in bytes."""

    type: Literal["file_id"]
    """The type of the object. Always `file_id`."""
