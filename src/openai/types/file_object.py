# File generated from our OpenAPI spec by Stainless.

from typing import Optional

from .._models import BaseModel

__all__ = ["FileObject"]


class FileObject(BaseModel):
    id: str
    """The file identifier, which can be referenced in the API endpoints."""

    bytes: int
    """The size of the file in bytes."""

    created_at: int
    """The Unix timestamp (in seconds) for when the file was created."""

    filename: str
    """The name of the file."""

    object: str
    """The object type, which is always "file"."""

    purpose: str
    """The intended purpose of the file. Currently, only "fine-tune" is supported."""

    status: Optional[str] = None
    """
    The current status of the file, which can be either `uploaded`, `processed`,
    `pending`, `error`, `deleting` or `deleted`.
    """

    status_details: Optional[str] = None
    """Additional details about the status of the file.

    If the file is in the `error` state, this will include a message describing the
    error.
    """
