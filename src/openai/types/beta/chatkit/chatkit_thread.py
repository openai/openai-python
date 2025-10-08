# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ...._utils import PropertyInfo
from ...._models import BaseModel

__all__ = ["ChatKitThread", "Status", "StatusActive", "StatusLocked", "StatusClosed"]


class StatusActive(BaseModel):
    type: Literal["active"]
    """Status discriminator that is always `active`."""


class StatusLocked(BaseModel):
    reason: Optional[str] = None
    """Reason that the thread was locked. Defaults to null when no reason is recorded."""

    type: Literal["locked"]
    """Status discriminator that is always `locked`."""


class StatusClosed(BaseModel):
    reason: Optional[str] = None
    """Reason that the thread was closed. Defaults to null when no reason is recorded."""

    type: Literal["closed"]
    """Status discriminator that is always `closed`."""


Status: TypeAlias = Annotated[Union[StatusActive, StatusLocked, StatusClosed], PropertyInfo(discriminator="type")]


class ChatKitThread(BaseModel):
    id: str
    """Identifier of the thread."""

    created_at: int
    """Unix timestamp (in seconds) for when the thread was created."""

    object: Literal["chatkit.thread"]
    """Type discriminator that is always `chatkit.thread`."""

    status: Status
    """Current status for the thread. Defaults to `active` for newly created threads."""

    title: Optional[str] = None
    """Optional human-readable title for the thread.

    Defaults to null when no title has been generated.
    """

    user: str
    """Free-form string that identifies your end user who owns the thread."""
