# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["ResponseFunctionWebSearchParam", "Action", "ActionSearch", "ActionOpenPage", "ActionFind"]


class ActionSearch(TypedDict, total=False):
    query: Required[str]
    """The search query."""

    type: Required[Literal["search"]]
    """The action type."""


class ActionOpenPage(TypedDict, total=False):
    type: Required[Literal["open_page"]]
    """The action type."""

    url: Required[str]
    """The URL opened by the model."""


class ActionFind(TypedDict, total=False):
    pattern: Required[str]
    """The pattern or text to search for within the page."""

    type: Required[Literal["find"]]
    """The action type."""

    url: Required[str]
    """The URL of the page searched for the pattern."""


Action: TypeAlias = Union[ActionSearch, ActionOpenPage, ActionFind]


class ResponseFunctionWebSearchParam(TypedDict, total=False):
    id: Required[str]
    """The unique ID of the web search tool call."""

    action: Required[Action]
    """
    An object describing the specific action taken in this web search call. Includes
    details on how the model used the web (search, open_page, find).
    """

    status: Required[Literal["in_progress", "searching", "completed", "failed"]]
    """The status of the web search tool call."""

    type: Required[Literal["web_search_call"]]
    """The type of the web search tool call. Always `web_search_call`."""
