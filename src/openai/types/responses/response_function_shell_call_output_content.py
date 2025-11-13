# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = ["ResponseFunctionShellCallOutputContent", "Outcome", "OutcomeTimeout", "OutcomeExit"]


class OutcomeTimeout(BaseModel):
    type: Literal["timeout"]
    """The outcome type. Always `timeout`."""


class OutcomeExit(BaseModel):
    exit_code: int
    """The exit code returned by the shell process."""

    type: Literal["exit"]
    """The outcome type. Always `exit`."""


Outcome: TypeAlias = Annotated[Union[OutcomeTimeout, OutcomeExit], PropertyInfo(discriminator="type")]


class ResponseFunctionShellCallOutputContent(BaseModel):
    outcome: Outcome
    """The exit or timeout outcome associated with this chunk."""

    stderr: str
    """Captured stderr output for this chunk of the shell call."""

    stdout: str
    """Captured stdout output for this chunk of the shell call."""
