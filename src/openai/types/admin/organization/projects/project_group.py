# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ProjectGroup"]


class ProjectGroup(BaseModel):
    """Details about a group's membership in a project."""

    created_at: int
    """Unix timestamp (in seconds) when the group was granted project access."""

    group_id: str
    """Identifier of the group that has access to the project."""

    group_name: str
    """Display name of the group."""

    group_type: str
    """The type of the group."""

    object: Literal["project.group"]
    """Always `project.group`."""

    project_id: str
    """Identifier of the project."""
