# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .beta_response_input_file_content import BetaResponseInputFileContent
from .beta_response_input_text_content import BetaResponseInputTextContent
from .beta_response_input_image_content import BetaResponseInputImageContent

__all__ = ["BetaResponseFunctionCallOutputItem"]

BetaResponseFunctionCallOutputItem: TypeAlias = Annotated[
    Union[BetaResponseInputTextContent, BetaResponseInputImageContent, BetaResponseInputFileContent],
    PropertyInfo(discriminator="type"),
]
