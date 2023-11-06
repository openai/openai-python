# File generated from our OpenAPI spec by Stainless.

import builtins
from typing import Dict, List, Union, Optional
from typing_extensions import Literal

from ...._models import BaseModel
from .required_action_function_tool_call import RequiredActionFunctionToolCall

__all__ = [
    "Run",
    "LastError",
    "RequiredAction",
    "RequiredActionSubmitToolOutputs",
    "Tool",
    "ToolAssistantToolsCode",
    "ToolAssistantToolsRetrieval",
    "ToolAssistantToolsFunction",
    "ToolAssistantToolsFunctionFunction",
]


class LastError(BaseModel):
    code: Literal["server_error", "rate_limit_exceeded"]
    """One of `server_error` or `rate_limit_exceeded`."""

    message: str
    """A human-readable description of the error."""


class RequiredActionSubmitToolOutputs(BaseModel):
    tool_calls: List[RequiredActionFunctionToolCall]
    """A list of the relevant tool calls."""


class RequiredAction(BaseModel):
    submit_tool_outputs: RequiredActionSubmitToolOutputs
    """Details on the tool outputs needed for this run to continue."""

    type: Literal["submit_tool_outputs"]
    """For now, this is always `submit_tool_outputs`."""


class ToolAssistantToolsCode(BaseModel):
    type: Literal["code_interpreter"]
    """The type of tool being defined: `code_interpreter`"""


class ToolAssistantToolsRetrieval(BaseModel):
    type: Literal["retrieval"]
    """The type of tool being defined: `retrieval`"""


class ToolAssistantToolsFunctionFunction(BaseModel):
    description: str
    """
    A description of what the function does, used by the model to choose when and
    how to call the function.
    """

    name: str
    """The name of the function to be called.

    Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length
    of 64.
    """

    parameters: Dict[str, builtins.object]
    """The parameters the functions accepts, described as a JSON Schema object.

    See the [guide](https://platform.openai.com/docs/guides/gpt/function-calling)
    for examples, and the
    [JSON Schema reference](https://json-schema.org/understanding-json-schema/) for
    documentation about the format.

    To describe a function that accepts no parameters, provide the value
    `{"type": "object", "properties": {}}`.
    """


class ToolAssistantToolsFunction(BaseModel):
    function: ToolAssistantToolsFunctionFunction
    """The function definition."""

    type: Literal["function"]
    """The type of tool being defined: `function`"""


Tool = Union[ToolAssistantToolsCode, ToolAssistantToolsRetrieval, ToolAssistantToolsFunction]


class Run(BaseModel):
    id: str
    """The identifier, which can be referenced in API endpoints."""

    assistant_id: str
    """
    The ID of the
    [assistant](https://platform.openai.com/docs/api-reference/assistants) used for
    execution of this run.
    """

    cancelled_at: Optional[int]
    """The Unix timestamp (in seconds) for when the run was cancelled."""

    completed_at: Optional[int]
    """The Unix timestamp (in seconds) for when the run was completed."""

    created_at: int
    """The Unix timestamp (in seconds) for when the run was created."""

    expires_at: int
    """The Unix timestamp (in seconds) for when the run will expire."""

    failed_at: Optional[int]
    """The Unix timestamp (in seconds) for when the run failed."""

    file_ids: List[str]
    """
    The list of [File](https://platform.openai.com/docs/api-reference/files) IDs the
    [assistant](https://platform.openai.com/docs/api-reference/assistants) used for
    this run.
    """

    instructions: str
    """
    The instructions that the
    [assistant](https://platform.openai.com/docs/api-reference/assistants) used for
    this run.
    """

    last_error: Optional[LastError]
    """The last error associated with this run. Will be `null` if there are no errors."""

    metadata: Optional[builtins.object]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format. Keys can be a maximum of 64 characters long and values can be
    a maxium of 512 characters long.
    """

    model: str
    """
    The model that the
    [assistant](https://platform.openai.com/docs/api-reference/assistants) used for
    this run.
    """

    object: Literal["assistant.run"]
    """The object type, which is always `assistant.run`."""

    required_action: Optional[RequiredAction]
    """Details on the action required to continue the run.

    Will be `null` if no action is required.
    """

    started_at: Optional[int]
    """The Unix timestamp (in seconds) for when the run was started."""

    status: Literal[
        "queued", "in_progress", "requires_action", "cancelling", "cancelled", "failed", "completed", "expired"
    ]
    """
    The status of the run, which can be either `queued`, `in_progress`,
    `requires_action`, `cancelling`, `cancelled`, `failed`, `completed`, or
    `expired`.
    """

    thread_id: str
    """
    The ID of the [thread](https://platform.openai.com/docs/api-reference/threads)
    that was executed on as a part of this run.
    """

    tools: List[Tool]
    """
    The list of tools that the
    [assistant](https://platform.openai.com/docs/api-reference/assistants) used for
    this run.
    """
