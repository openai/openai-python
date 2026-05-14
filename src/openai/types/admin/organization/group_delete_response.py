# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["GroupDeleteResponse"]


class GroupDeleteResponse(BaseModel):
    """Confirmation payload returned after deleting a group."""

    id: str
    """Identifier of the deleted group."""

    deleted: bool
    """Whether the group was deleted."""

    object: Literal["group.deleted"]
    """Always `group.deleted`."""
