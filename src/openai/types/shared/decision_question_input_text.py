# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["DecisionQuestionInputText"]


class DecisionQuestionInputText(BaseModel):
    text: str

    type: Literal["input_text"]
