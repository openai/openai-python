from typing import Optional

from .._models import BaseModel

__all__ = ["BatchRequestOutput", "BatchRequestOutputError", "BatchRequestOutputResponse"]


class BatchRequestOutputError(BaseModel):
    code: Optional[str] = None
    """A machine-readable error code."""

    message: Optional[str] = None
    """A human-readable error message."""


class BatchRequestOutputResponse(BaseModel):
    status_code: int
    """The HTTP status code of the response."""

    request_id: str
    """An unique identifier for the request."""

    body: Optional[object] = None
    """The JSON body of the response."""


class BatchRequestOutput(BaseModel):
    id: str
    """The ID of the batch request."""

    custom_id: str
    """A developer-provided per-request id that will be used to match outputs to inputs."""

    response: Optional[BatchRequestOutputResponse] = None

    error: Optional[BatchRequestOutputError] = None
