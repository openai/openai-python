# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import TypedDict

__all__ = ["SessionUpdateParams"]


class SessionUpdateParams(TypedDict, total=False):
    metadata: Optional[Dict[str, str]]
    """Replaces all metadata.

    Omit to leave unchanged, or pass null or {} to clear it. Up to 16 string
    key-value pairs, with keys up to 64 and values up to 512 characters.
    """
