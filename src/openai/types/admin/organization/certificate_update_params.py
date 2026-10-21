# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["CertificateUpdateParams"]


class CertificateUpdateParams(TypedDict, total=False):
    name: str
    """The updated name for the certificate"""
