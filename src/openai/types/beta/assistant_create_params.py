# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..._types import SequenceNotStr
from ..shared.chat_model import ChatModel
from .assistant_tool_param import AssistantToolParam
from ..shared_params.metadata import Metadata
from ..shared.reasoning_effort import ReasoningEffort
from .assistant_response_format_option_param import AssistantResponseFormatOptionParam

__all__ = [
    "AssistantCreateParams",
    "ToolResources",
    "ToolResourcesCodeInterpreter",
    "ToolResourcesFileSearch",
    "ToolResourcesFileSearchVectorStore",
    "ToolResourcesFileSearchVectorStoreChunkingStrategy",
    "ToolResourcesFileSearchVectorStoreChunkingStrategyAuto",
    "ToolResourcesFileSearchVectorStoreChunkingStrategyStatic",
    "ToolResourcesFileSearchVectorStoreChunkingStrategyStaticStatic",
]


class AssistantCreateParams(TypedDict, total=False):
    model: Required[Union[str, ChatModel]]
    """ID of the model to use.

    You can use the
    [List models](https://developers.openai.com/api/reference/resources/models/methods/list)
    API to see all of your available models, or see our
    [Model overview](https://developers.openai.com/api/docs/models) for descriptions
    of them.

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

    description: Optional[str]
    """The description of the assistant. The maximum length is 512 characters."""

    instructions: Optional[str]
    """The system instructions that the assistant uses.

    The maximum length is 256,000 characters.
    """

    metadata: Optional[Metadata]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with
    a maximum length of 512 characters.
    """

    name: Optional[str]
    """The name of the assistant. The maximum length is 256 characters."""

    reasoning_effort: Optional[ReasoningEffort]
    """Constrains effort on reasoning for reasoning models.

    Currently supported values are `none`, `minimal`, `low`, `medium`, `high`,
    `xhigh`, and `max`. Reducing reasoning effort can result in faster responses and
    fewer tokens used on reasoning in a response. Not all reasoning models support
    every value. See the
    [reasoning guide](https://developers.openai.com/api/docs/guides/reasoning) for
    model-specific support.
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

    tool_resources: Optional[ToolResources]
    """A set of resources that are used by the assistant's tools.

    The resources are specific to the type of tool. For example, the
    `code_interpreter` tool requires a list of file IDs, while the `file_search`
    tool requires a list of vector store IDs.
    """

    tools: Iterable[AssistantToolParam]
    """A list of tool enabled on the assistant.

    There can be a maximum of 128 tools per assistant. Tools can be of types
    `code_interpreter`, `file_search`, or `function`.
    """

    top_p: Optional[float]
    """
    An alternative to sampling with temperature, called nucleus sampling, where the
    model considers the results of the tokens with top_p probability mass. So 0.1
    means only the tokens comprising the top 10% probability mass are considered.

    We generally recommend altering this or temperature but not both.
    """


class ToolResourcesCodeInterpreter(TypedDict, total=False):
    file_ids: SequenceNotStr[str]
    """
    A list of [file](https://developers.openai.com/api/reference/resources/files)
    IDs made available to the `code_interpreter` tool. There can be a maximum of 20
    files associated with the tool.
    """


class ToolResourcesFileSearchVectorStoreChunkingStrategyAuto(TypedDict, total=False):
    """The default strategy.

    This strategy currently uses a `max_chunk_size_tokens` of `800` and `chunk_overlap_tokens` of `400`.
    """

    type: Required[Literal["auto"]]
    """Always `auto`."""


class ToolResourcesFileSearchVectorStoreChunkingStrategyStaticStatic(TypedDict, total=False):
    chunk_overlap_tokens: Required[int]
    """The number of tokens that overlap between chunks. The default value is `400`.

    Note that the overlap must not exceed half of `max_chunk_size_tokens`.
    """

    max_chunk_size_tokens: Required[int]
    """The maximum number of tokens in each chunk.

    The default value is `800`. The minimum value is `100` and the maximum value is
    `4096`.
    """


class ToolResourcesFileSearchVectorStoreChunkingStrategyStatic(TypedDict, total=False):
    static: Required[ToolResourcesFileSearchVectorStoreChunkingStrategyStaticStatic]

    type: Required[Literal["static"]]
    """Always `static`."""


ToolResourcesFileSearchVectorStoreChunkingStrategy: TypeAlias = Union[
    ToolResourcesFileSearchVectorStoreChunkingStrategyAuto, ToolResourcesFileSearchVectorStoreChunkingStrategyStatic
]


class ToolResourcesFileSearchVectorStore(TypedDict, total=False):
    chunking_strategy: ToolResourcesFileSearchVectorStoreChunkingStrategy
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


class ToolResourcesFileSearch(TypedDict, total=False):
    vector_store_ids: SequenceNotStr[str]
    """
    The
    [vector store](https://developers.openai.com/api/reference/resources/vector_stores)
    attached to this assistant. There can be a maximum of 1 vector store attached to
    the assistant.
    """

    vector_stores: Iterable[ToolResourcesFileSearchVectorStore]
    """
    A helper to create a
    [vector store](https://developers.openai.com/api/reference/resources/vector_stores)
    with file_ids and attach it to this assistant. There can be a maximum of 1
    vector store attached to the assistant.
    """


class ToolResources(TypedDict, total=False):
    """A set of resources that are used by the assistant's tools.

    The resources are specific to the type of tool. For example, the `code_interpreter` tool requires a list of file IDs, while the `file_search` tool requires a list of vector store IDs.
    """

    code_interpreter: ToolResourcesCodeInterpreter

    file_search: ToolResourcesFileSearch
