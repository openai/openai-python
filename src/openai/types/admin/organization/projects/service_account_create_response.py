# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ServiceAccountCreateResponse", "APIKey"]


class APIKey(BaseModel):
    id: str

    created_at: int

    name: str

    object: Literal["organization.project.service_account.api_key"]
    """The object type, which is always `organization.project.service_account.api_key`"""

    value: str


class ServiceAccountCreateResponse(BaseModel):
    id: str

    api_key: Optional[APIKey] = None

    created_at: int

    name: str

    object: Literal["organization.project.service_account"]

    role: Literal["member"]
    """Service accounts can only have one role of type `member`"""
