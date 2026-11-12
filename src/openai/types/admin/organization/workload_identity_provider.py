# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ...._utils import PropertyInfo
from ...._models import BaseModel

__all__ = [
    "WorkloadIdentityProvider",
    "AttributeTransformation",
    "Verification",
    "VerificationDiscovery",
    "VerificationUploadedJwks",
]


class AttributeTransformation(BaseModel):
    attribute: str

    expression: str


class VerificationDiscovery(BaseModel):
    discovery_url: Optional[str] = None

    type: Literal["discovery"]


class VerificationUploadedJwks(BaseModel):
    jwks: Dict[str, object]

    type: Literal["uploaded_jwks"]


Verification: TypeAlias = Annotated[
    Union[VerificationDiscovery, VerificationUploadedJwks], PropertyInfo(discriminator="type")
]


class WorkloadIdentityProvider(BaseModel):
    id: str

    attribute_transformations: List[AttributeTransformation]

    audience: str

    created_at: int

    description: Optional[str] = None

    enabled: bool

    issuer: str

    name: str

    object: Literal["organization.workload_identity_provider"]

    type: Literal["oidc"]

    updated_at: int

    verification: Verification
