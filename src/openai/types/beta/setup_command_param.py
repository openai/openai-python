# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["SetupCommandParam"]


class SetupCommandParam(TypedDict, total=False):
    """A confidential setup command executed before the hosted agent starts."""

    command: Required[str]
    """The shell command to execute."""

    cwd: Optional[str]
    """The absolute working directory. Defaults to `/workspace`."""
