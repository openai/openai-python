# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["SessionError"]


class SessionError(BaseModel):
    """An error payload with the same public fields as Responses API streaming errors."""

    code: Optional[str] = None
    """The machine-readable error code, if any."""

    message: str
    """A customer-safe explanation of the error."""

    param: Optional[str] = None
    """The request parameter associated with the error, if any."""

    type: str
    """The error type."""
