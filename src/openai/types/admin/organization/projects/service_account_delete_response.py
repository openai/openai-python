# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ServiceAccountDeleteResponse"]


class ServiceAccountDeleteResponse(BaseModel):
    id: str

    deleted: bool

    object: Literal["organization.project.service_account.deleted"]
