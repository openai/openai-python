# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

from .credential_auth_rotate_param import CredentialAuthRotateParam

__all__ = ["CredentialUpdateParams"]


class CredentialUpdateParams(TypedDict, total=False):
    vault_id: Required[str]

    auth: CredentialAuthRotateParam
    """Replacement values for the credential's existing authentication method."""

    metadata: Dict[str, str]
    """Replaces all metadata.

    Omit to preserve it, or pass {} to clear it. Up to 16 string key-value pairs,
    with keys up to 64 and values up to 512 characters.
    """
