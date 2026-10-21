# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["GroupDeleteResponse"]


class GroupDeleteResponse(BaseModel):
    """Confirmation payload returned after removing a group from a project."""

    deleted: bool
    """Whether the group membership in the project was removed."""

    object: Literal["project.group.deleted"]
    """Always `project.group.deleted`."""
