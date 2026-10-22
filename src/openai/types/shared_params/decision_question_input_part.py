# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import TypeAlias

from .decision_input_json import DecisionInputJSON
from .decision_question_input_text import DecisionQuestionInputText
from .decision_question_input_image import DecisionQuestionInputImage

__all__ = ["DecisionQuestionInputPart"]

DecisionQuestionInputPart: TypeAlias = Union[DecisionQuestionInputText, DecisionQuestionInputImage, DecisionInputJSON]
