# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["EvalJSONLFileIDSource"]


class EvalJSONLFileIDSource(BaseModel):
    id: str
    """The identifier of the file."""

    type: Literal["file_id"]
    """The type of jsonl source. Always `file_id`."""
