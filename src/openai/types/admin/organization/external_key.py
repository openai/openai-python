# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["ExternalKey"]


class ExternalKey(BaseModel):
    id: str

    api_project_ids: List[str]

    created_at: int

    name: str

    object: str

    type: str

    workspace_id: str

    audience: Optional[str] = None

    external_id: Optional[str] = None

    key_name: Optional[str] = None

    key_version: Optional[str] = None

    kms_arn: Optional[str] = None

    kms_key_location: Optional[str] = None

    kms_key_name: Optional[str] = None

    kms_key_ring_name: Optional[str] = None

    kms_key_version: Optional[str] = None

    kms_project_id: Optional[str] = None

    purpose: Optional[Literal["ekm", "psp_decryption"]] = None

    role_arn: Optional[str] = None

    tenant_id: Optional[str] = None

    vault_uri: Optional[str] = None

    workload_identity_pool_id: Optional[str] = None

    workload_identity_project_number: Optional[str] = None

    workload_identity_provider_id: Optional[str] = None
