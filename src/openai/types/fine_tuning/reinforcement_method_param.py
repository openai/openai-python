# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypeAlias, TypedDict

from ..graders.multi_grader_param import MultiGraderParam
from ..graders.python_grader_param import PythonGraderParam
from ..graders.score_model_grader_param import ScoreModelGraderParam
from ..graders.string_check_grader_param import StringCheckGraderParam
from .reinforcement_hyperparameters_param import ReinforcementHyperparametersParam
from ..graders.text_similarity_grader_param import TextSimilarityGraderParam

__all__ = ["ReinforcementMethodParam", "Grader"]

Grader: TypeAlias = Union[
    StringCheckGraderParam, TextSimilarityGraderParam, PythonGraderParam, ScoreModelGraderParam, MultiGraderParam
]


class ReinforcementMethodParam(TypedDict, total=False):
    grader: Required[Grader]
    """The grader used for the fine-tuning job."""

    hyperparameters: ReinforcementHyperparametersParam
    """The hyperparameters used for the reinforcement fine-tuning job."""
