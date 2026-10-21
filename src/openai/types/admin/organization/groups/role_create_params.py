# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["RoleCreateParams"]


class RoleCreateParams(TypedDict, total=False):
    role_id: Required[str]
    """Identifier of the role to assign."""
