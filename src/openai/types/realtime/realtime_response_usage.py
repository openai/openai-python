# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .realtime_response_usage_input_token_details import RealtimeResponseUsageInputTokenDetails
from .realtime_response_usage_output_token_details import RealtimeResponseUsageOutputTokenDetails

__all__ = ["RealtimeResponseUsage"]


class RealtimeResponseUsage(BaseModel):
    input_token_details: Optional[RealtimeResponseUsageInputTokenDetails] = None
    """Details about the input tokens used in the Response."""

    input_tokens: Optional[int] = None
    """
    The number of input tokens used in the Response, including text and audio
    tokens.
    """

    output_token_details: Optional[RealtimeResponseUsageOutputTokenDetails] = None
    """Details about the output tokens used in the Response."""

    output_tokens: Optional[int] = None
    """
    The number of output tokens sent in the Response, including text and audio
    tokens.
    """

    total_tokens: Optional[int] = None
    """
    The total number of tokens in the Response including input and output text and
    audio tokens.
    """
