# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel
from .run_status import RunStatus
from ..assistant_tool import AssistantTool
from .required_action_function_tool_call import RequiredActionFunctionToolCall

__all__ = ["Run", "LastError", "RequiredAction", "RequiredActionSubmitToolOutputs", "Usage"]


class LastError(BaseModel):
    code: Literal["server_error", "rate_limit_exceeded", "invalid_prompt"]
    """One of `server_error`, `rate_limit_exceeded`, or `invalid_prompt`."""

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


class Usage(BaseModel):
    completion_tokens: int
    """Number of completion tokens used over the course of the run."""

    prompt_tokens: int
    """Number of prompt tokens used over the course of the run."""

    total_tokens: int
    """Total number of tokens used (prompt + completion)."""


class Run(BaseModel):
    id: str
    """The identifier, which can be referenced in API endpoints."""

    assistant_id: str
    """
    The ID of the
    [assistant](https://platform.openai.com/docs/api-reference/assistants) used for
    execution of this run.
    """

    cancelled_at: Optional[int] = None
    """The Unix timestamp (in seconds) for when the run was cancelled."""

    completed_at: Optional[int] = None
    """The Unix timestamp (in seconds) for when the run was completed."""

    created_at: int
    """The Unix timestamp (in seconds) for when the run was created."""

    expires_at: Optional[int] = None
    """The Unix timestamp (in seconds) for when the run will expire."""

    failed_at: Optional[int] = None
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

    last_error: Optional[LastError] = None
    """The last error associated with this run. Will be `null` if there are no errors."""

    metadata: Optional[object] = None
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

    object: Literal["thread.run"]
    """The object type, which is always `thread.run`."""

    required_action: Optional[RequiredAction] = None
    """Details on the action required to continue the run.

    Will be `null` if no action is required.
    """

    started_at: Optional[int] = None
    """The Unix timestamp (in seconds) for when the run was started."""

    status: RunStatus
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

    tools: List[AssistantTool]
    """
    The list of tools that the
    [assistant](https://platform.openai.com/docs/api-reference/assistants) used for
    this run.
    """

    usage: Optional[Usage] = None
    """Usage statistics related to the run.

    This value will be `null` if the run is not in a terminal state (i.e.
    `in_progress`, `queued`, etc.).
    """
