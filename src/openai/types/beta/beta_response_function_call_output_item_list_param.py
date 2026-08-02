# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import TypeAlias

from .beta_response_input_file_content_param import BetaResponseInputFileContentParam
from .beta_response_input_text_content_param import BetaResponseInputTextContentParam
from .beta_response_input_image_content_param import BetaResponseInputImageContentParam

__all__ = ["BetaResponseFunctionCallOutputItemListParam", "BetaResponseFunctionCallOutputItemParam"]

BetaResponseFunctionCallOutputItemParam: TypeAlias = Union[
    BetaResponseInputTextContentParam, BetaResponseInputImageContentParam, BetaResponseInputFileContentParam
]

BetaResponseFunctionCallOutputItemListParam: TypeAlias = List[BetaResponseFunctionCallOutputItemParam]
