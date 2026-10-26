# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["MultiAgentConfigParam"]


class MultiAgentConfigParam(TypedDict, total=False):
    """Explicit configuration for creating and coordinating subagents."""

    enabled: Required[bool]
    """Whether subagent tools are enabled."""

    max_concurrent_subagents: int
    """Maximum number of subagents that may run concurrently. Defaults to 6."""
