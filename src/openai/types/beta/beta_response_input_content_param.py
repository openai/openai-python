# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import TypeAlias

from .beta_response_input_file_param import BetaResponseInputFileParam
from .beta_response_input_text_param import BetaResponseInputTextParam
from .beta_response_input_image_param import BetaResponseInputImageParam

__all__ = ["BetaResponseInputContentParam"]

BetaResponseInputContentParam: TypeAlias = Union[
    BetaResponseInputTextParam, BetaResponseInputImageParam, BetaResponseInputFileParam
]
