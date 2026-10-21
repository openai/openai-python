# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["UserCreateResponse"]


class UserCreateResponse(BaseModel):
    """Confirmation payload returned after adding a user to a group."""

    group_id: str
    """Identifier of the group the user was added to."""

    object: Literal["group.user"]
    """Always `group.user`."""

    user_id: str
    """Identifier of the user that was added."""
