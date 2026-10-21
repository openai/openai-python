# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["AdminAPIKeyDeleteResponse"]


class AdminAPIKeyDeleteResponse(BaseModel):
    id: str

    deleted: bool

    object: Literal["organization.admin_api_key.deleted"]
