# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .beta_response_input_file import BetaResponseInputFile
from .beta_response_input_text import BetaResponseInputText
from .beta_response_input_image import BetaResponseInputImage

__all__ = ["BetaResponseInputContent"]

BetaResponseInputContent: TypeAlias = Annotated[
    Union[BetaResponseInputText, BetaResponseInputImage, BetaResponseInputFile], PropertyInfo(discriminator="type")
]
