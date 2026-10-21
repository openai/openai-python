# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["CertificateDeleteResponse"]


class CertificateDeleteResponse(BaseModel):
    id: str
    """The ID of the certificate that was deleted."""

    object: Literal["certificate.deleted"]
    """The object type, must be `certificate.deleted`."""
