# Tests for ResponseFunctionWebSearch type
# Verifies that the action field correctly handles None values from the API
import pytest

from openai.types.responses.response_function_web_search import (
    ActionSearch,
    ActionOpenPage,
    ActionFind,
    ResponseFunctionWebSearch,
)


def test_response_function_web_search_with_search_action():
    """Test that a web search call with a search action works correctly."""
    data = {
        "id": "ws_123",
        "action": {
            "type": "search",
            "query": "test query",
            "queries": ["test query"],
        },
        "status": "completed",
        "type": "web_search_call",
    }
    result = ResponseFunctionWebSearch(**data)
    assert result.id == "ws_123"
    assert result.action is not None
    assert isinstance(result.action, ActionSearch)
    assert result.action.type == "search"
    assert result.action.query == "test query"


def test_response_function_web_search_with_open_page_action():
    """Test that a web search call with an open_page action works correctly."""
    data = {
        "id": "ws_456",
        "action": {
            "type": "open_page",
            "url": "https://example.com",
        },
        "status": "completed",
        "type": "web_search_call",
    }
    result = ResponseFunctionWebSearch(**data)
    assert result.id == "ws_456"
    assert result.action is not None
    assert isinstance(result.action, ActionOpenPage)
    assert result.action.type == "open_page"
    assert result.action.url == "https://example.com"


def test_response_function_web_search_with_find_action():
    """Test that a web search call with a find_in_page action works correctly."""
    data = {
        "id": "ws_789",
        "action": {
            "type": "find_in_page",
            "pattern": "search term",
            "url": "https://example.com",
        },
        "status": "completed",
        "type": "web_search_call",
    }
    result = ResponseFunctionWebSearch(**data)
    assert result.id == "ws_789"
    assert result.action is not None
    assert isinstance(result.action, ActionFind)
    assert result.action.type == "find_in_page"
    assert result.action.pattern == "search term"


def test_response_function_web_search_with_none_action():
    """Test that a web search call with action=None works correctly.

    This is a regression test for GitHub issue #3179.
    The API can return null for the action field in some cases
    (e.g., when the search is still in progress or the action
    hasn't been determined yet).
    """
    data = {
        "id": "ws_abc",
        "action": None,
        "status": "completed",
        "type": "web_search_call",
    }
    result = ResponseFunctionWebSearch(**data)
    assert result.id == "ws_abc"
    assert result.action is None
    assert result.status == "completed"


def test_response_function_web_search_without_action():
    """Test that a web search call without action field defaults to None."""
    data = {
        "id": "ws_def",
        "status": "in_progress",
        "type": "web_search_call",
    }
    result = ResponseFunctionWebSearch(**data)
    assert result.id == "ws_def"
    assert result.action is None
    assert result.status == "in_progress"


def test_response_function_web_search_action_none_safe_access():
    """Test that users can safely check action type with None action.

    This demonstrates the fix for issue #3179 - users can now safely
    access action.type without AttributeError when action is None.
    """
    data_with_action = {
        "id": "ws_1",
        "action": {"type": "search", "query": "test"},
        "status": "completed",
        "type": "web_search_call",
    }
    data_without_action = {
        "id": "ws_2",
        "action": None,
        "status": "completed",
        "type": "web_search_call",
    }

    result_with = ResponseFunctionWebSearch(**data_with_action)
    result_without = ResponseFunctionWebSearch(**data_without_action)

    # This pattern should work without errors
    search_count = 0
    for result in [result_with, result_without]:
        if result.action is not None and result.action.type == "search":
            search_count += 1

    assert search_count == 1
