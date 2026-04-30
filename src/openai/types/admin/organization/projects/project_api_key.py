# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ....._models import BaseModel
from .project_user import ProjectUser
from .project_service_account import ProjectServiceAccount

__all__ = ["ProjectAPIKey", "Owner"]


class Owner(BaseModel):
    service_account: Optional[ProjectServiceAccount] = None
    """Represents an individual service account in a project."""

    type: Optional[Literal["user", "service_account"]] = None
    """`user` or `service_account`"""

    user: Optional[ProjectUser] = None
    """Represents an individual user in a project."""


class ProjectAPIKey(BaseModel):
    """Represents an individual API key in a project."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    created_at: int
    """The Unix timestamp (in seconds) of when the API key was created"""

    last_used_at: int
    """The Unix timestamp (in seconds) of when the API key was last used."""

    name: str
    """The name of the API key"""

    object: Literal["organization.project.api_key"]
    """The object type, which is always `organization.project.api_key`"""

    owner: Owner

    redacted_value: str
    """The redacted value of the API key"""
