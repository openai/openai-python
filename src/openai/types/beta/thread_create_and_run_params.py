# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from .function_tool_param import FunctionToolParam
from .retrieval_tool_param import RetrievalToolParam
from .code_interpreter_tool_param import CodeInterpreterToolParam

__all__ = [
    "ThreadCreateAndRunParamsBase",
    "Thread",
    "ThreadMessage",
    "Tool",
    "ThreadCreateAndRunParamsNonStreaming",
    "ThreadCreateAndRunParamsStreaming",
]


class ThreadCreateAndRunParamsBase(TypedDict, total=False):
    assistant_id: Required[str]
    """
    The ID of the
    [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to
    execute this run.
    """

    instructions: Optional[str]
    """Override the default system message of the assistant.

    This is useful for modifying the behavior on a per-run basis.
    """

    metadata: Optional[object]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format. Keys can be a maximum of 64 characters long and values can be
    a maxium of 512 characters long.
    """

    model: Optional[str]
    """
    The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
    be used to execute this run. If a value is provided here, it will override the
    model associated with the assistant. If not, the model associated with the
    assistant will be used.
    """

    thread: Thread
    """If no thread is provided, an empty thread will be created."""

    tools: Optional[Iterable[Tool]]
    """Override the tools the assistant can use for this run.

    This is useful for modifying the behavior on a per-run basis.
    """


class ThreadMessage(TypedDict, total=False):
    content: Required[str]
    """The content of the message."""

    role: Required[Literal["user"]]
    """The role of the entity that is creating the message.

    Currently only `user` is supported.
    """

    file_ids: List[str]
    """
    A list of [File](https://platform.openai.com/docs/api-reference/files) IDs that
    the message should use. There can be a maximum of 10 files attached to a
    message. Useful for tools like `retrieval` and `code_interpreter` that can
    access and use files.
    """

    metadata: Optional[object]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format. Keys can be a maximum of 64 characters long and values can be
    a maxium of 512 characters long.
    """


class Thread(TypedDict, total=False):
    messages: Iterable[ThreadMessage]
    """
    A list of [messages](https://platform.openai.com/docs/api-reference/messages) to
    start the thread with.
    """

    metadata: Optional[object]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format. Keys can be a maximum of 64 characters long and values can be
    a maxium of 512 characters long.
    """


Tool = Union[CodeInterpreterToolParam, RetrievalToolParam, FunctionToolParam]


class ThreadCreateAndRunParamsNonStreaming(ThreadCreateAndRunParamsBase):
    stream: Optional[Literal[False]]
    """
    If `true`, returns a stream of events that happen during the Run as server-sent
    events, terminating when the Run enters a terminal state with a `data: [DONE]`
    message.
    """


class ThreadCreateAndRunParamsStreaming(ThreadCreateAndRunParamsBase):
    stream: Required[Literal[True]]
    """
    If `true`, returns a stream of events that happen during the Run as server-sent
    events, terminating when the Run enters a terminal state with a `data: [DONE]`
    message.
    """


ThreadCreateAndRunParams = Union[ThreadCreateAndRunParamsNonStreaming, ThreadCreateAndRunParamsStreaming]
