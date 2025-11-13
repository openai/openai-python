# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["ResponseFunctionShellCallOutputContentParam", "Outcome", "OutcomeTimeout", "OutcomeExit"]


class OutcomeTimeout(TypedDict, total=False):
    type: Required[Literal["timeout"]]
    """The outcome type. Always `timeout`."""


class OutcomeExit(TypedDict, total=False):
    exit_code: Required[int]
    """The exit code returned by the shell process."""

    type: Required[Literal["exit"]]
    """The outcome type. Always `exit`."""


Outcome: TypeAlias = Union[OutcomeTimeout, OutcomeExit]


class ResponseFunctionShellCallOutputContentParam(TypedDict, total=False):
    outcome: Required[Outcome]
    """The exit or timeout outcome associated with this chunk."""

    stderr: Required[str]
    """Captured stderr output for this chunk of the shell call."""

    stdout: Required[str]
    """Captured stdout output for this chunk of the shell call."""
