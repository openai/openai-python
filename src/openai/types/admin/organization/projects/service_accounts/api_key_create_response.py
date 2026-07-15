# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ......_models import BaseModel

__all__ = ["APIKeyCreateResponse"]


class APIKeyCreateResponse(BaseModel):
    id: str

    created_at: int

    name: str

    object: Literal["organization.project.service_account.api_key"]
    """The object type, which is always `organization.project.service_account.api_key`"""

    value: str
