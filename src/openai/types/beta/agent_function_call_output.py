# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import TypeAlias

from .input_content import InputContent

__all__ = ["AgentFunctionCallOutput"]

AgentFunctionCallOutput: TypeAlias = Union[str, List[InputContent]]
