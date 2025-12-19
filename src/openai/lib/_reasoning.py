"""Utilities for reasoning configuration.

This module provides utilities for configuring reasoning behavior,
including support for the OPENAI_REASONING_EFFORT environment variable.

Example usage:
    from openai import OpenAI
    from openai.lib import get_default_reasoning

    client = OpenAI()

    # Uses OPENAI_REASONING_EFFORT env var if set, otherwise returns None
    reasoning = get_default_reasoning()

    response = client.responses.create(
        model="gpt-5",
        input="Hello",
        reasoning=reasoning,
    )
"""

from __future__ import annotations

import os
import warnings
from typing import Optional, Literal

from ..types.shared_params.reasoning import Reasoning
from ..types.shared.reasoning_effort import ReasoningEffort


__all__ = [
    "get_default_reasoning",
    "get_reasoning_effort_from_env",
]

# Valid reasoning effort values
VALID_REASONING_EFFORTS: tuple[str, ...] = (
    "none",
    "minimal",
    "low",
    "medium",
    "high",
    "xhigh",
)

# Environment variable name
REASONING_EFFORT_ENV_VAR = "OPENAI_REASONING_EFFORT"


def get_reasoning_effort_from_env() -> Optional[ReasoningEffort]:
    """Get reasoning effort from the OPENAI_REASONING_EFFORT environment variable.

    Returns:
        The reasoning effort value if set and valid, None otherwise.

    Valid values are: none, minimal, low, medium, high, xhigh

    If an invalid value is set, a warning is emitted and None is returned.

    Example:
        >>> import os
        >>> os.environ["OPENAI_REASONING_EFFORT"] = "low"
        >>> get_reasoning_effort_from_env()
        'low'
    """
    value = os.environ.get(REASONING_EFFORT_ENV_VAR)
    if value is None:
        return None

    # Normalize to lowercase
    value_lower = value.lower().strip()

    if value_lower not in VALID_REASONING_EFFORTS:
        warnings.warn(
            f"Invalid {REASONING_EFFORT_ENV_VAR} value: '{value}'. "
            f"Valid values are: {', '.join(VALID_REASONING_EFFORTS)}. "
            "Ignoring environment variable.",
            UserWarning,
            stacklevel=2,
        )
        return None

    return value_lower  # type: ignore[return-value]


def get_default_reasoning(
    effort: Optional[ReasoningEffort] = None,
    summary: Optional[Literal["auto", "concise", "detailed"]] = None,
) -> Optional[Reasoning]:
    """Get a Reasoning configuration, using environment variable as default.

    This function allows you to easily configure reasoning with support for
    the OPENAI_REASONING_EFFORT environment variable.

    Args:
        effort: Override the reasoning effort. If None, uses OPENAI_REASONING_EFFORT
                environment variable if set.
        summary: Optional summary configuration for reasoning output.

    Returns:
        A Reasoning TypedDict if effort is configured (either explicitly or via
        environment variable), None otherwise.

    Precedence:
        1. Explicit `effort` parameter (if provided)
        2. OPENAI_REASONING_EFFORT environment variable (if set)
        3. None (SDK default behavior)

    Example:
        >>> # With environment variable set:
        >>> import os
        >>> os.environ["OPENAI_REASONING_EFFORT"] = "low"
        >>> get_default_reasoning()
        {'effort': 'low'}

        >>> # With explicit override:
        >>> get_default_reasoning(effort="high")
        {'effort': 'high'}

        >>> # With no configuration:
        >>> del os.environ["OPENAI_REASONING_EFFORT"]
        >>> get_default_reasoning()
        None
    """
    # Determine the effort value
    final_effort: Optional[ReasoningEffort] = None

    if effort is not None:
        final_effort = effort
    else:
        final_effort = get_reasoning_effort_from_env()

    # If no effort is configured, return None
    if final_effort is None and summary is None:
        return None

    # Build the Reasoning config
    result: Reasoning = {}
    if final_effort is not None:
        result["effort"] = final_effort
    if summary is not None:
        result["summary"] = summary

    return result
