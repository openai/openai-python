# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["ExternalStorageCreateParams", "Provider", "ProviderAws", "ProviderAzure"]


class ExternalStorageCreateParams(TypedDict, total=False):
    project_id: Required[str]

    provider: Required[Provider]


class ProviderAws(TypedDict, total=False):
    bucket: Required[str]

    role_arn: Required[str]

    type: Required[Literal["aws"]]


class ProviderAzure(TypedDict, total=False):
    account_name: Required[str]

    container: Required[str]

    resource_group: Required[str]

    subscription_id: Required[str]

    tenant_id: Required[str]

    type: Required[Literal["azure"]]


Provider: TypeAlias = Union[ProviderAws, ProviderAzure]
