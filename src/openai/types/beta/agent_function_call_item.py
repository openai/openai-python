# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .agent_function_call_status import AgentFunctionCallStatus

__all__ = ["AgentFunctionCallItem"]


class AgentFunctionCallItem(BaseModel):
    """A function call produced by the agent."""

    id: str
    """The ID of the function call item."""

    arguments: object
    """The arguments to pass to the function."""

    call_id: str
    """The ID used to submit the function result."""

    name: str
    """The name of the function to call."""

    status: AgentFunctionCallStatus
    """The status of the function call."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["function_call"]
    """The item type. Always `function_call`."""
