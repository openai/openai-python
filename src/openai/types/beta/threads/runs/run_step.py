# File generated from our OpenAPI spec by Stainless.

import builtins
from typing import Union, Optional
from typing_extensions import Literal

from ....._models import BaseModel
from .tool_calls_step_details import ToolCallsStepDetails
from .message_creation_step_details import MessageCreationStepDetails

__all__ = ["RunStep", "LastError", "StepDetails"]


class LastError(BaseModel):
    code: Literal["server_error", "rate_limit_exceeded"]
    """One of `server_error` or `rate_limit_exceeded`."""

    message: str
    """A human-readable description of the error."""


StepDetails = Union[MessageCreationStepDetails, ToolCallsStepDetails]


class RunStep(BaseModel):
    id: str
    """The identifier of the run step, which can be referenced in API endpoints."""

    assistant_id: str
    """
    The ID of the
    [Assistant](https://platform.openai.com/docs/api-reference/assistants)
    associated with the Run Step.
    """

    cancelled_at: Optional[int]
    """The Unix timestamp (in seconds) for when the Run Step was cancelled."""

    completed_at: Optional[int]
    """The Unix timestamp (in seconds) for when the Run Step was completed."""

    created_at: int
    """The Unix timestamp (in seconds) for when the Run Step was created."""

    expired_at: Optional[int]
    """The Unix timestamp (in seconds) for when the Run Step expired.

    A step is considered expired if the parent Run is expired.
    """

    failed_at: Optional[int]
    """The Unix timestamp (in seconds) for when the Run Step failed."""

    last_error: Optional[LastError]
    """The last error associated with this Run Step.

    Will be `null` if there are no errors.
    """

    metadata: Optional[builtins.object]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format. Keys can be a maximum of 64 characters long and values can be
    a maxium of 512 characters long.
    """

    object: Literal["assistant.run.step"]
    """The object type, which is always `assistant.run.step``."""

    run_id: str
    """
    The ID of the [Run](https://platform.openai.com/docs/api-reference/runs) that
    this Run Step is a part of.
    """

    status: Literal["in_progress", "cancelled", "failed", "completed", "expired"]
    """
    The status of the run, which can be either `in_progress`, `cancelled`, `failed`,
    `completed`, or `expired`.
    """

    step_details: StepDetails
    """The details of the activity the Run Step was involved in."""

    thread_id: str
    """
    The ID of the [Thread](https://platform.openai.com/docs/api-reference/threads)
    that was Run.
    """

    type: Literal["message_creation", "tool_calls"]
    """The type of Run Step, which can be either `message_creation` or `tool_calls`."""
