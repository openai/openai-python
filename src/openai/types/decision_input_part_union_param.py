# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import TypeAlias

from .decision_input_text_param import DecisionInputTextParam
from .decision_input_image_param import DecisionInputImageParam

__all__ = ["DecisionInputPartUnionParam"]

DecisionInputPartUnionParam: TypeAlias = Union[DecisionInputTextParam, DecisionInputImageParam]
