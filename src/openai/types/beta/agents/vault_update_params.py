# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import TypedDict

__all__ = ["VaultUpdateParams"]


class VaultUpdateParams(TypedDict, total=False):
    metadata: Dict[str, str]
    """Replaces all metadata.

    Omit to leave unchanged, or pass {} to clear it. Up to 16 string key-value
    pairs, with keys up to 64 and values up to 512 characters.
    """

    name: Optional[str]
    """A replacement name.

    Omit to leave unchanged, or pass null to clear it. The name is trimmed before
    storage. It must contain 1 to 256 UTF-8 bytes after trimming.
    """
