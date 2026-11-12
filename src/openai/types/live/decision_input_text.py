# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["DecisionInputText"]


class DecisionInputText(BaseModel):
    text: str
    """The text input to the model."""

    type: Literal["input_text"]
