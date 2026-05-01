# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["Invite", "Project"]


class Project(BaseModel):
    id: Optional[str] = None
    """Project's public ID"""

    role: Optional[Literal["member", "owner"]] = None
    """Project membership role"""


class Invite(BaseModel):
    """Represents an individual `invite` to the organization."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    created_at: int
    """The Unix timestamp (in seconds) of when the invite was sent."""

    email: str
    """The email address of the individual to whom the invite was sent"""

    expires_at: Optional[int] = None
    """The Unix timestamp (in seconds) of when the invite expires."""

    object: Literal["organization.invite"]
    """The object type, which is always `organization.invite`"""

    role: Literal["owner", "reader"]
    """`owner` or `reader`"""

    status: Literal["accepted", "expired", "pending"]
    """`accepted`,`expired`, or `pending`"""

    accepted_at: Optional[int] = None
    """The Unix timestamp (in seconds) of when the invite was accepted."""

    projects: Optional[List[Project]] = None
    """The projects that were granted membership upon acceptance of the invite."""
