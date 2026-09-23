# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseError", "Misalignment", "MisalignmentSteer"]


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


class ResponseError(BaseModel):
    """An error object returned when the model fails to generate a Response."""

    code: Literal[
        "server_error",
        "rate_limit_exceeded",
        "invalid_prompt",
        "data_residency_mismatch",
        "bio_policy",
        "misalignment_policy_violation",
        "vector_store_timeout",
        "invalid_image",
        "invalid_image_format",
        "invalid_base64_image",
        "invalid_image_url",
        "image_too_large",
        "image_too_small",
        "image_parse_error",
        "image_content_policy_violation",
        "invalid_image_mode",
        "image_file_too_large",
        "unsupported_image_media_type",
        "empty_image_file",
        "failed_to_download_image",
        "image_file_not_found",
    ]
    """The error code for the response."""

    message: str
    """A human-readable description of the error."""

    misalignment: Optional[Misalignment] = None
