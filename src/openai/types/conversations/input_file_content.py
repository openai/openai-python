# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["InputFileContent"]


class InputFileContent(BaseModel):
    file_id: Optional[str] = None
    """The ID of the file to be sent to the model."""

    type: Literal["input_file"]
    """The type of the input item. Always `input_file`."""

    file_url: Optional[str] = None
    """The URL of the file to be sent to the model."""

    filename: Optional[str] = None
    """The name of the file to be sent to the model."""
