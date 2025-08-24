# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["FileCitationBody"]


class FileCitationBody(BaseModel):
    file_id: str
    """The ID of the file."""

    filename: str
    """The filename of the file cited."""

    index: int
    """The index of the file in the list of files."""

    type: Literal["file_citation"]
    """The type of the file citation. Always `file_citation`."""
