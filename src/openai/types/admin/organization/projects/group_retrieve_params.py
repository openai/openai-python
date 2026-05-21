# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["GroupRetrieveParams"]


class GroupRetrieveParams(TypedDict, total=False):
    project_id: Required[str]

    group_type: Literal["group", "tenant_group"]
    """The type of group to retrieve."""
