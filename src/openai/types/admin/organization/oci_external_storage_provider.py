# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["OciExternalStorageProvider"]


class OciExternalStorageProvider(BaseModel):
    bucket: str

    region: str

    tenancy_ocid: str

    type: Literal["oci"]
