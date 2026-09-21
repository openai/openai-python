# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["MultiAgentConfig"]


class MultiAgentConfig(BaseModel):
    """The resolved configuration for creating and coordinating subagents."""

    enabled: bool
    """Whether subagent tools are enabled. Defaults to false."""

    max_concurrent_subagents: Optional[int] = None
    """Maximum number of subagents that may run concurrently, or null when disabled.

    Defaults to 6 when enabled.
    """
