# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .eval_jsonl_file_id_source import EvalJSONLFileIDSource
from .eval_jsonl_file_content_source import EvalJSONLFileContentSource

__all__ = ["CreateEvalJSONLRunDataSource", "Source"]

Source: TypeAlias = Annotated[
    Union[EvalJSONLFileContentSource, EvalJSONLFileIDSource], PropertyInfo(discriminator="type")
]


class CreateEvalJSONLRunDataSource(BaseModel):
    source: Source

    type: Literal["jsonl"]
    """The type of data source. Always `jsonl`."""
