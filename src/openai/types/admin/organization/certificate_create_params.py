# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["CertificateCreateParams"]


class CertificateCreateParams(TypedDict, total=False):
    certificate: Required[str]
    """The certificate content in PEM format"""

    name: str
    """An optional name for the certificate"""
