# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["OrganizationDataRetention"]


class OrganizationDataRetention(BaseModel):
    """Represents the organization's data retention control setting."""

    object: Literal["organization.data_retention"]
    """The object type, which is always `organization.data_retention`."""

    type: Literal[
        "zero_data_retention",
        "modified_abuse_monitoring",
        "enhanced_zero_data_retention",
        "enhanced_modified_abuse_monitoring",
    ]
    """The configured organization data retention type."""
