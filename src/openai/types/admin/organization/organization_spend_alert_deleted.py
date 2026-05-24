# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["OrganizationSpendAlertDeleted"]


class OrganizationSpendAlertDeleted(BaseModel):
    """Confirmation payload returned after deleting an organization spend alert."""

    id: str
    """The deleted spend alert ID."""

    deleted: bool
    """Whether the spend alert was deleted."""

    object: Literal["organization.spend_alert.deleted"]
    """Always `organization.spend_alert.deleted`."""
