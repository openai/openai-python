# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ProjectSpendAlertDeleted"]


class ProjectSpendAlertDeleted(BaseModel):
    """Confirmation payload returned after deleting a project spend alert."""

    id: str
    """The deleted spend alert ID."""

    deleted: bool
    """Whether the spend alert was deleted."""

    object: Literal["project.spend_alert.deleted"]
    """Always `project.spend_alert.deleted`."""
