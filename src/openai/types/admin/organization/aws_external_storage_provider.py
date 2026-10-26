# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["AwsExternalStorageProvider"]


class AwsExternalStorageProvider(BaseModel):
    account_id: str

    bucket: str

    external_id: str

    region: str

    role_arn: str

    type: Literal["aws"]
