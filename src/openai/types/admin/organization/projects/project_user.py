# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ProjectUser"]


class ProjectUser(BaseModel):
    """Represents an individual user in a project."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    added_at: int
    """The Unix timestamp (in seconds) of when the project was added."""

    email: str
    """The email address of the user"""

    name: str
    """The name of the user"""

    object: Literal["organization.project.user"]
    """The object type, which is always `organization.project.user`"""

    role: Literal["owner", "member"]
    """`owner` or `member`"""
