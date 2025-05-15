# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..shared_params.metadata import Metadata
from ..shared_params.eval_item import EvalItem
from .eval_jsonl_file_id_source_param import EvalJSONLFileIDSourceParam
from ..responses.easy_input_message_param import EasyInputMessageParam
from .eval_jsonl_file_content_source_param import EvalJSONLFileContentSourceParam

__all__ = [
    "CreateEvalCompletionsRunDataSourceParam",
    "Source",
    "SourceStoredCompletions",
    "InputMessages",
    "InputMessagesTemplate",
    "InputMessagesTemplateTemplate",
    "InputMessagesItemReference",
    "SamplingParams",
]


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


Source: TypeAlias = Union[EvalJSONLFileContentSourceParam, EvalJSONLFileIDSourceParam, SourceStoredCompletions]

InputMessagesTemplateTemplate: TypeAlias = Union[EasyInputMessageParam, EvalItem]


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
