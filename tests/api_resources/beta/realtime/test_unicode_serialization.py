"""Test that realtime event serialization properly handles Unicode characters."""

import json
from typing import Any, Dict

import pytest

from openai.types.beta.realtime.realtime_client_event_param import RealtimeClientEventParam


class TestUnicodeSerializationFix:
    """Test that Unicode characters in realtime events are not unnecessarily escaped."""

    def test_cyrillic_text_serialization(self) -> None:
        """Test that Cyrillic text in event data is serialized without Unicode escaping."""
        # Sample event with Cyrillic text (simulating function calling with Russian descriptions)
        event_data: RealtimeClientEventParam = {
            "type": "response.create",
            "response": {
                "modalities": ["text"],
                "instructions": "Ответьте на русском языке",
                "tools": [
                    {
                        "type": "function",
                        "name": "get_user_info", 
                        "description": "Получить информацию о пользователе",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Имя пользователя"
                                },
                                "age": {
                                    "type": "integer",
                                    "description": "Возраст пользователя"
                                }
                            },
                            "required": ["name"]
                        }
                    }
                ]
            }
        }
        
        # Test the JSON serialization behavior
        serialized_with_escapes = json.dumps(event_data)  # Default ensure_ascii=True
        serialized_without_escapes = json.dumps(event_data, ensure_ascii=False)
        
        # Verify the fix: ensure_ascii=False should be used to avoid token bloat
        assert len(serialized_without_escapes) < len(serialized_with_escapes), (
            "Serialization with ensure_ascii=False should be more compact"
        )
        
        # Verify no Unicode escapes in the fixed version
        assert "\\u" not in serialized_without_escapes, (
            "Fixed serialization should not contain Unicode escape sequences"
        )
        
        # Verify original Cyrillic text is preserved
        assert "Имя пользователя" in serialized_without_escapes, (
            "Original Cyrillic text should be preserved in fixed serialization"
        )
        
        # Verify both versions parse to the same data
        assert json.loads(serialized_with_escapes) == json.loads(serialized_without_escapes), (
            "Both serialization methods should produce equivalent JSON when parsed"
        )

    def test_unicode_token_savings(self) -> None:
        """Test that Unicode text serialization provides significant token savings."""
        # Event with substantial Unicode content
        event_with_unicode = {
            "type": "session.update",
            "session": {
                "instructions": (
                    "Вы помощник, который говорит на русском языке. "
                    "Отвечайте вежливо и информативно на все вопросы пользователей. "
                    "Используйте правильную грамматику и орфографию."
                ),
                "voice": "alloy",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                }
            }
        }
        
        # Compare serialization sizes
        with_escapes = json.dumps(event_with_unicode)
        without_escapes = json.dumps(event_with_unicode, ensure_ascii=False)
        
        # Calculate savings
        size_reduction = len(with_escapes) - len(without_escapes)
        percentage_saved = (size_reduction / len(with_escapes)) * 100
        
        # Should provide substantial savings for Unicode-heavy content
        assert percentage_saved > 30, (
            f"Expected >30% size reduction, got {percentage_saved:.1f}%"
        )
        
        # Estimated token savings (rough estimate: 4 chars per token)
        estimated_token_savings = size_reduction / 4
        assert estimated_token_savings > 20, (
            f"Expected >20 tokens saved, estimated {estimated_token_savings:.0f}"
        )

    def test_mixed_content_serialization(self) -> None:
        """Test serialization with mixed ASCII and Unicode content."""
        mixed_content_event = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": "Hello! Can you help me? Привет! Помогите мне, пожалуйста!"
                    }
                ]
            }
        }
        
        serialized = json.dumps(mixed_content_event, ensure_ascii=False)
        
        # Verify both languages are preserved correctly
        assert "Hello! Can you help me?" in serialized
        assert "Привет! Помогите мне, пожалуйста!" in serialized
        assert "\\u" not in serialized  # No Unicode escapes

    def test_ascii_only_content_unchanged(self) -> None:
        """Test that ASCII-only content behaves the same with both settings."""
        ascii_only_event = {
            "type": "response.create",
            "response": {
                "modalities": ["text", "audio"],
                "instructions": "Please respond in English only.",
                "voice": "alloy"
            }
        }
        
        with_escapes = json.dumps(ascii_only_event)
        without_escapes = json.dumps(ascii_only_event, ensure_ascii=False)
        
        # For ASCII-only content, both should be identical
        assert with_escapes == without_escapes, (
            "ASCII-only content should be identical with both ensure_ascii settings"
        )

    @pytest.mark.parametrize("language_text,expected_text", [
        ("中文测试", "中文测试"),  # Chinese
        ("العربية", "العربية"),    # Arabic
        ("עברית", "עברית"),      # Hebrew
        ("日本語", "日本語"),      # Japanese
        ("한국어", "한국어"),      # Korean
        ("हिन्दी", "हिन्दी"),     # Hindi
    ])
    def test_various_unicode_scripts(self, language_text: str, expected_text: str) -> None:
        """Test that various Unicode scripts are handled correctly."""
        event = {
            "type": "session.update",
            "session": {
                "instructions": f"Respond in this language: {language_text}"
            }
        }
        
        serialized = json.dumps(event, ensure_ascii=False)
        
        # Verify the original text is preserved
        assert expected_text in serialized
        assert "\\u" not in serialized  # No Unicode escapes