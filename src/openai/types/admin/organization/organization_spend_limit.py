# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["OrganizationSpendLimit", "Enforcement"]


class Enforcement(BaseModel):
    """The current enforcement state of the hard spend limit."""

    status: Union[str, Literal["inactive", "enforcing"]]
    """Whether the hard spend limit is currently enforcing."""


class OrganizationSpendLimit(BaseModel):
    """Represents a hard spend limit configured at the organization level."""

    currency: Union[str, Literal["USD"]]
    """The currency for the threshold amount. Currently, only `USD` is supported."""

    enforcement: Enforcement
    """The current enforcement state of the hard spend limit."""

    interval: Union[str, Literal["month"]]
    """The time interval for evaluating spend against the threshold.

    Currently, only `month` is supported.
    """

    object: Literal["organization.spend_limit"]
    """The object type, which is always `organization.spend_limit`."""

    threshold_amount: int
    """The hard spend limit amount, in cents."""
