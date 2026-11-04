# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["WorkloadIdentityProviderListParams"]


class WorkloadIdentityProviderListParams(TypedDict, total=False):
    after: str

    limit: int

    order: Literal["asc", "desc"]
