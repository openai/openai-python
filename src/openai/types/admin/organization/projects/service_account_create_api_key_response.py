# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ServiceAccountCreateAPIKeyResponse"]


class ServiceAccountCreateAPIKeyResponse(BaseModel):
    id: str
    """The identifier of the API key."""

    created_at: int
    """The Unix timestamp (in seconds) when the API key was created."""

    name: str
    """The name of the API key."""

    object: Literal["organization.project.service_account.api_key"]
    """The object type, which is always `organization.project.service_account.api_key`"""

    value: str
    """The unredacted API key value."""
