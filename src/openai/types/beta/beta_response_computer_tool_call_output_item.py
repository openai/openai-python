# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_response_computer_tool_call_output_screenshot import BetaResponseComputerToolCallOutputScreenshot

__all__ = ["BetaResponseComputerToolCallOutputItem", "AcknowledgedSafetyCheck", "Agent"]


class AcknowledgedSafetyCheck(BaseModel):
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


class BetaResponseComputerToolCallOutputItem(BaseModel):
    id: str
    """The unique ID of the computer call tool output."""

    call_id: str
    """The ID of the computer tool call that produced the output."""

    output: BetaResponseComputerToolCallOutputScreenshot
    """A computer screenshot image used with the computer use tool."""

    status: Literal["completed", "incomplete", "failed", "in_progress"]
    """The status of the message input.

    One of `in_progress`, `completed`, or `incomplete`. Populated when input items
    are returned via API.
    """

    type: Literal["computer_call_output"]
    """The type of the computer tool call output. Always `computer_call_output`."""

    acknowledged_safety_checks: Optional[List[AcknowledgedSafetyCheck]] = None
    """
    The safety checks reported by the API that have been acknowledged by the
    developer.
    """

    agent: Optional[Agent] = None
    """The agent that produced this item."""

    created_by: Optional[str] = None
    """The identifier of the actor that created the item."""
