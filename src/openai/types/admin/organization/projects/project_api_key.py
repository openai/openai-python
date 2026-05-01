# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ProjectAPIKey", "Owner", "OwnerServiceAccount", "OwnerUser"]


class OwnerServiceAccount(BaseModel):
    """The service account that owns a project API key."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    created_at: int
    """The Unix timestamp (in seconds) of when the service account was created."""

    name: str
    """The name of the service account."""

    role: str
    """The service account's project role."""


class OwnerUser(BaseModel):
    """The user that owns a project API key."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    created_at: int
    """The Unix timestamp (in seconds) of when the user was created."""

    email: str
    """The email address of the user."""

    name: str
    """The name of the user."""

    role: str
    """The user's project role."""


class Owner(BaseModel):
    service_account: Optional[OwnerServiceAccount] = None
    """The service account that owns a project API key."""

    type: Optional[Literal["user", "service_account"]] = None
    """`user` or `service_account`"""

    user: Optional[OwnerUser] = None
    """The user that owns a project API key."""


class ProjectAPIKey(BaseModel):
    """Represents an individual API key in a project."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    created_at: int
    """The Unix timestamp (in seconds) of when the API key was created"""

    last_used_at: Optional[int] = None
    """The Unix timestamp (in seconds) of when the API key was last used."""

    name: str
    """The name of the API key"""

    object: Literal["organization.project.api_key"]
    """The object type, which is always `organization.project.api_key`"""

    owner: Owner

    redacted_value: str
    """The redacted value of the API key"""
