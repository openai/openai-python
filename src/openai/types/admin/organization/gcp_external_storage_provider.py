# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["GcpExternalStorageProvider"]


class GcpExternalStorageProvider(BaseModel):
    audience: str

    bucket: str

    region: str

    type: Literal["gcp"]

    workload_identity_pool_id: str

    workload_identity_project_number: str

    workload_identity_provider_id: str
