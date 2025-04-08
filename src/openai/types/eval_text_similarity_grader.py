# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["EvalTextSimilarityGrader"]


class EvalTextSimilarityGrader(BaseModel):
    evaluation_metric: Literal[
        "fuzzy_match",
        "bleu",
        "gleu",
        "meteor",
        "rouge_1",
        "rouge_2",
        "rouge_3",
        "rouge_4",
        "rouge_5",
        "rouge_l",
        "cosine",
    ]
    """The evaluation metric to use.

    One of `cosine`, `fuzzy_match`, `bleu`, `gleu`, `meteor`, `rouge_1`, `rouge_2`,
    `rouge_3`, `rouge_4`, `rouge_5`, or `rouge_l`.
    """

    input: str
    """The text being graded."""

    pass_threshold: float
    """A float score where a value greater than or equal indicates a passing grade."""

    reference: str
    """The text being graded against."""

    type: Literal["text_similarity"]
    """The type of grader."""

    name: Optional[str] = None
    """The name of the grader."""
