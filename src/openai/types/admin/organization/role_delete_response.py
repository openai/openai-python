# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["RoleDeleteResponse"]


class RoleDeleteResponse(BaseModel):
    """Confirmation payload returned after deleting a role."""

    id: str
    """Identifier of the deleted role."""

    deleted: bool
    """Whether the role was deleted."""

    object: Literal["role.deleted"]
    """Always `role.deleted`."""
