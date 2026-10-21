# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["OrganizationUser", "Projects", "ProjectsData", "User"]


class ProjectsData(BaseModel):
    id: Optional[str] = None

    name: Optional[str] = None

    role: Optional[str] = None


class Projects(BaseModel):
    """Projects associated with the user, if included."""

    data: List[ProjectsData]

    object: Literal["list"]


class User(BaseModel):
    """Nested user details."""

    id: str

    object: Literal["user"]

    banned: Optional[bool] = None

    banned_at: Optional[int] = None

    email: Optional[str] = None

    enabled: Optional[bool] = None

    name: Optional[str] = None

    picture: Optional[str] = None


class OrganizationUser(BaseModel):
    """Represents an individual `user` within an organization."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    added_at: int
    """The Unix timestamp (in seconds) of when the user was added."""

    object: Literal["organization.user"]
    """The object type, which is always `organization.user`"""

    api_key_last_used_at: Optional[int] = None
    """The Unix timestamp (in seconds) of the user's last API key usage."""

    created: Optional[int] = None
    """The Unix timestamp (in seconds) of when the user was created."""

    developer_persona: Optional[str] = None
    """The developer persona metadata for the user."""

    email: Optional[str] = None
    """The email address of the user"""

    is_default: Optional[bool] = None
    """Whether this is the organization's default user."""

    is_scale_tier_authorized_purchaser: Optional[bool] = None
    """Whether the user is an authorized purchaser for Scale Tier."""

    is_scim_managed: Optional[bool] = None
    """Whether the user is managed through SCIM."""

    is_service_account: Optional[bool] = None
    """Whether the user is a service account."""

    name: Optional[str] = None
    """The name of the user"""

    projects: Optional[Projects] = None
    """Projects associated with the user, if included."""

    role: Optional[str] = None
    """`owner` or `reader`"""

    technical_level: Optional[str] = None
    """The technical level metadata for the user."""

    user: Optional[User] = None
    """Nested user details."""
