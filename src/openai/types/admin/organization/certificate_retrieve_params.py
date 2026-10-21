# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["CertificateRetrieveParams"]


class CertificateRetrieveParams(TypedDict, total=False):
    include: List[Literal["content"]]
    """A list of additional fields to include in the response.

    Currently the only supported value is `content` to fetch the PEM content of the
    certificate.
    """
