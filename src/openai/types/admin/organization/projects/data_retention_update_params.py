# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["DataRetentionUpdateParams"]


class DataRetentionUpdateParams(TypedDict, total=False):
    retention_type: Required[
        Literal[
            "organization_default",
            "none",
            "zero_data_retention",
            "modified_abuse_monitoring",
            "enhanced_zero_data_retention",
            "enhanced_modified_abuse_monitoring",
        ]
    ]
    """The desired project data retention type."""
