# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["AdminAPIKey", "Owner"]


class Owner(BaseModel):
    id: Optional[str] = None
    """The identifier, which can be referenced in API endpoints"""

    created_at: Optional[int] = None
    """The Unix timestamp (in seconds) of when the user was created"""

    name: Optional[str] = None
    """The name of the user"""

    object: Optional[str] = None
    """The object type, which is always organization.user"""

    role: Optional[str] = None
    """Always `owner`"""

    type: Optional[str] = None
    """Always `user`"""


class AdminAPIKey(BaseModel):
    """Represents an individual Admin API key in an org."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    created_at: int
    """The Unix timestamp (in seconds) of when the API key was created"""

    object: Literal["organization.admin_api_key"]
    """The object type, which is always `organization.admin_api_key`"""

    owner: Owner

    redacted_value: str
    """The redacted value of the API key"""

    last_used_at: Optional[int] = None
    """The Unix timestamp (in seconds) of when the API key was last used"""

    name: Optional[str] = None
    """The name of the API key"""
