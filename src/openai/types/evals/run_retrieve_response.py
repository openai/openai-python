# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import Field as FieldInfo

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .eval_api_error import EvalAPIError
from ..shared.metadata import Metadata
from .create_eval_jsonl_run_data_source import CreateEvalJSONLRunDataSource
from .create_eval_completions_run_data_source import CreateEvalCompletionsRunDataSource

__all__ = ["RunRetrieveResponse", "DataSource", "PerModelUsage", "PerTestingCriteriaResult", "ResultCounts"]

DataSource: TypeAlias = Annotated[
    Union[CreateEvalJSONLRunDataSource, CreateEvalCompletionsRunDataSource], PropertyInfo(discriminator="type")
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


class RunRetrieveResponse(BaseModel):
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
