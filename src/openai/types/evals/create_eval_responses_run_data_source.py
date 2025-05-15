# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from ..shared.eval_item import EvalItem
from ..shared.reasoning_effort import ReasoningEffort
from .eval_jsonl_file_id_source import EvalJSONLFileIDSource
from .eval_jsonl_file_content_source import EvalJSONLFileContentSource

__all__ = [
    "CreateEvalResponsesRunDataSource",
    "Source",
    "SourceResponses",
    "InputMessages",
    "InputMessagesTemplate",
    "InputMessagesTemplateTemplate",
    "InputMessagesTemplateTemplateChatMessage",
    "InputMessagesItemReference",
    "SamplingParams",
]


class SourceResponses(BaseModel):
    type: Literal["responses"]
    """The type of run data source. Always `responses`."""

    created_after: Optional[int] = None
    """Only include items created after this timestamp (inclusive).

    This is a query parameter used to select responses.
    """

    created_before: Optional[int] = None
    """Only include items created before this timestamp (inclusive).

    This is a query parameter used to select responses.
    """

    has_tool_calls: Optional[bool] = None
    """Whether the response has tool calls.

    This is a query parameter used to select responses.
    """

    instructions_search: Optional[str] = None
    """Optional string to search the 'instructions' field.

    This is a query parameter used to select responses.
    """

    metadata: Optional[object] = None
    """Metadata filter for the responses.

    This is a query parameter used to select responses.
    """

    model: Optional[str] = None
    """The name of the model to find responses for.

    This is a query parameter used to select responses.
    """

    reasoning_effort: Optional[ReasoningEffort] = None
    """Optional reasoning effort parameter.

    This is a query parameter used to select responses.
    """

    temperature: Optional[float] = None
    """Sampling temperature. This is a query parameter used to select responses."""

    tools: Optional[List[str]] = None
    """List of tool names. This is a query parameter used to select responses."""

    top_p: Optional[float] = None
    """Nucleus sampling parameter. This is a query parameter used to select responses."""

    users: Optional[List[str]] = None
    """List of user identifiers. This is a query parameter used to select responses."""


Source: TypeAlias = Annotated[
    Union[EvalJSONLFileContentSource, EvalJSONLFileIDSource, SourceResponses], PropertyInfo(discriminator="type")
]


class InputMessagesTemplateTemplateChatMessage(BaseModel):
    content: str
    """The content of the message."""

    role: str
    """The role of the message (e.g. "system", "assistant", "user")."""


InputMessagesTemplateTemplate: TypeAlias = Union[InputMessagesTemplateTemplateChatMessage, EvalItem]


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


class SamplingParams(BaseModel):
    max_completion_tokens: Optional[int] = None
    """The maximum number of tokens in the generated output."""

    seed: Optional[int] = None
    """A seed value to initialize the randomness, during sampling."""

    temperature: Optional[float] = None
    """A higher temperature increases randomness in the outputs."""

    top_p: Optional[float] = None
    """An alternative to temperature for nucleus sampling; 1.0 includes all tokens."""


class CreateEvalResponsesRunDataSource(BaseModel):
    source: Source
    """A EvalResponsesSource object describing a run data source configuration."""

    type: Literal["responses"]
    """The type of run data source. Always `responses`."""

    input_messages: Optional[InputMessages] = None

    model: Optional[str] = None
    """The name of the model to use for generating completions (e.g. "o3-mini")."""

    sampling_params: Optional[SamplingParams] = None
