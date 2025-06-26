# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = ["ResponseFunctionWebSearch", "Action", "ActionSearch", "ActionOpenPage", "ActionFind"]


class ActionSearch(BaseModel):
    query: str
    """The search query."""

    type: Literal["search"]
    """The action type."""


class ActionOpenPage(BaseModel):
    type: Literal["open_page"]
    """The action type."""

    url: str
    """The URL opened by the model."""


class ActionFind(BaseModel):
    pattern: str
    """The pattern or text to search for within the page."""

    type: Literal["find"]
    """The action type."""

    url: str
    """The URL of the page searched for the pattern."""


Action: TypeAlias = Annotated[Union[ActionSearch, ActionOpenPage, ActionFind], PropertyInfo(discriminator="type")]


class ResponseFunctionWebSearch(BaseModel):
    id: str
    """The unique ID of the web search tool call."""

    action: Action
    """
    An object describing the specific action taken in this web search call. Includes
    details on how the model used the web (search, open_page, find).
    """

    status: Literal["in_progress", "searching", "completed", "failed"]
    """The status of the web search tool call."""

    type: Literal["web_search_call"]
    """The type of the web search tool call. Always `web_search_call`."""
