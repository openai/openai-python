# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from ..shared.metadata import Metadata

__all__ = [
    "CreateEvalCompletionsRunDataSource",
    "InputMessages",
    "InputMessagesTemplate",
    "InputMessagesTemplateTemplate",
    "InputMessagesTemplateTemplateChatMessage",
    "InputMessagesTemplateTemplateInputMessage",
    "InputMessagesTemplateTemplateInputMessageContent",
    "InputMessagesTemplateTemplateOutputMessage",
    "InputMessagesTemplateTemplateOutputMessageContent",
    "InputMessagesItemReference",
    "Source",
    "SourceFileContent",
    "SourceFileContentContent",
    "SourceFileID",
    "SourceStoredCompletions",
    "SamplingParams",
]


class InputMessagesTemplateTemplateChatMessage(BaseModel):
    content: str
    """The content of the message."""

    role: str
    """The role of the message (e.g. "system", "assistant", "user")."""


class InputMessagesTemplateTemplateInputMessageContent(BaseModel):
    text: str
    """The text content."""

    type: Literal["input_text"]
    """The type of content, which is always `input_text`."""


class InputMessagesTemplateTemplateInputMessage(BaseModel):
    content: InputMessagesTemplateTemplateInputMessageContent

    role: Literal["user", "system", "developer"]
    """The role of the message. One of `user`, `system`, or `developer`."""

    type: Literal["message"]
    """The type of item, which is always `message`."""


class InputMessagesTemplateTemplateOutputMessageContent(BaseModel):
    text: str
    """The text content."""

    type: Literal["output_text"]
    """The type of content, which is always `output_text`."""


class InputMessagesTemplateTemplateOutputMessage(BaseModel):
    content: InputMessagesTemplateTemplateOutputMessageContent

    role: Literal["assistant"]
    """The role of the message. Must be `assistant` for output."""

    type: Literal["message"]
    """The type of item, which is always `message`."""


InputMessagesTemplateTemplate: TypeAlias = Union[
    InputMessagesTemplateTemplateChatMessage,
    InputMessagesTemplateTemplateInputMessage,
    InputMessagesTemplateTemplateOutputMessage,
]


class InputMessagesTemplate(BaseModel):
    template: List[InputMessagesTemplateTemplate]
    """A list of chat messages forming the prompt or context.

    May include variable references to the "item" namespace, ie {{item.name}}.
    """

    type: Literal["template"]
    """The type of input messages. Always `template`."""


class InputMessagesItemReference(BaseModel):
    item_reference: str
    """A reference to a variable in the "item" namespace. Ie, "item.name" """

    type: Literal["item_reference"]
    """The type of input messages. Always `item_reference`."""


InputMessages: TypeAlias = Annotated[
    Union[InputMessagesTemplate, InputMessagesItemReference], PropertyInfo(discriminator="type")
]


class SourceFileContentContent(BaseModel):
    item: Dict[str, object]

    sample: Optional[Dict[str, object]] = None


class SourceFileContent(BaseModel):
    content: List[SourceFileContentContent]
    """The content of the jsonl file."""

    type: Literal["file_content"]
    """The type of jsonl source. Always `file_content`."""


class SourceFileID(BaseModel):
    id: str
    """The identifier of the file."""

    type: Literal["file_id"]
    """The type of jsonl source. Always `file_id`."""


class SourceStoredCompletions(BaseModel):
    created_after: Optional[int] = None
    """An optional Unix timestamp to filter items created after this time."""

    created_before: Optional[int] = None
    """An optional Unix timestamp to filter items created before this time."""

    limit: Optional[int] = None
    """An optional maximum number of items to return."""

    metadata: Optional[Metadata] = None
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with
    a maximum length of 512 characters.
    """

    model: Optional[str] = None
    """An optional model to filter by (e.g., 'gpt-4o')."""

    type: Literal["stored_completions"]
    """The type of source. Always `stored_completions`."""


Source: TypeAlias = Annotated[
    Union[SourceFileContent, SourceFileID, SourceStoredCompletions], PropertyInfo(discriminator="type")
]


class SamplingParams(BaseModel):
    max_completion_tokens: Optional[int] = None
    """The maximum number of tokens in the generated output."""

    seed: Optional[int] = None
    """A seed value to initialize the randomness, during sampling."""

    temperature: Optional[float] = None
    """A higher temperature increases randomness in the outputs."""

    top_p: Optional[float] = None
    """An alternative to temperature for nucleus sampling; 1.0 includes all tokens."""


class CreateEvalCompletionsRunDataSource(BaseModel):
    input_messages: InputMessages

    model: str
    """The name of the model to use for generating completions (e.g. "o3-mini")."""

    source: Source
    """A StoredCompletionsRunDataSource configuration describing a set of filters"""

    type: Literal["completions"]
    """The type of run data source. Always `completions`."""

    sampling_params: Optional[SamplingParams] = None
