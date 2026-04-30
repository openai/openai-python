# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from ....._models import BaseModel

__all__ = ["RoleListResponse"]


class RoleListResponse(BaseModel):
    """
    Detailed information about a role assignment entry returned when listing assignments.
    """

    id: str
    """Identifier for the role."""

    created_at: Optional[int] = None
    """When the role was created."""

    created_by: Optional[str] = None
    """Identifier of the actor who created the role."""

    created_by_user_obj: Optional[Dict[str, object]] = None
    """User details for the actor that created the role, when available."""

    description: Optional[str] = None
    """Description of the role."""

    metadata: Optional[Dict[str, object]] = None
    """Arbitrary metadata stored on the role."""

    name: str
    """Name of the role."""

    permissions: List[str]
    """Permissions associated with the role."""

    predefined_role: bool
    """Whether the role is predefined by OpenAI."""

    resource_type: str
    """Resource type the role applies to."""

    updated_at: Optional[int] = None
    """When the role was last updated."""
