# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .response_input_file import ResponseInputFile
from .response_input_text import ResponseInputText
from .response_input_image import ResponseInputImage

__all__ = ["ResponseInputContent"]

ResponseInputContent: TypeAlias = Annotated[
    Union[ResponseInputText, ResponseInputImage, ResponseInputFile], PropertyInfo(discriminator="type")
]
