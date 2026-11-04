# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .hosted_environment_file_id import HostedEnvironmentFileID

__all__ = ["HostedEnvironmentFile", "HostedEnvironmentFileResourceInline"]


class HostedEnvironmentFileResourceInline(BaseModel):
    """A file supplied inline when the session was created."""

    id: str
    """The session-scoped ID of the file in the execution environment."""

    path: str
    """The file's absolute path inside the environment."""

    size_bytes: int
    """The decoded file size in bytes."""

    type: Literal["inline"]
    """The type of the object. Always `inline`."""


HostedEnvironmentFile: TypeAlias = Annotated[
    Union[HostedEnvironmentFileID, HostedEnvironmentFileResourceInline], PropertyInfo(discriminator="type")
]
