# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["Project"]


class Project(BaseModel):
    """Represents an individual project."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    created_at: int
    """The Unix timestamp (in seconds) of when the project was created."""

    object: Literal["organization.project"]
    """The object type, which is always `organization.project`"""

    archived_at: Optional[int] = None
    """The Unix timestamp (in seconds) of when the project was archived or `null`."""

    external_key_id: Optional[str] = None
    """The external key associated with the project."""

    name: Optional[str] = None
    """The name of the project. This appears in reporting."""

    status: Optional[str] = None
    """`active` or `archived`"""
