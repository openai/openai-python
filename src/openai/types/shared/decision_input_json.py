# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["DecisionInputJSON"]


class DecisionInputJSON(BaseModel):
    """A JSON object or an array of objects rendered as text.

    Nested values may be any JSON value. Limited to 32 container levels, 10,000 values, and 256 KiB of compact UTF-8 JSON.
    """

    data: Union[List[Dict[str, Optional[object]]], Dict[str, Optional[object]]]

    type: Literal["input_json"]
