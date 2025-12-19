"""Tests for ChatModel type definitions.

Verifies that the ChatModel type includes correct model names.
Relates to issue #2761: gpt-audio-mini is missing from the ChatModel list
"""

import pytest
from typing import get_args

from openai.types.shared import ChatModel


class TestChatModelTypes:
    """Test ChatModel type definitions."""

    def test_gpt_audio_mini_exists(self) -> None:
        """Verify gpt-audio-mini is in ChatModel (fixes #2761)."""
        valid_models = get_args(ChatModel)

        assert "gpt-audio-mini" in valid_models, (
            "gpt-audio-mini should be in ChatModel"
        )
        assert "gpt-audio-mini-2025-04-01" in valid_models, (
            "gpt-audio-mini-2025-04-01 should be in ChatModel"
        )

    def test_audio_models_exist(self) -> None:
        """Verify audio-related models are present."""
        valid_models = get_args(ChatModel)

        expected_audio_models = [
            "gpt-4o-audio-preview",
            "gpt-4o-mini-audio-preview",
            "gpt-audio-mini",
        ]

        for model in expected_audio_models:
            assert model in valid_models, f"{model} should be in ChatModel"
