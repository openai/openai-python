# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["McpToolCallErrorParam", "McpProtocolError", "McpToolExecutionError", "HTTPError"]


class McpProtocolError(TypedDict, total=False):
    code: Required[int]

    message: Required[str]

    type: Required[Literal["mcp_protocol_error"]]


class McpToolExecutionError(TypedDict, total=False):
    content: Required[object]

    type: Required[Literal["mcp_tool_execution_error"]]


class HTTPError(TypedDict, total=False):
    code: Required[int]

    message: Required[str]

    type: Required[Literal["http_error"]]


McpToolCallErrorParam: TypeAlias = Union[McpProtocolError, McpToolExecutionError, HTTPError]
