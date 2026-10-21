# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["Certificate", "CertificateDetails"]


class CertificateDetails(BaseModel):
    content: Optional[str] = None
    """The content of the certificate in PEM format."""

    expires_at: Optional[int] = None
    """The Unix timestamp (in seconds) of when the certificate expires."""

    valid_at: Optional[int] = None
    """The Unix timestamp (in seconds) of when the certificate becomes valid."""


class Certificate(BaseModel):
    """Represents an individual `certificate` uploaded to the organization."""

    id: str
    """The identifier, which can be referenced in API endpoints"""

    certificate_details: CertificateDetails

    created_at: int
    """The Unix timestamp (in seconds) of when the certificate was uploaded."""

    name: Optional[str] = None
    """The name of the certificate."""

    object: Literal["certificate", "organization.certificate", "organization.project.certificate"]
    """The object type.

    - If creating, updating, or getting a specific certificate, the object type is
      `certificate`.
    - If listing, activating, or deactivating certificates for the organization, the
      object type is `organization.certificate`.
    - If listing, activating, or deactivating certificates for a project, the object
      type is `organization.project.certificate`.
    """

    active: Optional[bool] = None
    """Whether the certificate is currently active at the specified scope.

    Not returned when getting details for a specific certificate.
    """
