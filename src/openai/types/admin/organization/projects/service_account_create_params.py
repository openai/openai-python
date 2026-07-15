# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ServiceAccountCreateParams"]


class ServiceAccountCreateParams(TypedDict, total=False):
    name: Required[str]
    """The name of the service account being created."""
