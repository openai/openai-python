# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..._types import SequenceNotStr
from ..shared.chat_model import ChatModel
from .assistant_tool_param import AssistantToolParam
from ..shared_params.metadata import Metadata
from .code_interpreter_tool_param import CodeInterpreterToolParam
from .assistant_tool_choice_option_param import AssistantToolChoiceOptionParam
from .threads.message_content_part_param import MessageContentPartParam
from .assistant_response_format_option_param import AssistantResponseFormatOptionParam

__all__ = [
    "ThreadCreateAndRunParamsBase",
    "Thread",
    "ThreadMessage",
    "ThreadMessageAttachment",
    "ThreadMessageAttachmentTool",
    "ThreadMessageAttachmentToolFileSearch",
    "ThreadToolResources",
    "ThreadToolResourcesCodeInterpreter",
    "ThreadToolResourcesFileSearch",
    "ThreadToolResourcesFileSearchVectorStore",
    "ThreadToolResourcesFileSearchVectorStoreChunkingStrategy",
    "ThreadToolResourcesFileSearchVectorStoreChunkingStrategyAuto",
    "ThreadToolResourcesFileSearchVectorStoreChunkingStrategyStatic",
    "ThreadToolResourcesFileSearchVectorStoreChunkingStrategyStaticStatic",
    "ToolResources",
    "ToolResourcesCodeInterpreter",
    "ToolResourcesFileSearch",
    "TruncationStrategy",
    "ThreadCreateAndRunParamsNonStreaming",
    "ThreadCreateAndRunParamsStreaming",
]


class ThreadCreateAndRunParamsBase(TypedDict, total=False):
    assistant_id: Required[str]
    """
    The ID of the
    [assistant](https://developers.openai.com/api/docs/assistants/migration) to use
    to execute this run.
    """

    instructions: Optional[str]
    """Override the default system message of the assistant.

    This is useful for modifying the behavior on a per-run basis.
    """

    max_completion_tokens: Optional[int]
    """
    The maximum number of completion tokens that may be used over the course of the
    run. The run will make a best effort to use only the number of completion tokens
    specified, across multiple turns of the run. If the run exceeds the number of
    completion tokens specified, the run will end with status `incomplete`. See
    `incomplete_details` for more info.
    """

    max_prompt_tokens: Optional[int]
    """The maximum number of prompt tokens that may be used over the course of the run.

    The run will make a best effort to use only the number of prompt tokens
    specified, across multiple turns of the run. If the run exceeds the number of
    prompt tokens specified, the run will end with status `incomplete`. See
    `incomplete_details` for more info.
    """

    metadata: Optional[Metadata]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with
    a maximum length of 512 characters.
    """

    model: Union[str, ChatModel, None]
    """
    The ID of the
    [Model](https://developers.openai.com/api/reference/resources/models) to be used
    to execute this run. If a value is provided here, it will override the model
    associated with the assistant. If not, the model associated with the assistant
    will be used.

    Deprecated values:

    - "gpt-5.4-nano", "gpt-5.4-nano-2026-03-17", "gpt-5.1", "gpt-5.1-2025-11-13":
      Announced shutdown date: 2027-04-01. See
      https://developers.openai.com/api/docs/deprecations for details and
      recommended replacements.
    - "gpt-5.3-chat-latest", "gpt-5.2-chat-latest": Announced shutdown date:
      2026-08-10. See https://developers.openai.com/api/docs/deprecations for
      details and recommended replacements.
    - "gpt-5.1-codex", "gpt-5.1-chat-latest", "gpt-5-chat-latest",
      "gpt-4o-search-preview", "gpt-4o-mini-search-preview",
      "gpt-4o-search-preview-2025-03-11", "gpt-4o-mini-search-preview-2025-03-11":
      Announced shutdown date: 2026-07-23. See
      https://developers.openai.com/api/docs/deprecations for details and
      recommended replacements.
    - "gpt-5.1-mini": Not a supported model ID. Retained for SDK compatibility.
    - "gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-5-2025-08-07",
      "gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07", "o3", "o3-2025-04-16":
      Announced shutdown date: 2026-12-11. See
      https://developers.openai.com/api/docs/deprecations for details and
      recommended replacements.
    - "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14",
      "gpt-4o", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06", "gpt-4o-mini",
      "gpt-4o-mini-2024-07-18": Announced shutdown date: 2027-01-14. See
      https://developers.openai.com/api/docs/deprecations for details and
      recommended replacements.
    - "gpt-4.1-nano", "gpt-4.1-nano-2025-04-14", "o4-mini", "o4-mini-2025-04-16",
      "o3-mini", "o3-mini-2025-01-31", "o1", "o1-2024-12-17", "gpt-4o-2024-05-13",
      "gpt-4-turbo", "gpt-4-turbo-2024-04-09", "gpt-4-1106-preview", "gpt-4",
      "gpt-4-0613", "gpt-3.5-turbo", "gpt-3.5-turbo-0125": Announced shutdown date:
      2026-10-23. See https://developers.openai.com/api/docs/deprecations for
      details and recommended replacements.
    - "o1-preview", "o1-preview-2024-09-12": Announced shutdown date: 2025-07-28.
      See https://developers.openai.com/api/docs/deprecations for details and
      recommended replacements.
    - "o1-mini", "o1-mini-2024-09-12": Announced shutdown date: 2025-10-27. See
      https://developers.openai.com/api/docs/deprecations for details and
      recommended replacements.
    - "gpt-audio-mini", "gpt-audio-mini-2025-12-15": Announced shutdown date:
      2027-01-20. See https://developers.openai.com/api/docs/deprecations for
      details and recommended replacements.
    - "gpt-4o-audio-preview", "gpt-4o-audio-preview-2024-12-17",
      "gpt-4o-audio-preview-2025-06-03", "gpt-4o-mini-audio-preview",
      "gpt-4o-mini-audio-preview-2024-12-17": Announced shutdown date: 2026-05-07.
      See https://developers.openai.com/api/docs/deprecations for details and
      recommended replacements.
    - "gpt-4o-audio-preview-2024-10-01": Announced shutdown date: 2025-10-10. See
      https://developers.openai.com/api/docs/deprecations for details and
      recommended replacements.
    - "chatgpt-4o-latest": Announced shutdown date: 2026-02-17. See
      https://developers.openai.com/api/docs/deprecations for details and
      recommended replacements.
    - "codex-mini-latest": Announced shutdown date: 2026-02-12. See
      https://developers.openai.com/api/docs/deprecations for details and
      recommended replacements.
    - "gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-0314": Announced shutdown
      date: 2026-03-26. See https://developers.openai.com/api/docs/deprecations for
      details and recommended replacements.
    - "gpt-4-vision-preview": Announced shutdown date: 2024-12-06. See
      https://developers.openai.com/api/docs/deprecations for details and
      recommended replacements.
    - "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-0613": Announced shutdown date:
      2025-06-06. See https://developers.openai.com/api/docs/deprecations for
      details and recommended replacements.
    - "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613",
      "gpt-3.5-turbo-16k-0613": Announced shutdown date: 2024-09-13. See
      https://developers.openai.com/api/docs/deprecations for details and
      recommended replacements.
    - "gpt-3.5-turbo-1106": Announced shutdown date: 2026-09-28. See
      https://developers.openai.com/api/docs/deprecations for details and
      recommended replacements.
    """

    parallel_tool_calls: bool
    """
    Whether to enable
    [parallel function calling](https://developers.openai.com/api/docs/guides/function-calling#parallel-function-calling)
    during tool use.
    """

    response_format: Optional[AssistantResponseFormatOptionParam]
    """Specifies the format that the model must output.

    Compatible with [GPT-4o](https://developers.openai.com/api/docs/models/gpt-4o),
    [GPT-4 Turbo](https://developers.openai.com/api/docs/models/gpt-4-turbo), and
    all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

    Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
    Outputs which ensures the model will match your supplied JSON schema. Learn more
    in the
    [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs).

    Setting to `{ "type": "json_object" }` enables JSON mode, which ensures the
    message the model generates is valid JSON.

    **Important:** when using JSON mode, you **must** also instruct the model to
    produce JSON yourself via a system or user message. Without this, the model may
    generate an unending stream of whitespace until the generation reaches the token
    limit, resulting in a long-running and seemingly "stuck" request. Also note that
    the message content may be partially cut off if `finish_reason="length"`, which
    indicates the generation exceeded `max_tokens` or the conversation exceeded the
    max context length.
    """

    temperature: Optional[float]
    """What sampling temperature to use, between 0 and 2.

    Higher values like 0.8 will make the output more random, while lower values like
    0.2 will make it more focused and deterministic.
    """

    thread: Thread
    """Options to create a new thread.

    If no thread is provided when running a request, an empty thread will be
    created.
    """

    tool_choice: Optional[AssistantToolChoiceOptionParam]
    """
    Controls which (if any) tool is called by the model. `none` means the model will
    not call any tools and instead generates a message. `auto` is the default value
    and means the model can pick between generating a message or calling one or more
    tools. `required` means the model must call one or more tools before responding
    to the user. Specifying a particular tool like `{"type": "file_search"}` or
    `{"type": "function", "function": {"name": "my_function"}}` forces the model to
    call that tool.
    """

    tool_resources: Optional[ToolResources]
    """A set of resources that are used by the assistant's tools.

    The resources are specific to the type of tool. For example, the
    `code_interpreter` tool requires a list of file IDs, while the `file_search`
    tool requires a list of vector store IDs.
    """

    tools: Optional[Iterable[AssistantToolParam]]
    """Override the tools the assistant can use for this run.

    This is useful for modifying the behavior on a per-run basis.
    """

    top_p: Optional[float]
    """
    An alternative to sampling with temperature, called nucleus sampling, where the
    model considers the results of the tokens with top_p probability mass. So 0.1
    means only the tokens comprising the top 10% probability mass are considered.

    We generally recommend altering this or temperature but not both.
    """

    truncation_strategy: Optional[TruncationStrategy]
    """Controls for how a thread will be truncated prior to the run.

    Use this to control the initial context window of the run.
    """


class ThreadMessageAttachmentToolFileSearch(TypedDict, total=False):
    type: Required[Literal["file_search"]]
    """The type of tool being defined: `file_search`"""


ThreadMessageAttachmentTool: TypeAlias = Union[CodeInterpreterToolParam, ThreadMessageAttachmentToolFileSearch]


class ThreadMessageAttachment(TypedDict, total=False):
    file_id: str
    """The ID of the file to attach to the message."""

    tools: Iterable[ThreadMessageAttachmentTool]
    """The tools to add this file to."""


class ThreadMessage(TypedDict, total=False):
    content: Required[Union[str, Iterable[MessageContentPartParam]]]
    """The text contents of the message."""

    role: Required[Literal["user", "assistant"]]
    """The role of the entity that is creating the message. Allowed values include:

    - `user`: Indicates the message is sent by an actual user and should be used in
      most cases to represent user-generated messages.
    - `assistant`: Indicates the message is generated by the assistant. Use this
      value to insert messages from the assistant into the conversation.
    """

    attachments: Optional[Iterable[ThreadMessageAttachment]]
    """A list of files attached to the message, and the tools they should be added to."""

    metadata: Optional[Metadata]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with
    a maximum length of 512 characters.
    """


class ThreadToolResourcesCodeInterpreter(TypedDict, total=False):
    file_ids: SequenceNotStr[str]
    """
    A list of [file](https://developers.openai.com/api/reference/resources/files)
    IDs made available to the `code_interpreter` tool. There can be a maximum of 20
    files associated with the tool.
    """


class ThreadToolResourcesFileSearchVectorStoreChunkingStrategyAuto(TypedDict, total=False):
    """The default strategy.

    This strategy currently uses a `max_chunk_size_tokens` of `800` and `chunk_overlap_tokens` of `400`.
    """

    type: Required[Literal["auto"]]
    """Always `auto`."""


class ThreadToolResourcesFileSearchVectorStoreChunkingStrategyStaticStatic(TypedDict, total=False):
    chunk_overlap_tokens: Required[int]
    """The number of tokens that overlap between chunks. The default value is `400`.

    Note that the overlap must not exceed half of `max_chunk_size_tokens`.
    """

    max_chunk_size_tokens: Required[int]
    """The maximum number of tokens in each chunk.

    The default value is `800`. The minimum value is `100` and the maximum value is
    `4096`.
    """


class ThreadToolResourcesFileSearchVectorStoreChunkingStrategyStatic(TypedDict, total=False):
    static: Required[ThreadToolResourcesFileSearchVectorStoreChunkingStrategyStaticStatic]

    type: Required[Literal["static"]]
    """Always `static`."""


ThreadToolResourcesFileSearchVectorStoreChunkingStrategy: TypeAlias = Union[
    ThreadToolResourcesFileSearchVectorStoreChunkingStrategyAuto,
    ThreadToolResourcesFileSearchVectorStoreChunkingStrategyStatic,
]


class ThreadToolResourcesFileSearchVectorStore(TypedDict, total=False):
    chunking_strategy: ThreadToolResourcesFileSearchVectorStoreChunkingStrategy
    """The chunking strategy used to chunk the file(s).

    If not set, will use the `auto` strategy.
    """

    file_ids: SequenceNotStr[str]
    """
    A list of [file](https://developers.openai.com/api/reference/resources/files)
    IDs to add to the vector store. For vector stores created before Nov 2025, there
    can be a maximum of 10,000 files in a vector store. For vector stores created
    starting in Nov 2025, the limit is 100,000,000 files.
    """

    metadata: Optional[Metadata]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with
    a maximum length of 512 characters.
    """


class ThreadToolResourcesFileSearch(TypedDict, total=False):
    vector_store_ids: SequenceNotStr[str]
    """
    The
    [vector store](https://developers.openai.com/api/reference/resources/vector_stores)
    attached to this thread. There can be a maximum of 1 vector store attached to
    the thread.
    """

    vector_stores: Iterable[ThreadToolResourcesFileSearchVectorStore]
    """
    A helper to create a
    [vector store](https://developers.openai.com/api/reference/resources/vector_stores)
    with file_ids and attach it to this thread. There can be a maximum of 1 vector
    store attached to the thread.
    """


class ThreadToolResources(TypedDict, total=False):
    """
    A set of resources that are made available to the assistant's tools in this thread. The resources are specific to the type of tool. For example, the `code_interpreter` tool requires a list of file IDs, while the `file_search` tool requires a list of vector store IDs.
    """

    code_interpreter: ThreadToolResourcesCodeInterpreter

    file_search: ThreadToolResourcesFileSearch


class Thread(TypedDict, total=False):
    """Options to create a new thread.

    If no thread is provided when running a
    request, an empty thread will be created.
    """

    messages: Iterable[ThreadMessage]
    """
    A list of
    [messages](https://developers.openai.com/api/docs/assistants/migration) to start
    the thread with.
    """

    metadata: Optional[Metadata]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with
    a maximum length of 512 characters.
    """

    tool_resources: Optional[ThreadToolResources]
    """
    A set of resources that are made available to the assistant's tools in this
    thread. The resources are specific to the type of tool. For example, the
    `code_interpreter` tool requires a list of file IDs, while the `file_search`
    tool requires a list of vector store IDs.
    """


class ToolResourcesCodeInterpreter(TypedDict, total=False):
    file_ids: SequenceNotStr[str]
    """
    A list of [file](https://developers.openai.com/api/reference/resources/files)
    IDs made available to the `code_interpreter` tool. There can be a maximum of 20
    files associated with the tool.
    """


class ToolResourcesFileSearch(TypedDict, total=False):
    vector_store_ids: SequenceNotStr[str]
    """
    The ID of the
    [vector store](https://developers.openai.com/api/reference/resources/vector_stores)
    attached to this assistant. There can be a maximum of 1 vector store attached to
    the assistant.
    """


class ToolResources(TypedDict, total=False):
    """A set of resources that are used by the assistant's tools.

    The resources are specific to the type of tool. For example, the `code_interpreter` tool requires a list of file IDs, while the `file_search` tool requires a list of vector store IDs.
    """

    code_interpreter: ToolResourcesCodeInterpreter

    file_search: ToolResourcesFileSearch


class TruncationStrategy(TypedDict, total=False):
    """Controls for how a thread will be truncated prior to the run.

    Use this to control the initial context window of the run.
    """

    type: Required[Literal["auto", "last_messages"]]
    """The truncation strategy to use for the thread.

    The default is `auto`. If set to `last_messages`, the thread will be truncated
    to the n most recent messages in the thread. When set to `auto`, messages in the
    middle of the thread will be dropped to fit the context length of the model,
    `max_prompt_tokens`.
    """

    last_messages: Optional[int]
    """
    The number of most recent messages from the thread when constructing the context
    for the run.
    """


class ThreadCreateAndRunParamsNonStreaming(ThreadCreateAndRunParamsBase, total=False):
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
