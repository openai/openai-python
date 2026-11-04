# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DecisionInputJSON"]


class DecisionInputJSON(TypedDict, total=False):
    """A JSON object or an array of objects rendered as text.

    Nested values may be any JSON value. Limited to 32 container levels, 10,000 values, and 256 KiB of compact UTF-8 JSON.
    """

    data: Required[Union[Dict[str, Optional[object]], Iterable[Dict[str, Optional[object]]]]]

    type: Required[Literal["input_json"]]
