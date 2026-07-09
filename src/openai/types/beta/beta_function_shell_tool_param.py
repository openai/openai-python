# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .beta_container_auto_param import BetaContainerAutoParam
from .beta_local_environment_param import BetaLocalEnvironmentParam
from .beta_container_reference_param import BetaContainerReferenceParam

__all__ = ["BetaFunctionShellToolParam", "Environment"]

Environment: TypeAlias = Union[BetaContainerAutoParam, BetaLocalEnvironmentParam, BetaContainerReferenceParam]


class BetaFunctionShellToolParam(TypedDict, total=False):
    """A tool that allows the model to execute shell commands."""

    type: Required[Literal["shell"]]
    """The type of the shell tool. Always `shell`."""

    allowed_callers: Optional[List[Literal["direct", "programmatic"]]]
    """The tool invocation context(s)."""

    environment: Optional[Environment]
