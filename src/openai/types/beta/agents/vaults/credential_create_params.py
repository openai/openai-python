# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .credential_auth_create_param import CredentialAuthCreateParam

__all__ = ["CredentialCreateParams"]


class CredentialCreateParams(TypedDict, total=False):
    auth: Required[CredentialAuthCreateParam]
    """The authentication method and secret values to store for the MCP server."""

    name: Required[str]
    """The name is trimmed before storage.

    It must contain 1 to 256 UTF-8 bytes after trimming.
    """
