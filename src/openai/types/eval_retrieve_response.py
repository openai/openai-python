# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from .._utils import PropertyInfo
from .._models import BaseModel
from .shared.metadata import Metadata
from .eval_label_model_grader import EvalLabelModelGrader
from .eval_string_check_grader import EvalStringCheckGrader
from .eval_text_similarity_grader import EvalTextSimilarityGrader
from .responses.response_input_text import ResponseInputText
from .eval_custom_data_source_config import EvalCustomDataSourceConfig
from .eval_stored_completions_data_source_config import EvalStoredCompletionsDataSourceConfig

__all__ = [
    "EvalRetrieveResponse",
    "DataSourceConfig",
    "TestingCriterion",
    "TestingCriterionPython",
    "TestingCriterionScoreModel",
    "TestingCriterionScoreModelInput",
    "TestingCriterionScoreModelInputContent",
    "TestingCriterionScoreModelInputContentOutputText",
]

DataSourceConfig: TypeAlias = Annotated[
    Union[EvalCustomDataSourceConfig, EvalStoredCompletionsDataSourceConfig], PropertyInfo(discriminator="type")
]


class TestingCriterionPython(BaseModel):
    __test__ = False
    name: str
    """The name of the grader."""

    source: str
    """The source code of the python script."""

    type: Literal["python"]
    """The object type, which is always `python`."""

    image_tag: Optional[str] = None
    """The image tag to use for the python script."""

    pass_threshold: Optional[float] = None
    """The threshold for the score."""


class TestingCriterionScoreModelInputContentOutputText(BaseModel):
    __test__ = False
    text: str
    """The text output from the model."""

    type: Literal["output_text"]
    """The type of the output text. Always `output_text`."""


TestingCriterionScoreModelInputContent: TypeAlias = Union[
    str, ResponseInputText, TestingCriterionScoreModelInputContentOutputText
]


class TestingCriterionScoreModelInput(BaseModel):
    __test__ = False
    content: TestingCriterionScoreModelInputContent
    """Text inputs to the model - can contain template strings."""

    role: Literal["user", "assistant", "system", "developer"]
    """The role of the message input.

    One of `user`, `assistant`, `system`, or `developer`.
    """

    type: Optional[Literal["message"]] = None
    """The type of the message input. Always `message`."""


class TestingCriterionScoreModel(BaseModel):
    __test__ = False
    input: List[TestingCriterionScoreModelInput]
    """The input text. This may include template strings."""

    model: str
    """The model to use for the evaluation."""

    name: str
    """The name of the grader."""

    type: Literal["score_model"]
    """The object type, which is always `score_model`."""

    pass_threshold: Optional[float] = None
    """The threshold for the score."""

    range: Optional[List[float]] = None
    """The range of the score. Defaults to `[0, 1]`."""

    sampling_params: Optional[object] = None
    """The sampling parameters for the model."""


TestingCriterion: TypeAlias = Annotated[
    Union[
        EvalLabelModelGrader,
        EvalStringCheckGrader,
        EvalTextSimilarityGrader,
        TestingCriterionPython,
        TestingCriterionScoreModel,
    ],
    PropertyInfo(discriminator="type"),
]


class EvalRetrieveResponse(BaseModel):
    id: str
    """Unique identifier for the evaluation."""

    created_at: int
    """The Unix timestamp (in seconds) for when the eval was created."""

    data_source_config: DataSourceConfig
    """Configuration of data sources used in runs of the evaluation."""

    metadata: Optional[Metadata] = None
    """Set of 16 key-value pairs that can be attached to an object.

    This can be useful for storing additional information about the object in a
    structured format, and querying for objects via API or the dashboard.

    Keys are strings with a maximum length of 64 characters. Values are strings with
    a maximum length of 512 characters.
    """

    name: str
    """The name of the evaluation."""

    object: Literal["eval"]
    """The object type."""

    testing_criteria: List[TestingCriterion]
    """A list of testing criteria."""
