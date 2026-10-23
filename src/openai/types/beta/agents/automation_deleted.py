# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["AutomationDeleted"]


class AutomationDeleted(BaseModel):
    id: str
    """The deleted automation ID."""

    deleted: bool
    """Always true."""

    object: Literal["agent.automation.deleted"]
    """Always `agent.automation.deleted`."""
