# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["OrganizationSpendLimitDeleted"]


class OrganizationSpendLimitDeleted(BaseModel):
    """Confirmation payload returned after deleting an organization hard spend limit."""

    deleted: bool
    """Whether the hard spend limit was deleted."""

    object: Literal["organization.spend_limit.deleted"]
    """The object type, which is always `organization.spend_limit.deleted`."""
