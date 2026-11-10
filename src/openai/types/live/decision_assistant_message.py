# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = ["DecisionAssistantMessage", "ContentPart", "ContentPartOutputText", "ContentPartRefusal"]


class ContentPartOutputText(BaseModel):
    text: str
    """The text content."""

    type: Literal["output_text"]


class ContentPartRefusal(BaseModel):
    refusal: str
    """The refusal text."""

    type: Literal["refusal"]


ContentPart: TypeAlias = Annotated[Union[ContentPartOutputText, ContentPartRefusal], PropertyInfo(discriminator="type")]


class DecisionAssistantMessage(BaseModel):
    content: Union[str, List[ContentPart]]
    """The text input to the model."""

    role: Literal["assistant"]

    id: Optional[str] = None
    """The unique ID of this message item."""

    phase: Optional[Literal["commentary", "final_answer"]] = None
    """
    Labels an `assistant` message as intermediate commentary (`commentary`) or the
    final answer (`final_answer`). For models like `gpt-5.3-codex` and beyond, when
    sending follow-up requests, preserve and resend phase on all assistant messages
    — dropping it can degrade performance. Not used for user messages.
    """

    type: Optional[Literal["message"]] = None
