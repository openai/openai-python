# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "BetaResponseSteerRequiredInput",
    "FunctionCallOutput",
    "CustomToolCallOutput",
    "ComputerCallOutput",
    "ShellCallOutput",
    "ApplyPatchCallOutput",
    "ToolSearchOutput",
    "McpApprovalResponse",
]


class FunctionCallOutput(BaseModel):
    """Supply `output` using the function tool call output input schema."""

    call_id: str

    name: str

    type: Literal["function_call_output"]


class CustomToolCallOutput(BaseModel):
    """Supply `output` using the custom tool call output input schema.

    The
    original custom tool call supplies the tool's name.
    """

    call_id: str

    type: Literal["custom_tool_call_output"]


class ComputerCallOutput(BaseModel):
    """
    Supply `output` using the computer tool call output input schema,
    including any required `acknowledged_safety_checks`.
    """

    call_id: str

    type: Literal["computer_call_output"]


class ShellCallOutput(BaseModel):
    """Supply `output` using the shell tool call output input schema.

    Each
    output entry includes `stdout`, `stderr`, and `outcome`.
    """

    call_id: str

    type: Literal["shell_call_output"]


class ApplyPatchCallOutput(BaseModel):
    """
    Supply `status` and optional `output` using the apply patch tool call
    output input schema.
    """

    call_id: str

    type: Literal["apply_patch_call_output"]


class ToolSearchOutput(BaseModel):
    """
    Supply `tools` using the tool search output input schema, retaining
    `execution: "client"`.
    """

    call_id: str

    execution: Literal["client"]

    type: Literal["tool_search_output"]


class McpApprovalResponse(BaseModel):
    """Supply `approve` using the MCP approval response input schema.

    An
    optional `reason` can be supplied when denying the request. The original
    approval request identifies the tool and server.
    """

    approval_request_id: str

    type: Literal["mcp_approval_response"]


BetaResponseSteerRequiredInput: TypeAlias = Annotated[
    Union[
        FunctionCallOutput,
        CustomToolCallOutput,
        ComputerCallOutput,
        ShellCallOutput,
        ApplyPatchCallOutput,
        ToolSearchOutput,
        McpApprovalResponse,
    ],
    PropertyInfo(discriminator="type"),
]
