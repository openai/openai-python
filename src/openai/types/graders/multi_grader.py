# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict, Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .python_grader import PythonGrader
from .label_model_grader import LabelModelGrader
from .score_model_grader import ScoreModelGrader
from .string_check_grader import StringCheckGrader
from .text_similarity_grader import TextSimilarityGrader

__all__ = ["MultiGrader", "Graders"]

Graders: TypeAlias = Annotated[
    Union[StringCheckGrader, TextSimilarityGrader, PythonGrader, ScoreModelGrader, LabelModelGrader],
    PropertyInfo(discriminator="type"),
]


class MultiGrader(BaseModel):
    """
    A MultiGrader object combines the output of multiple graders to produce a single score.
    """

    calculate_output: str
    """A formula to calculate the output based on grader results."""

    graders: Dict[str, Graders]

    name: str
    """The name of the grader."""

    type: Literal["multi"]
    """The object type, which is always `multi`."""
