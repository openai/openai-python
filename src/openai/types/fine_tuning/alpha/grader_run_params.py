# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, TypeAlias, TypedDict

from ...graders.multi_grader_param import MultiGraderParam
from ...graders.python_grader_param import PythonGraderParam
from ...graders.score_model_grader_param import ScoreModelGraderParam
from ...graders.string_check_grader_param import StringCheckGraderParam
from ...graders.text_similarity_grader_param import TextSimilarityGraderParam

__all__ = ["GraderRunParams", "Grader"]


class GraderRunParams(TypedDict, total=False):
    grader: Required[Grader]
    """The grader used for the fine-tuning job."""

    model_sample: Required[str]
    """The model sample to be evaluated."""

    reference_answer: Required[Union[str, Iterable[object], float, object]]
    """The reference answer for the evaluation."""


Grader: TypeAlias = Union[
    StringCheckGraderParam, TextSimilarityGraderParam, PythonGraderParam, ScoreModelGraderParam, MultiGraderParam
]
