# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import builtins
from typing import Dict, List, Optional
from typing_extensions import Literal

from ...._models import BaseModel
from ..eval_api_error import EvalAPIError

__all__ = ["OutputItemRetrieveResponse", "Sample", "SampleInput", "SampleOutput", "SampleUsage"]


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

    results: List[Dict[str, builtins.object]]
    """A list of results from the evaluation run."""

    run_id: str
    """The identifier of the evaluation run associated with this output item."""

    sample: Sample
    """A sample containing the input and output of the evaluation run."""

    status: str
    """The status of the evaluation run."""
