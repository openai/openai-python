# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["WorkloadIdentityProviderDeleted"]


class WorkloadIdentityProviderDeleted(BaseModel):
    id: str

    deleted: bool

    object: Literal["organization.workload_identity_provider.deleted"]
