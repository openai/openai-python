# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseMcpCallFailedEvent"]


class ResponseMcpCallFailedEvent(BaseModel):
    type: Literal["response.mcp_call.failed"]
    """The type of the event. Always 'response.mcp_call.failed'."""
