# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ProjectCreateParams"]


class ProjectCreateParams(TypedDict, total=False):
    name: Required[str]
    """The friendly name of the project, this name appears in reports."""

    external_key_id: Optional[str]
    """External key ID to associate with the project."""

    geography: Optional[str]
    """Create the project with the specified data residency region.

    Your organization must have access to Data residency functionality in order to
    use. See
    [data residency controls](https://platform.openai.com/docs/guides/your-data#data-residency-controls)
    to review the functionality and limitations of setting this field. Deprecated:
    use `residency` instead. Do not provide both `geography` and `residency`.
    """

    residency: Optional[
        Literal[
            "GLOBAL",
            "US_STORAGE_PROCESSING",
            "EU_STORAGE_PROCESSING",
            "JP_STORAGE",
            "KR_STORAGE",
            "CA_STORAGE",
            "SG_STORAGE",
            "IN_STORAGE",
            "AU_STORAGE",
            "GB_STORAGE",
            "AE_STORAGE",
            "AE_STORAGE_PROCESSING",
        ]
    ]
    """Create the project with the specified residency configuration.

    Your organization must have access to the requested residency configuration in
    order to use it. See
    [data residency controls](https://platform.openai.com/docs/guides/your-data#data-residency-controls)
    to review the functionality and limitations of setting this field.
    """
