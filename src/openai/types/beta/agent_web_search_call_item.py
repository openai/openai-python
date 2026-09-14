# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .web_search_action import WebSearchAction
from .agent_output_item_status import AgentOutputItemStatus

__all__ = ["AgentWebSearchCallItem"]


class AgentWebSearchCallItem(BaseModel):
    """A web search call produced by the agent."""

    id: str
    """The ID of the web search call."""

    action: Optional[WebSearchAction] = None
    """An action performed by the web search tool."""

    status: AgentOutputItemStatus
    """The status of the web search call."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["web_search_call"]
    """The item type. Always `web_search_call`."""
