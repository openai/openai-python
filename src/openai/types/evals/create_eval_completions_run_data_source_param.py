# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..shared_params.metadata import Metadata
from ..responses.easy_input_message_param import EasyInputMessageParam
from ..responses.response_input_text_param import ResponseInputTextParam

__all__ = [
    "CreateEvalCompletionsRunDataSourceParam",
    "Source",
    "SourceFileContent",
    "SourceFileContentContent",
    "SourceFileID",
    "SourceStoredCompletions",
    "InputMessages",
    "InputMessagesTemplate",
    "InputMessagesTemplateTemplate",
    "InputMessagesTemplateTemplateMessage",
    "InputMessagesTemplateTemplateMessageContent",
    "InputMessagesTemplateTemplateMessageContentOutputText",
    "InputMessagesItemReference",
    "SamplingParams",
]


class SourceFileContentContent(TypedDict, total=False):
    item: Required[Dict[str, object]]

    sample: Dict[str, object]


class SourceFileContent(TypedDict, total=False):
    content: Required[Iterable[SourceFileContentContent]]
    """The content of the jsonl file."""

    type: Required[Literal["file_content"]]
    """The type of jsonl source. Always `file_content`."""


class SourceFileID(TypedDict, total=False):
    id: Required[str]
    """The identifier of the file."""

    type: Required[Literal["file_id"]]
    """The type of jsonl source. Always `file_id`."""


class SourceStoredCompletions(TypedDict, total=False):
    type: Required[Literal["stored_completions"]]
    """The type of source. Always `stored_completions`."""

    created_after: Optional[int]
    """An optional Unix timestamp to filter items created after this time."""

    created_before: Optional[int]
    """An optional Unix timestamp to filter items created before this time."""

    limit: Optional[int]
    """An optional maximum number of items to return."""

    metadata: Optional[Metadata]
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with
    a maximum length of 512 characters.
    """

    model: Optional[str]
    """An optional model to filter by (e.g., 'gpt-4o')."""


Source: TypeAlias = Union[SourceFileContent, SourceFileID, SourceStoredCompletions]


class InputMessagesTemplateTemplateMessageContentOutputText(TypedDict, total=False):
    text: Required[str]
    """The text output from the model."""

    type: Required[Literal["output_text"]]
    """The type of the output text. Always `output_text`."""


InputMessagesTemplateTemplateMessageContent: TypeAlias = Union[
    str, ResponseInputTextParam, InputMessagesTemplateTemplateMessageContentOutputText
]


class InputMessagesTemplateTemplateMessage(TypedDict, total=False):
    content: Required[InputMessagesTemplateTemplateMessageContent]
    """Text inputs to the model - can contain template strings."""

    role: Required[Literal["user", "assistant", "system", "developer"]]
    """The role of the message input.

    One of `user`, `assistant`, `system`, or `developer`.
    """

    type: Literal["message"]
    """The type of the message input. Always `message`."""


InputMessagesTemplateTemplate: TypeAlias = Union[EasyInputMessageParam, InputMessagesTemplateTemplateMessage]


class InputMessagesTemplate(TypedDict, total=False):
    template: Required[Iterable[InputMessagesTemplateTemplate]]
    """A list of chat messages forming the prompt or context.

    May include variable references to the "item" namespace, ie {{item.name}}.
    """

    type: Required[Literal["template"]]
    """The type of input messages. Always `template`."""


class InputMessagesItemReference(TypedDict, total=False):
    item_reference: Required[str]
    """A reference to a variable in the "item" namespace. Ie, "item.name" """

    type: Required[Literal["item_reference"]]
    """The type of input messages. Always `item_reference`."""


InputMessages: TypeAlias = Union[InputMessagesTemplate, InputMessagesItemReference]


class SamplingParams(TypedDict, total=False):
    max_completion_tokens: int
    """The maximum number of tokens in the generated output."""

    seed: int
    """A seed value to initialize the randomness, during sampling."""

    temperature: float
    """A higher temperature increases randomness in the outputs."""

    top_p: float
    """An alternative to temperature for nucleus sampling; 1.0 includes all tokens."""


class CreateEvalCompletionsRunDataSourceParam(TypedDict, total=False):
    source: Required[Source]
    """A StoredCompletionsRunDataSource configuration describing a set of filters"""

    type: Required[Literal["completions"]]
    """The type of run data source. Always `completions`."""

    input_messages: InputMessages

    model: str
    """The name of the model to use for generating completions (e.g. "o3-mini")."""

    sampling_params: SamplingParams
