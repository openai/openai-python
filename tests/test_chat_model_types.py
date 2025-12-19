"""Tests for ChatModel type definitions.

Verifies that the ChatModel type includes correct model names.
Relates to issue #2785: GPT 5.1 Mini wrongly listed in model list
"""

import pytest
from typing import get_args

from openai.types.shared import ChatModel


class TestChatModelTypes:
    """Test ChatModel type definitions."""

    def test_gpt_5_1_codex_mini_exists(self) -> None:
        """Verify gpt-5.1-codex-mini is in ChatModel (fixes #2785)."""
        # Get all valid ChatModel values
        valid_models = get_args(ChatModel)

        # gpt-5.1-codex-mini should exist (not gpt-5.1-mini)
        assert "gpt-5.1-codex-mini" in valid_models, (
            "gpt-5.1-codex-mini should be in ChatModel"
        )

    def test_gpt_5_1_mini_not_exists(self) -> None:
        """Verify gpt-5.1-mini is NOT in ChatModel (was incorrect)."""
        valid_models = get_args(ChatModel)

        # gpt-5.1-mini should NOT exist (it was wrongly listed)
        assert "gpt-5.1-mini" not in valid_models, (
            "gpt-5.1-mini should NOT be in ChatModel (issue #2785)"
        )

    def test_gpt_5_1_codex_exists(self) -> None:
        """Verify gpt-5.1-codex is in ChatModel."""
        valid_models = get_args(ChatModel)
        assert "gpt-5.1-codex" in valid_models

    def test_gpt_5_family_models_exist(self) -> None:
        """Verify GPT-5 family models are present."""
        valid_models = get_args(ChatModel)

        expected_gpt5_models = [
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
            "gpt-5.1",
            "gpt-5.1-codex",
            "gpt-5.1-codex-mini",
            "gpt-5.2",
        ]

        for model in expected_gpt5_models:
            assert model in valid_models, f"{model} should be in ChatModel"
