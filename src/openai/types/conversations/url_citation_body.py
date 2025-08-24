# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["URLCitationBody"]


class URLCitationBody(BaseModel):
    end_index: int
    """The index of the last character of the URL citation in the message."""

    start_index: int
    """The index of the first character of the URL citation in the message."""

    title: str
    """The title of the web resource."""

    type: Literal["url_citation"]
    """The type of the URL citation. Always `url_citation`."""

    url: str
    """The URL of the web resource."""
