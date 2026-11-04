# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["AzureExternalStorageProvider"]


class AzureExternalStorageProvider(BaseModel):
    account_name: str

    container: str

    region: str

    resource_group: str

    subscription_id: str

    tenant_id: str

    type: Literal["azure"]
