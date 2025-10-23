# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["WebSearchTool", "Filters", "UserLocation"]


class Filters(BaseModel):
    allowed_domains: Optional[List[str]] = None
    """Allowed domains for the search.

    If not provided, all domains are allowed. Subdomains of the provided domains are
    allowed as well.

    Example: `["pubmed.ncbi.nlm.nih.gov"]`
    """


class UserLocation(BaseModel):
    city: Optional[str] = None
    """Free text input for the city of the user, e.g. `San Francisco`."""

    country: Optional[str] = None
    """
    The two-letter [ISO country code](https://en.wikipedia.org/wiki/ISO_3166-1) of
    the user, e.g. `US`.
    """

    region: Optional[str] = None
    """Free text input for the region of the user, e.g. `California`."""

    timezone: Optional[str] = None
    """
    The [IANA timezone](https://timeapi.io/documentation/iana-timezones) of the
    user, e.g. `America/Los_Angeles`.
    """

    type: Optional[Literal["approximate"]] = None
    """The type of location approximation. Always `approximate`."""


class WebSearchTool(BaseModel):
    type: Literal["web_search", "web_search_2025_08_26"]
    """The type of the web search tool.

    One of `web_search` or `web_search_2025_08_26`.
    """

    filters: Optional[Filters] = None
    """Filters for the search."""

    search_context_size: Optional[Literal["low", "medium", "high"]] = None
    """High level guidance for the amount of context window space to use for the
    search.

    One of `low`, `medium`, or `high`. `medium` is the default.
    """

    user_location: Optional[UserLocation] = None
    """The approximate location of the user."""
