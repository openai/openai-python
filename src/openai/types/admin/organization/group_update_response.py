# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["GroupUpdateResponse"]


class GroupUpdateResponse(BaseModel):
    """Response returned after updating a group."""

    id: str
    """Identifier for the group."""

    created_at: int
    """Unix timestamp (in seconds) when the group was created."""

    is_scim_managed: bool
    """
    Whether the group is managed through SCIM and controlled by your identity
    provider.
    """

    name: str
    """Updated display name for the group."""
