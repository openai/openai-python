# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "WorkloadIdentityProviderCreateParams",
    "AttributeTransformation",
    "Verification",
    "VerificationDiscovery",
    "VerificationUploadedJwks",
]


class WorkloadIdentityProviderCreateParams(TypedDict, total=False):
    audience: Required[str]

    issuer: Required[str]

    name: Required[str]

    type: Required[Literal["oidc"]]

    attribute_transformations: Iterable[AttributeTransformation]

    description: str

    enabled: bool

    verification: Verification


class AttributeTransformation(TypedDict, total=False):
    attribute: Required[str]

    expression: Required[str]


class VerificationDiscovery(TypedDict, total=False):
    discovery_url: Required[Optional[str]]

    type: Required[Literal["discovery"]]


class VerificationUploadedJwks(TypedDict, total=False):
    jwks: Required[Dict[str, object]]

    type: Required[Literal["uploaded_jwks"]]


Verification: TypeAlias = Union[VerificationDiscovery, VerificationUploadedJwks]
