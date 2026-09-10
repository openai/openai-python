# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .output_text import OutputText
from .agent_output_item_status import AgentOutputItemStatus

__all__ = ["AgentSessionAssistantMessage"]


class AgentSessionAssistantMessage(BaseModel):
    """An assistant message produced by the agent."""

    id: str
    """The ID of the message."""

    content: List[OutputText]
    """The content of the message."""

    phase: Optional[Literal["commentary", "final_answer"]] = None
    """The phase of an assistant message.

    - `commentary` - Commentary produced while the agent works.
    - `final_answer` - The agent's final answer.
    """

    role: Literal["assistant"]
    """The role of the message author. Always `assistant`."""

    status: AgentOutputItemStatus
    """The status of the message."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["message"]
    """The item type. Always `message`."""
