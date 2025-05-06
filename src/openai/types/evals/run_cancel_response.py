# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import Field as FieldInfo

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .eval_api_error import EvalAPIError
from ..shared.metadata import Metadata
from ..shared.reasoning_effort import ReasoningEffort
from ..responses.response_input_text import ResponseInputText
from .create_eval_jsonl_run_data_source import CreateEvalJSONLRunDataSource
from .create_eval_completions_run_data_source import CreateEvalCompletionsRunDataSource

__all__ = [
    "RunCancelResponse",
    "DataSource",
    "DataSourceCompletions",
    "DataSourceCompletionsSource",
    "DataSourceCompletionsSourceFileContent",
    "DataSourceCompletionsSourceFileContentContent",
    "DataSourceCompletionsSourceFileID",
    "DataSourceCompletionsSourceResponses",
    "DataSourceCompletionsInputMessages",
    "DataSourceCompletionsInputMessagesTemplate",
    "DataSourceCompletionsInputMessagesTemplateTemplate",
    "DataSourceCompletionsInputMessagesTemplateTemplateChatMessage",
    "DataSourceCompletionsInputMessagesTemplateTemplateEvalItem",
    "DataSourceCompletionsInputMessagesTemplateTemplateEvalItemContent",
    "DataSourceCompletionsInputMessagesTemplateTemplateEvalItemContentOutputText",
    "DataSourceCompletionsInputMessagesItemReference",
    "DataSourceCompletionsSamplingParams",
    "PerModelUsage",
    "PerTestingCriteriaResult",
    "ResultCounts",
]


class DataSourceCompletionsSourceFileContentContent(BaseModel):
    item: Dict[str, object]

    sample: Optional[Dict[str, object]] = None


class DataSourceCompletionsSourceFileContent(BaseModel):
    content: List[DataSourceCompletionsSourceFileContentContent]
    """The content of the jsonl file."""

    type: Literal["file_content"]
    """The type of jsonl source. Always `file_content`."""


class DataSourceCompletionsSourceFileID(BaseModel):
    id: str
    """The identifier of the file."""

    type: Literal["file_id"]
    """The type of jsonl source. Always `file_id`."""


class DataSourceCompletionsSourceResponses(BaseModel):
    type: Literal["responses"]
    """The type of run data source. Always `responses`."""

    allow_parallel_tool_calls: Optional[bool] = None
    """Whether to allow parallel tool calls.

    This is a query parameter used to select responses.
    """

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
    """Optional search string for instructions.

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

    top_p: Optional[float] = None
    """Nucleus sampling parameter. This is a query parameter used to select responses."""

    users: Optional[List[str]] = None
    """List of user identifiers. This is a query parameter used to select responses."""


DataSourceCompletionsSource: TypeAlias = Annotated[
    Union[
        DataSourceCompletionsSourceFileContent, DataSourceCompletionsSourceFileID, DataSourceCompletionsSourceResponses
    ],
    PropertyInfo(discriminator="type"),
]


class DataSourceCompletionsInputMessagesTemplateTemplateChatMessage(BaseModel):
    content: str
    """The content of the message."""

    role: str
    """The role of the message (e.g. "system", "assistant", "user")."""


class DataSourceCompletionsInputMessagesTemplateTemplateEvalItemContentOutputText(BaseModel):
    text: str
    """The text output from the model."""

    type: Literal["output_text"]
    """The type of the output text. Always `output_text`."""


DataSourceCompletionsInputMessagesTemplateTemplateEvalItemContent: TypeAlias = Union[
    str, ResponseInputText, DataSourceCompletionsInputMessagesTemplateTemplateEvalItemContentOutputText
]


class DataSourceCompletionsInputMessagesTemplateTemplateEvalItem(BaseModel):
    content: DataSourceCompletionsInputMessagesTemplateTemplateEvalItemContent
    """Text inputs to the model - can contain template strings."""

    role: Literal["user", "assistant", "system", "developer"]
    """The role of the message input.

    One of `user`, `assistant`, `system`, or `developer`.
    """

    type: Optional[Literal["message"]] = None
    """The type of the message input. Always `message`."""


DataSourceCompletionsInputMessagesTemplateTemplate: TypeAlias = Union[
    DataSourceCompletionsInputMessagesTemplateTemplateChatMessage,
    DataSourceCompletionsInputMessagesTemplateTemplateEvalItem,
]


class DataSourceCompletionsInputMessagesTemplate(BaseModel):
    template: List[DataSourceCompletionsInputMessagesTemplateTemplate]
    """A list of chat messages forming the prompt or context.

    May include variable references to the "item" namespace, ie {{item.name}}.
    """

    type: Literal["template"]
    """The type of input messages. Always `template`."""


class DataSourceCompletionsInputMessagesItemReference(BaseModel):
    item_reference: str
    """A reference to a variable in the "item" namespace. Ie, "item.name" """

    type: Literal["item_reference"]
    """The type of input messages. Always `item_reference`."""


DataSourceCompletionsInputMessages: TypeAlias = Annotated[
    Union[DataSourceCompletionsInputMessagesTemplate, DataSourceCompletionsInputMessagesItemReference],
    PropertyInfo(discriminator="type"),
]


class DataSourceCompletionsSamplingParams(BaseModel):
    max_completion_tokens: Optional[int] = None
    """The maximum number of tokens in the generated output."""

    seed: Optional[int] = None
    """A seed value to initialize the randomness, during sampling."""

    temperature: Optional[float] = None
    """A higher temperature increases randomness in the outputs."""

    top_p: Optional[float] = None
    """An alternative to temperature for nucleus sampling; 1.0 includes all tokens."""


class DataSourceCompletions(BaseModel):
    source: DataSourceCompletionsSource
    """A EvalResponsesSource object describing a run data source configuration."""

    type: Literal["completions"]
    """The type of run data source. Always `completions`."""

    input_messages: Optional[DataSourceCompletionsInputMessages] = None

    model: Optional[str] = None
    """The name of the model to use for generating completions (e.g. "o3-mini")."""

    sampling_params: Optional[DataSourceCompletionsSamplingParams] = None


DataSource: TypeAlias = Annotated[
    Union[CreateEvalJSONLRunDataSource, CreateEvalCompletionsRunDataSource, DataSourceCompletions],
    PropertyInfo(discriminator="type"),
]


class PerModelUsage(BaseModel):
    cached_tokens: int
    """The number of tokens retrieved from cache."""

    completion_tokens: int
    """The number of completion tokens generated."""

    invocation_count: int
    """The number of invocations."""

    run_model_name: str = FieldInfo(alias="model_name")
    """The name of the model."""

    prompt_tokens: int
    """The number of prompt tokens used."""

    total_tokens: int
    """The total number of tokens used."""


class PerTestingCriteriaResult(BaseModel):
    failed: int
    """Number of tests failed for this criteria."""

    passed: int
    """Number of tests passed for this criteria."""

    testing_criteria: str
    """A description of the testing criteria."""


class ResultCounts(BaseModel):
    errored: int
    """Number of output items that resulted in an error."""

    failed: int
    """Number of output items that failed to pass the evaluation."""

    passed: int
    """Number of output items that passed the evaluation."""

    total: int
    """Total number of executed output items."""


class RunCancelResponse(BaseModel):
    id: str
    """Unique identifier for the evaluation run."""

    created_at: int
    """Unix timestamp (in seconds) when the evaluation run was created."""

    data_source: DataSource
    """Information about the run's data source."""

    error: EvalAPIError
    """An object representing an error response from the Eval API."""

    eval_id: str
    """The identifier of the associated evaluation."""

    metadata: Optional[Metadata] = None
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with
    a maximum length of 512 characters.
    """

    model: str
    """The model that is evaluated, if applicable."""

    name: str
    """The name of the evaluation run."""

    object: Literal["eval.run"]
    """The type of the object. Always "eval.run"."""

    per_model_usage: List[PerModelUsage]
    """Usage statistics for each model during the evaluation run."""

    per_testing_criteria_results: List[PerTestingCriteriaResult]
    """Results per testing criteria applied during the evaluation run."""

    report_url: str
    """The URL to the rendered evaluation run report on the UI dashboard."""

    result_counts: ResultCounts
    """Counters summarizing the outcomes of the evaluation run."""

    status: str
    """The status of the evaluation run."""
