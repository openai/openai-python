# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .decision_input_text import DecisionInputText

__all__ = ["DecisionDeveloperMessage"]


class DecisionDeveloperMessage(BaseModel):
    content: Union[str, List[DecisionInputText]]
    """The text input to the model."""

    role: Literal["developer"]

    id: Optional[str] = None
    """The unique ID of this message item."""

    type: Optional[Literal["message"]] = None
