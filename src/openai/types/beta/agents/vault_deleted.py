# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["VaultDeleted"]


class VaultDeleted(BaseModel):
    """Confirmation that a vault was deleted."""

    id: str
    """The ID of the deleted vault."""

    deleted: bool
    """Whether the resource was deleted. Always `true`."""

    object: Literal["vault.deleted"]
    """The object type. Always `vault.deleted`."""
