# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseInputFileContent"]


class ResponseInputFileContent(BaseModel):
    """A file input to the model."""

    type: Literal["input_file"]
    """The type of the input item. Always `input_file`."""

    detail: Optional[Literal["low", "high"]] = None
    """The detail level of the file to be sent to the model.

    Use `low` for the default rendering behavior, or `high` to render the file at
    higher quality. Defaults to `low`.
    """

    file_data: Optional[str] = None
    """The base64-encoded data of the file to be sent to the model."""

    file_id: Optional[str] = None
    """The ID of the file to be sent to the model."""

    file_url: Optional[str] = None
    """The URL of the file to be sent to the model."""

    filename: Optional[str] = None
    """The name of the file to be sent to the model."""
