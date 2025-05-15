# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["EvalJSONLFileContentSource", "Content"]


class Content(BaseModel):
    item: Dict[str, object]

    sample: Optional[Dict[str, object]] = None


class EvalJSONLFileContentSource(BaseModel):
    content: List[Content]
    """The content of the jsonl file."""

    type: Literal["file_content"]
    """The type of jsonl source. Always `file_content`."""
