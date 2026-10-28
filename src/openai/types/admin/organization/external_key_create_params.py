# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "ExternalKeyCreateParams",
    "V1OrganizationExternalKeysPostRequestAws",
    "V1OrganizationExternalKeysPostRequestGcp",
    "V1OrganizationExternalKeysPostRequestAzure",
]


class V1OrganizationExternalKeysPostRequestAws(TypedDict, total=False):
    external_id: Required[str]

    kms_arn: Required[str]

    name: Required[str]

    role_arn: Required[str]

    type: Required[Literal["aws"]]

    purpose: Union[Literal["ekm"], Literal["psp_decryption"]]


class V1OrganizationExternalKeysPostRequestGcp(TypedDict, total=False):
    audience: Required[str]

    kms_key_location: Required[str]

    kms_key_name: Required[str]

    kms_key_ring_name: Required[str]

    kms_project_id: Required[str]

    name: Required[str]

    type: Required[Literal["gcp"]]

    workload_identity_pool_id: Required[str]

    workload_identity_project_number: Required[str]

    workload_identity_provider_id: Required[str]

    kms_key_version: str

    purpose: Union[Literal["ekm"], Literal["psp_decryption"]]


class V1OrganizationExternalKeysPostRequestAzure(TypedDict, total=False):
    key_name: Required[str]

    name: Required[str]

    tenant_id: Required[str]

    type: Required[Literal["azure"]]

    vault_uri: Required[str]

    key_version: str

    purpose: Union[Literal["ekm"], Literal["psp_decryption"]]


ExternalKeyCreateParams: TypeAlias = Union[
    V1OrganizationExternalKeysPostRequestAws,
    V1OrganizationExternalKeysPostRequestGcp,
    V1OrganizationExternalKeysPostRequestAzure,
]
