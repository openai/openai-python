# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .agent_output_item_status import AgentOutputItemStatus
from .agent_session_message_content import AgentSessionMessageContent

__all__ = ["AgentSessionMessage"]


class AgentSessionMessage(BaseModel):
    """A user or assistant message recorded in a session."""

    id: Optional[str] = None
    """
    The ID of this item, or null for legacy user messages whose ID was not recorded.
    """

    content: List[AgentSessionMessageContent]
    """The content of the message.

    User messages contain input text or images; assistant messages contain output
    text.
    """

    phase: Optional[Literal["commentary", "final_answer"]] = None
    """The phase of an assistant message.

    - `commentary` - Commentary produced while the agent works.
    - `final_answer` - The agent's final answer.
    """

    role: Literal["user", "assistant"]
    """The role of the message author."""

    status: AgentOutputItemStatus
    """The status of the message. User messages are always `completed`."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["message"]
    """The item type. Always `message`."""

    @property
    def output_text(self) -> str:
        """Join all `output_text` content blocks, returning an empty string if none exist."""
        return "".join(content.text for content in self.content if content.type == "output_text")
