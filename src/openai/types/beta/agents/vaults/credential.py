# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel
from .credential_auth import CredentialAuth

__all__ = ["Credential"]


class Credential(BaseModel):
    """Metadata for a stored MCP server credential. Secret values are never returned."""

    id: str
    """The ID of the credential."""

    auth: CredentialAuth
    """The authentication method and non-secret configuration for the MCP server."""

    created_at: int
    """The Unix timestamp, in seconds, when the credential was created."""

    name: str
    """The human-readable name of the credential."""

    object: Literal["vault.credential"]
    """The object type. Always `vault.credential`."""

    updated_at: int
    """The Unix timestamp, in seconds, when the credential was last updated."""

    vault_id: str
    """The ID of the vault containing this credential."""
