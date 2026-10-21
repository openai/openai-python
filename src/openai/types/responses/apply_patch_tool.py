# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ApplyPatchTool"]


class ApplyPatchTool(BaseModel):
    """Allows the assistant to create, delete, or update files using unified diffs."""

    type: Literal["apply_patch"]
    """The type of the tool. Always `apply_patch`."""

    allowed_callers: Optional[List[Literal["direct", "programmatic"]]] = None
    """The tool invocation context(s)."""
