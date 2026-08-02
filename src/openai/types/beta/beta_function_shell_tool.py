# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .beta_container_auto import BetaContainerAuto
from .beta_local_environment import BetaLocalEnvironment
from .beta_container_reference import BetaContainerReference

__all__ = ["BetaFunctionShellTool", "Environment"]

Environment: TypeAlias = Annotated[
    Union[BetaContainerAuto, BetaLocalEnvironment, BetaContainerReference, None], PropertyInfo(discriminator="type")
]


class BetaFunctionShellTool(BaseModel):
    """A tool that allows the model to execute shell commands."""

    type: Literal["shell"]
    """The type of the shell tool. Always `shell`."""

    allowed_callers: Optional[List[Literal["direct", "programmatic"]]] = None
    """The tool invocation context(s)."""

    environment: Optional[Environment] = None
