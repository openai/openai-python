# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .decision_input_json import DecisionInputJSON
from .decision_question_input_text import DecisionQuestionInputText
from .decision_question_input_image import DecisionQuestionInputImage

__all__ = ["DecisionQuestionInputPart"]

DecisionQuestionInputPart: TypeAlias = Annotated[
    Union[DecisionQuestionInputText, DecisionQuestionInputImage, DecisionInputJSON], PropertyInfo(discriminator="type")
]
