"""Tests for reasoning utilities.

Tests the OPENAI_REASONING_EFFORT environment variable support.
Relates to issue #2686: Allow setting reasoning effort via environment variable
"""

from __future__ import annotations

import os
import warnings

import pytest

from openai.lib import get_default_reasoning, get_reasoning_effort_from_env


class TestGetReasoningEffortFromEnv:
    """Tests for get_reasoning_effort_from_env function."""

    def setup_method(self) -> None:
        """Clean up env var before each test."""
        if "OPENAI_REASONING_EFFORT" in os.environ:
            del os.environ["OPENAI_REASONING_EFFORT"]

    def teardown_method(self) -> None:
        """Clean up env var after each test."""
        if "OPENAI_REASONING_EFFORT" in os.environ:
            del os.environ["OPENAI_REASONING_EFFORT"]

    def test_returns_none_when_not_set(self) -> None:
        """Returns None when env var is not set."""
        result = get_reasoning_effort_from_env()
        assert result is None

    @pytest.mark.parametrize(
        "value",
        ["none", "minimal", "low", "medium", "high", "xhigh"],
    )
    def test_returns_valid_values(self, value: str) -> None:
        """Returns the value when it's valid."""
        os.environ["OPENAI_REASONING_EFFORT"] = value
        result = get_reasoning_effort_from_env()
        assert result == value

    def test_case_insensitive(self) -> None:
        """Accepts case-insensitive values."""
        os.environ["OPENAI_REASONING_EFFORT"] = "HIGH"
        result = get_reasoning_effort_from_env()
        assert result == "high"

    def test_strips_whitespace(self) -> None:
        """Strips leading/trailing whitespace."""
        os.environ["OPENAI_REASONING_EFFORT"] = "  low  "
        result = get_reasoning_effort_from_env()
        assert result == "low"

    def test_warns_on_invalid_value(self) -> None:
        """Warns and returns None for invalid values."""
        os.environ["OPENAI_REASONING_EFFORT"] = "invalid"
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = get_reasoning_effort_from_env()
            assert result is None
            assert len(w) == 1
            assert "Invalid" in str(w[0].message)
            assert "OPENAI_REASONING_EFFORT" in str(w[0].message)


class TestGetDefaultReasoning:
    """Tests for get_default_reasoning function."""

    def setup_method(self) -> None:
        """Clean up env var before each test."""
        if "OPENAI_REASONING_EFFORT" in os.environ:
            del os.environ["OPENAI_REASONING_EFFORT"]

    def teardown_method(self) -> None:
        """Clean up env var after each test."""
        if "OPENAI_REASONING_EFFORT" in os.environ:
            del os.environ["OPENAI_REASONING_EFFORT"]

    def test_returns_none_when_no_config(self) -> None:
        """Returns None when no effort configured."""
        result = get_default_reasoning()
        assert result is None

    def test_uses_env_var(self) -> None:
        """Uses env var when no explicit effort provided."""
        os.environ["OPENAI_REASONING_EFFORT"] = "low"
        result = get_default_reasoning()
        assert result == {"effort": "low"}

    def test_explicit_effort_overrides_env(self) -> None:
        """Explicit effort parameter overrides env var."""
        os.environ["OPENAI_REASONING_EFFORT"] = "low"
        result = get_default_reasoning(effort="high")
        assert result == {"effort": "high"}

    def test_with_summary(self) -> None:
        """Can configure summary alongside effort."""
        os.environ["OPENAI_REASONING_EFFORT"] = "medium"
        result = get_default_reasoning(summary="concise")
        assert result == {"effort": "medium", "summary": "concise"}

    def test_summary_only(self) -> None:
        """Can configure summary without effort."""
        result = get_default_reasoning(summary="detailed")
        assert result == {"summary": "detailed"}

    def test_explicit_none_effort_uses_env(self) -> None:
        """Explicit None for effort still uses env var."""
        os.environ["OPENAI_REASONING_EFFORT"] = "high"
        result = get_default_reasoning(effort=None)
        assert result == {"effort": "high"}
