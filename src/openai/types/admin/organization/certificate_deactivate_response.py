# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["CertificateDeactivateResponse", "CertificateDetails"]


class CertificateDetails(BaseModel):
    expires_at: Optional[int] = None
    """The Unix timestamp (in seconds) of when the certificate expires."""

    valid_at: Optional[int] = None
    """The Unix timestamp (in seconds) of when the certificate becomes valid."""


class CertificateDeactivateResponse(BaseModel):
    """Represents an individual certificate configured at the organization level."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    active: bool
    """Whether the certificate is currently active at the organization level."""

    certificate_details: CertificateDetails

    created_at: int
    """The Unix timestamp (in seconds) of when the certificate was uploaded."""

    name: Optional[str] = None
    """The name of the certificate."""

    object: Literal["organization.certificate"]
    """The object type, which is always `organization.certificate`."""
