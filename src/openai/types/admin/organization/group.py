# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["Group"]


class Group(BaseModel):
    """Details about an organization group."""

    id: str
    """Identifier for the group."""

    created_at: int
    """Unix timestamp (in seconds) when the group was created."""

    group_type: str
    """The type of the group."""

    is_scim_managed: bool
    """
    Whether the group is managed through SCIM and controlled by your identity
    provider.
    """

    name: str
    """Display name of the group."""
