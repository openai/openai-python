# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Union, Optional
from typing_extensions import TypeAlias

from ..._models import BaseModel
from .beta_response_input_file import BetaResponseInputFile
from .beta_response_input_text import BetaResponseInputText
from .beta_response_input_image import BetaResponseInputImage

__all__ = ["BetaResponsePrompt", "Variables"]

Variables: TypeAlias = Union[str, BetaResponseInputText, BetaResponseInputImage, BetaResponseInputFile]


class BetaResponsePrompt(BaseModel):
    """
    Reference to a prompt template and its variables.
    [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).
    """

    id: str
    """The unique identifier of the prompt template to use."""

    variables: Optional[Dict[str, Variables]] = None
    """Optional map of values to substitute in for variables in your prompt.

    The substitution values can either be strings, or other Response input types
    like images or files.
    """

    version: Optional[str] = None
    """Optional version of the prompt template."""
