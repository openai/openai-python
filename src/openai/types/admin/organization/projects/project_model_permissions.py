# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["ProjectModelPermissions"]


class ProjectModelPermissions(BaseModel):
    """Represents the model allowlist or denylist policy for a project."""

    mode: Literal["allow_list", "deny_list"]
    """Whether the project uses an allowlist or a denylist."""

    api_model_ids: List[str] = FieldInfo(alias="model_ids")
    """The model IDs included in the model permissions policy."""

    object: Literal["project.model_permissions"]
    """The object type, which is always `project.model_permissions`."""
