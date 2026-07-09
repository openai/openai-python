# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from .beta_computer_action_param import BetaComputerActionParam
from .beta_computer_action_list_param import BetaComputerActionListParam

__all__ = ["BetaResponseComputerToolCallParam", "PendingSafetyCheck", "Agent"]


class PendingSafetyCheck(TypedDict, total=False):
    """A pending safety check for the computer call."""

    id: Required[str]
    """The ID of the pending safety check."""

    code: Optional[str]
    """The type of the pending safety check."""

    message: Optional[str]
    """Details about the pending safety check."""


class Agent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class BetaResponseComputerToolCallParam(TypedDict, total=False):
    """A tool call to a computer use tool.

    See the
    [computer use guide](https://platform.openai.com/docs/guides/tools-computer-use) for more information.
    """

    id: Required[str]
    """The unique ID of the computer call."""

    call_id: Required[str]
    """An identifier used when responding to the tool call with output."""

    pending_safety_checks: Required[Iterable[PendingSafetyCheck]]
    """The pending safety checks for the computer call."""

    status: Required[Literal["in_progress", "completed", "incomplete"]]
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """

    type: Required[Literal["computer_call"]]
    """The type of the computer call. Always `computer_call`."""

    action: BetaComputerActionParam
    """A click action."""

    actions: BetaComputerActionListParam
    """Flattened batched actions for `computer_use`.

    Each action includes an `type` discriminator and action-specific fields.
    """

    agent: Optional[Agent]
    """The agent that produced this item."""
