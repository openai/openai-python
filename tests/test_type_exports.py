"""Tests for type exports from openai.types.

Verifies that major types are exported from openai.types for easier access.
Relates to issue #2680: Major types are not exposed in openai.types
"""

import pytest


class TestTypeExports:
    """Test that major types are exported from openai.types."""

    def test_chat_completion_exported(self) -> None:
        """Verify ChatCompletion is exported from openai.types (fixes #2680)."""
        from openai.types import ChatCompletion
        from openai.types.chat import ChatCompletion as ChatCompletionOriginal

        assert ChatCompletion is ChatCompletionOriginal

    def test_response_exported(self) -> None:
        """Verify Response is exported from openai.types (fixes #2680)."""
        from openai.types import Response
        from openai.types.responses import Response as ResponseOriginal

        assert Response is ResponseOriginal

    def test_response_usage_exported(self) -> None:
        """Verify ResponseUsage is exported from openai.types (fixes #2680)."""
        from openai.types import ResponseUsage
        from openai.types.responses import ResponseUsage as ResponseUsageOriginal

        assert ResponseUsage is ResponseUsageOriginal

    def test_types_can_be_used_for_type_hints(self) -> None:
        """Verify that imported types can be used for type hints."""
        from openai.types import ChatCompletion, Response, ResponseUsage

        def process_chat_completion(completion: ChatCompletion) -> None:
            pass

        def process_response(response: Response) -> None:
            pass

        def process_usage(usage: ResponseUsage) -> None:
            pass

        # If we get here without errors, the types work for hints
        assert True
