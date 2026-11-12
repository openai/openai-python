# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["SafetyCase", "Notice"]


class Notice(BaseModel):
    type: Literal["warning", "deactivation"]


class SafetyCase(BaseModel):
    id: str

    created_at: int

    entity_identifier: str

    notice: Notice

    object: Literal["safety.case"]

    reason: Optional[str] = None
