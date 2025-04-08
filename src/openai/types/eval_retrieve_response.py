# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from .._utils import PropertyInfo
from .._models import BaseModel
from .shared.metadata import Metadata
from .eval_label_model_grader import EvalLabelModelGrader
from .eval_string_check_grader import EvalStringCheckGrader
from .eval_text_similarity_grader import EvalTextSimilarityGrader
from .eval_custom_data_source_config import EvalCustomDataSourceConfig
from .eval_stored_completions_data_source_config import EvalStoredCompletionsDataSourceConfig

__all__ = ["EvalRetrieveResponse", "DataSourceConfig", "TestingCriterion"]

DataSourceConfig: TypeAlias = Annotated[
    Union[EvalCustomDataSourceConfig, EvalStoredCompletionsDataSourceConfig], PropertyInfo(discriminator="type")
]

TestingCriterion: TypeAlias = Annotated[
    Union[EvalLabelModelGrader, EvalStringCheckGrader, EvalTextSimilarityGrader], PropertyInfo(discriminator="type")
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

    share_with_openai: bool
    """Indicates whether the evaluation is shared with OpenAI."""

    testing_criteria: List[TestingCriterion]
    """A list of testing criteria."""
