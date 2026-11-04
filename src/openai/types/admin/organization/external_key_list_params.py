# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["ExternalKeyListParams"]


class ExternalKeyListParams(TypedDict, total=False):
    after: Optional[str]

    limit: int

    order: Literal["asc", "desc"]

    purpose: Literal["ekm", "psp_decryption"]
    """Filter by key purpose. When omitted, returns keys of all purposes."""
