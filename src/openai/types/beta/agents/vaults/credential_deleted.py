# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["CredentialDeleted"]


class CredentialDeleted(BaseModel):
    """Confirmation that a vault credential was deleted."""

    id: str
    """The ID of the deleted credential."""

    deleted: bool
    """Whether the resource was deleted. Always `true`."""

    object: Literal["vault.credential.deleted"]
    """The object type. Always `vault.credential.deleted`."""
