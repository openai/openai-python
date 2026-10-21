# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_computer_action import BetaComputerAction
from .beta_computer_action_list import BetaComputerActionList

__all__ = ["BetaResponseComputerToolCall", "PendingSafetyCheck", "Agent"]


class PendingSafetyCheck(BaseModel):
    """A pending safety check for the computer call."""

    id: str
    """The ID of the pending safety check."""

    code: Optional[str] = None
    """The type of the pending safety check."""

    message: Optional[str] = None
    """Details about the pending safety check."""


class Agent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseComputerToolCall(BaseModel):
    """A tool call to a computer use tool.

    See the
    [computer use guide](https://platform.openai.com/docs/guides/tools-computer-use) for more information.
    """

    id: str
    """The unique ID of the computer call."""

    call_id: str
    """An identifier used when responding to the tool call with output."""

    pending_safety_checks: List[PendingSafetyCheck]
    """The pending safety checks for the computer call."""

    status: Literal["in_progress", "completed", "incomplete"]
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """

    type: Literal["computer_call"]
    """The type of the computer call. Always `computer_call`."""

    action: Optional[BetaComputerAction] = None
    """A click action."""

    actions: Optional[BetaComputerActionList] = None
    """Flattened batched actions for `computer_use`.

    Each action includes an `type` discriminator and action-specific fields.
    """

    agent: Optional[Agent] = None
    """The agent that produced this item."""
