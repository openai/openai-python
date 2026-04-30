# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["OrganizationUser"]


class OrganizationUser(BaseModel):
    """Represents an individual `user` within an organization."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    added_at: int
    """The Unix timestamp (in seconds) of when the user was added."""

    email: str
    """The email address of the user"""

    name: str
    """The name of the user"""

    object: Literal["organization.user"]
    """The object type, which is always `organization.user`"""

    role: Literal["owner", "reader"]
    """`owner` or `reader`"""
