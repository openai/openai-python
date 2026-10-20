# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import TypedDict

__all__ = ["VaultCreateParams"]


class VaultCreateParams(TypedDict, total=False):
    metadata: Optional[Dict[str, str]]
    """
    Key-value pairs to associate with the vault, such as an application or team
    identifier.
    """

    name: str
    """The name is trimmed before storage.

    It must contain 1 to 256 UTF-8 bytes after trimming.
    """
