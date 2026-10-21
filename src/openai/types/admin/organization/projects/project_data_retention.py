# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ProjectDataRetention"]


class ProjectDataRetention(BaseModel):
    """Represents a project's data retention control setting."""

    object: Literal["project.data_retention"]
    """The object type, which is always `project.data_retention`."""

    type: Literal[
        "organization_default",
        "none",
        "zero_data_retention",
        "modified_abuse_monitoring",
        "enhanced_zero_data_retention",
        "enhanced_modified_abuse_monitoring",
    ]
    """The configured project data retention type."""
