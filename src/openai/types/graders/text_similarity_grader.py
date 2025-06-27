# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["TextSimilarityGrader"]


class TextSimilarityGrader(BaseModel):
    evaluation_metric: Literal[
        "fuzzy_match", "bleu", "gleu", "meteor", "rouge_1", "rouge_2", "rouge_3", "rouge_4", "rouge_5", "rouge_l"
    ]
    """The evaluation metric to use.

    One of `fuzzy_match`, `bleu`, `gleu`, `meteor`, `rouge_1`, `rouge_2`, `rouge_3`,
    `rouge_4`, `rouge_5`, or `rouge_l`.
    """

    input: str
    """The text being graded."""

    name: str
    """The name of the grader."""

    reference: str
    """The text being graded against."""

    type: Literal["text_similarity"]
    """The type of grader."""
