# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ProjectUser"]


class ProjectUser(BaseModel):
    """Represents an individual user in a project."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    added_at: int
    """The Unix timestamp (in seconds) of when the project was added."""

    object: Literal["organization.project.user"]
    """The object type, which is always `organization.project.user`"""

    role: str
    """`owner` or `member`"""

    email: Optional[str] = None
    """The email address of the user"""

    name: Optional[str] = None
    """The name of the user"""
