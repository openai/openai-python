# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseMcpListToolsInProgressEvent"]


class ResponseMcpListToolsInProgressEvent(BaseModel):
    type: Literal["response.mcp_list_tools.in_progress"]
    """The type of the event. Always 'response.mcp_list_tools.in_progress'."""
