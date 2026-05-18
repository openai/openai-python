# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ProjectModelPermissionsDeleted"]


class ProjectModelPermissionsDeleted(BaseModel):
    """Confirmation payload returned after deleting project model permissions."""

    deleted: bool
    """Whether the project model permissions were deleted."""

    object: Literal["project.model_permissions.deleted"]
    """The object type, which is always `project.model_permissions.deleted`."""
