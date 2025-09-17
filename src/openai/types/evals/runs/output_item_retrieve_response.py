# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from ..eval_api_error import EvalAPIError

__all__ = ["OutputItemRetrieveResponse", "Result", "Sample", "SampleInput", "SampleOutput", "SampleUsage"]


class Result(BaseModel):
    name: str
    """The name of the grader."""

    passed: bool
    """Whether the grader considered the output a pass."""

    score: float
    """The numeric score produced by the grader."""

    sample: Optional[Dict[str, object]] = None
    """Optional sample or intermediate data produced by the grader."""

    type: Optional[str] = None
    """The grader type (for example, "string-check-grader")."""

    __pydantic_extra__: Dict[str, object] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]
    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class SampleInput(BaseModel):
    content: str
    """The content of the message."""

    role: str
    """The role of the message sender (e.g., system, user, developer)."""


class SampleOutput(BaseModel):
    content: Optional[str] = None
    """The content of the message."""

    role: Optional[str] = None
    """The role of the message (e.g. "system", "assistant", "user")."""


class SampleUsage(BaseModel):
    cached_tokens: int
    """The number of tokens retrieved from cache."""

    completion_tokens: int
    """The number of completion tokens generated."""

    prompt_tokens: int
    """The number of prompt tokens used."""

    total_tokens: int
    """The total number of tokens used."""


class Sample(BaseModel):
    error: EvalAPIError
    """An object representing an error response from the Eval API."""

    finish_reason: str
    """The reason why the sample generation was finished."""

    input: List[SampleInput]
    """An array of input messages."""

    max_completion_tokens: int
    """The maximum number of tokens allowed for completion."""

    model: str
    """The model used for generating the sample."""

    output: List[SampleOutput]
    """An array of output messages."""

    seed: int
    """The seed used for generating the sample."""

    temperature: float
    """The sampling temperature used."""

    top_p: float
    """The top_p value used for sampling."""

    usage: SampleUsage
    """Token usage details for the sample."""


class OutputItemRetrieveResponse(BaseModel):
    id: str
    """Unique identifier for the evaluation run output item."""

    created_at: int
    """Unix timestamp (in seconds) when the evaluation run was created."""

    datasource_item: Dict[str, object]
    """Details of the input data source item."""

    datasource_item_id: int
    """The identifier for the data source item."""

    eval_id: str
    """The identifier of the evaluation group."""

    object: Literal["eval.run.output_item"]
    """The type of the object. Always "eval.run.output_item"."""

    results: List[Result]
    """A list of grader results for this output item."""

    run_id: str
    """The identifier of the evaluation run associated with this output item."""

    sample: Sample
    """A sample containing the input and output of the evaluation run."""

    status: str
    """The status of the evaluation run."""
