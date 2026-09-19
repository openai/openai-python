# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ...._utils import PropertyInfo
from ...._models import BaseModel
from .aws_external_storage_provider import AwsExternalStorageProvider
from .azure_external_storage_provider import AzureExternalStorageProvider

__all__ = ["ExternalStorageConfiguration", "Provider"]

Provider: TypeAlias = Annotated[
    Union[AwsExternalStorageProvider, AzureExternalStorageProvider], PropertyInfo(discriminator="type")
]


class ExternalStorageConfiguration(BaseModel):
    id: str

    created_at: int

    geography: str

    object: Literal["organization.external_storage"]

    project_id: str

    provider: Provider

    status: Literal["pending", "validated", "unhealthy"]
