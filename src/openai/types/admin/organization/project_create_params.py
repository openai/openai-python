# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ProjectCreateParams"]


class ProjectCreateParams(TypedDict, total=False):
    name: Required[str]
    """The friendly name of the project, this name appears in reports."""

    geography: Literal["US", "EU", "JP", "IN", "KR", "CA", "AU", "SG"]
    """Create the project with the specified data residency region.

    Your organization must have access to Data residency functionality in order to
    use. See
    [data residency controls](https://platform.openai.com/docs/guides/your-data#data-residency-controls)
    to review the functionality and limitations of setting this field.
    """
