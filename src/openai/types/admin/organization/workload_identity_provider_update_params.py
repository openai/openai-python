# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "WorkloadIdentityProviderUpdateParams",
    "AttributeTransformation",
    "Verification",
    "VerificationDiscoveryVerificationParam",
    "VerificationUploadedJwksVerificationParam",
]


class WorkloadIdentityProviderUpdateParams(TypedDict, total=False):
    attribute_transformations: Iterable[AttributeTransformation]

    audience: str

    description: Optional[str]

    enabled: bool

    issuer: str

    name: str

    verification: Verification


class AttributeTransformation(TypedDict, total=False):
    attribute: Required[str]

    expression: Required[str]


class VerificationDiscoveryVerificationParam(TypedDict, total=False):
    discovery_url: Required[Optional[str]]

    type: Required[Literal["discovery"]]


class VerificationUploadedJwksVerificationParam(TypedDict, total=False):
    jwks: Required[Dict[str, object]]

    type: Required[Literal["uploaded_jwks"]]


Verification: TypeAlias = Union[VerificationDiscoveryVerificationParam, VerificationUploadedJwksVerificationParam]
