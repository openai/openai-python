# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["VideoCreateError", "Misalignment", "MisalignmentSteer"]


class MisalignmentSteer(BaseModel):
    """An optional public continuation instruction."""

    message: str
    """The public continuation instruction."""


class Misalignment(BaseModel):
    detailed_explanation: Optional[str] = None
    """The public explanation for this block."""

    error_type: Union[
        str,
        Literal[
            "potentially_unintended_data_transfer",
            "potentially_unintended_data_access",
            "potentially_unintended_destructive_activity",
            "other",
        ],
        None,
    ] = None
    """An optional classification; clients must accept additional values."""

    steer: Optional[MisalignmentSteer] = None
    """An optional public continuation instruction."""


class VideoCreateError(BaseModel):
    """An error that occurred while generating the response."""

    code: str
    """A machine-readable error code that was returned."""

    message: str
    """A human-readable description of the error that was returned."""

    misalignment: Optional[Misalignment] = None
