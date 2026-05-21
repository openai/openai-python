# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["UserRetrieveResponse"]


class UserRetrieveResponse(BaseModel):
    """Details about a user returned from an organization group membership lookup."""

    id: str
    """Identifier for the user."""

    email: Optional[str] = None
    """Email address of the user, or `null` for users without an email."""

    is_service_account: Optional[bool] = None
    """Whether the user is a service account."""

    name: str
    """Display name of the user."""

    picture: Optional[str] = None
    """URL of the user's profile picture, if available."""

    user_type: Literal["user", "tenant_user"]
    """The type of user."""
