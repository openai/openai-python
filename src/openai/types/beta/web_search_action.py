# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "WebSearchAction",
    "WebSearchActionResourceSearch",
    "WebSearchActionResourceOpenPage",
    "WebSearchActionResourceFindInPage",
    "WebSearchActionResourceOther",
]


class WebSearchActionResourceSearch(BaseModel):
    """A search query or group of search queries."""

    queries: Optional[List[str]] = None
    """The search queries, when multiple queries were used."""

    query: Optional[str] = None
    """The search query, when a single query was used."""

    type: Literal["search"]
    """The type of the object. Always `search`."""


class WebSearchActionResourceOpenPage(BaseModel):
    """Opens a web page."""

    type: Literal["open_page"]
    """The type of the object. Always `open_page`."""

    url: Optional[str] = None
    """The URL of the page that was opened."""


class WebSearchActionResourceFindInPage(BaseModel):
    """Finds text within a web page."""

    pattern: Optional[str] = None
    """The text pattern that was searched for."""

    type: Literal["find_in_page"]
    """The type of the object. Always `find_in_page`."""

    url: Optional[str] = None
    """The URL of the page that was searched."""


class WebSearchActionResourceOther(BaseModel):
    """Another web search action."""

    type: Literal["other"]
    """The type of the object. Always `other`."""


WebSearchAction: TypeAlias = Annotated[
    Union[
        WebSearchActionResourceSearch,
        WebSearchActionResourceOpenPage,
        WebSearchActionResourceFindInPage,
        WebSearchActionResourceOther,
    ],
    PropertyInfo(discriminator="type"),
]
