# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["UserDeleteResponse"]


class UserDeleteResponse(BaseModel):
    """Confirmation payload returned after removing a user from a group."""

    deleted: bool
    """Whether the group membership was removed."""

    object: Literal["group.user.deleted"]
    """Always `group.user.deleted`."""
