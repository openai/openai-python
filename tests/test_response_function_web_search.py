# Tests for ResponseFunctionWebSearch type
# Verifies that the action field correctly handles None values from the API
import pytest

from openai.types.responses.response_function_web_search import (
    ActionSearch,
    ActionSearchSource,
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


def test_action_search_source_url_type():
    """Test that ActionSearchSource with type='url' works correctly."""
    source = ActionSearchSource(type="url", url="https://example.com")
    assert source.type == "url"
    assert source.url == "https://example.com"
    assert source.name is None


def test_action_search_source_api_type():
    """Test that ActionSearchSource with type='api' works correctly.

    This is a regression test for GitHub issue #2736.
    The API returns specialized data sources with type='api' and a name field
    (e.g., 'oai-weather', 'oai-sports', 'oai-finance') instead of a URL.
    """
    source = ActionSearchSource(type="api", name="oai-weather")
    assert source.type == "api"
    assert source.name == "oai-weather"
    assert source.url is None


def test_action_search_source_api_type_with_url():
    """Test that ActionSearchSource with type='api' can optionally have a URL."""
    source = ActionSearchSource(type="api", name="oai-sports", url="https://api.example.com")
    assert source.type == "api"
    assert source.name == "oai-sports"
    assert source.url == "https://api.example.com"


def test_search_action_with_api_source():
    """Test that ActionSearch can contain API-type sources.

    This verifies the fix for issue #2736 - the API returns specialized
    data sources (weather, sports, finance) with type='api'.
    """
    data = {
        "id": "ws_api",
        "action": {
            "type": "search",
            "query": "weather in NYC",
            "queries": ["weather in NYC"],
            "sources": [
                {"type": "url", "url": "https://weather.com"},
                {"type": "api", "name": "oai-weather"},
            ],
        },
        "status": "completed",
        "type": "web_search_call",
    }
    result = ResponseFunctionWebSearch(**data)
    assert result.action is not None
    assert isinstance(result.action, ActionSearch)
    assert result.action.sources is not None
    assert len(result.action.sources) == 2
    assert result.action.sources[0].type == "url"
    assert result.action.sources[0].url == "https://weather.com"
    assert result.action.sources[1].type == "api"
    assert result.action.sources[1].name == "oai-weather"
