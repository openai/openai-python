# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["Role"]


class Role(BaseModel):
    """Details about a role that can be assigned through the public Roles API."""

    id: str
    """Identifier for the role."""

    description: Optional[str] = None
    """Optional description of the role."""

    name: str
    """Unique name for the role."""

    object: Literal["role"]
    """Always `role`."""

    permissions: List[str]
    """Permissions granted by the role."""

    predefined_role: bool
    """Whether the role is predefined and managed by OpenAI."""

    resource_type: str
    """
    Resource type the role is bound to (for example `api.organization` or
    `api.project`).
    """
