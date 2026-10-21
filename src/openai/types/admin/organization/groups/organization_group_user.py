# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ....._models import BaseModel

__all__ = ["OrganizationGroupUser"]


class OrganizationGroupUser(BaseModel):
    """Represents an individual user returned when inspecting group membership."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    email: Optional[str] = None
    """The email address of the user."""

    name: str
    """The name of the user."""
