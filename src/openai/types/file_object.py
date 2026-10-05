# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["FileObject"]


class FileObject(BaseModel):
    """The `File` object represents a document that has been uploaded to OpenAI."""

    id: str
    """The file identifier, which can be referenced in the API endpoints."""

    bytes: int
    """The size of the file, in bytes.

    In a completed file upload response, this can be null when the file size is not
    yet available.
    """

    created_at: int
    """The Unix timestamp (in seconds) for when the file was created."""

    filename: str
    """The name of the file."""

    object: Literal["file"]
    """The object type, which is always `file`."""

    purpose: Literal[
        "assistants",
        "assistants_output",
        "batch",
        "batch_output",
        "fine-tune",
        "fine-tune-results",
        "vision",
        "user_data",
    ]
    """The intended purpose of the file.

    Supported values are `assistants`, `assistants_output`, `batch`, `batch_output`,
    `fine-tune`, `fine-tune-results`, `vision`, and `user_data`.
    """

    status: Literal["uploaded", "processed", "error"]
    """Deprecated.

    The current status of the file, which can be either `uploaded`, `processed`, or
    `error`.
    """

    expires_at: Optional[int] = None
    """The Unix timestamp (in seconds) for when the file will expire.

    In a completed file upload response, this can be null when no expiry is set.
    """

    status_details: Optional[str] = None
    """Deprecated.

    For details on why a fine-tuning training file failed validation, see the
    `error` field on `fine_tuning.job`. Completed file upload responses can return
    null when these details are unset.
    """
