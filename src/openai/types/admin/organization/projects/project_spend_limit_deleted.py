# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ProjectSpendLimitDeleted"]


class ProjectSpendLimitDeleted(BaseModel):
    """Confirmation payload returned after deleting a project hard spend limit."""

    deleted: bool
    """Whether the hard spend limit was deleted."""

    object: Literal["project.spend_limit.deleted"]
    """The object type, which is always `project.spend_limit.deleted`."""
