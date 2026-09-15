# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .credential_auth_rotate_param import CredentialAuthRotateParam

__all__ = ["CredentialUpdateParams"]


class CredentialUpdateParams(TypedDict, total=False):
    vault_id: Required[str]

    auth: Required[CredentialAuthRotateParam]
    """Replacement values for the credential's existing authentication method."""
