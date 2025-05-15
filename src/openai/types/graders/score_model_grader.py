# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from ..shared.eval_item import EvalItem

__all__ = ["ScoreModelGrader"]


class ScoreModelGrader(BaseModel):
    input: List[EvalItem]
    """The input text. This may include template strings."""

    model: str
    """The model to use for the evaluation."""

    name: str
    """The name of the grader."""

    type: Literal["score_model"]
    """The object type, which is always `score_model`."""

    range: Optional[List[float]] = None
    """The range of the score. Defaults to `[0, 1]`."""

    sampling_params: Optional[object] = None
    """The sampling parameters for the model."""
