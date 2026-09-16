# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["Error"]


class Error(BaseModel):
    """
    Details of an error encountered by the Live session, including the affected parameter or client command when available.
    """

    code: str
    """
    A machine-readable code identifying the Live error, such as `unknown_parameter`.
    """

    message: str
    """A human-readable explanation of the Live error."""

    type: str
    """
    The category of error, such as `invalid_request_error` for an invalid Live
    client command.
    """

    client_event_id: Optional[str] = None
    """The event_id of the client command that caused the error, when supplied."""

    param: Optional[str] = None
    """The parameter that caused the error, when applicable, such as `session.voice`."""
