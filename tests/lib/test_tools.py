from __future__ import annotations

from openai._types import Omit, omit
from openai.lib._tools import _apply_web_search_default_location_tools


class TestApplyWebSearchDefaultLocationTools:
    """Tests for _apply_web_search_default_location_tools."""

    def test_no_tools_returns_omit(self) -> None:
        """When tools is Omit (not given), return it unchanged."""
        result = _apply_web_search_default_location_tools(omit)
        assert result is omit

    def test_empty_tools_list(self) -> None:
        """An empty list of tools should be returned unchanged."""
        tools: list = []
        result = _apply_web_search_default_location_tools(tools)
        assert result is tools  # same reference, no changes

    def test_non_web_search_tools_unchanged(self) -> None:
        """Tools that are not web_search should not be modified."""
        tools = [
            {"type": "function", "function": {"name": "my_func"}},
            {"type": "code_interpreter"},
        ]
        result = _apply_web_search_default_location_tools(tools)
        assert result is tools  # same reference, no changes

    def test_web_search_injects_user_location(self) -> None:
        """web_search without user_location should get one injected."""
        tools = [{"type": "web_search"}]
        result = _apply_web_search_default_location_tools(tools)
        assert result is not tools  # new list created
        assert result[0]["user_location"] == {"type": "approximate"}
        assert result[0]["type"] == "web_search"

    def test_web_search_with_existing_user_location_unchanged(self) -> None:
        """web_search that already has user_location should not be overridden."""
        existing_loc = {"type": "approximate", "city": "London", "country": "GB"}
        tools = [{"type": "web_search", "user_location": existing_loc}]
        result = _apply_web_search_default_location_tools(tools)
        assert result is tools  # same reference, no changes needed
        assert result[0]["user_location"] is existing_loc

    def test_web_search_2025_08_26_injects(self) -> None:
        tools = [{"type": "web_search_2025_08_26"}]
        result = _apply_web_search_default_location_tools(tools)
        assert result[0]["user_location"] == {"type": "approximate"}

    def test_web_search_preview_injects(self) -> None:
        tools = [{"type": "web_search_preview"}]
        result = _apply_web_search_default_location_tools(tools)
        assert result[0]["user_location"] == {"type": "approximate"}

    def test_web_search_preview_2025_03_11_injects(self) -> None:
        tools = [{"type": "web_search_preview_2025_03_11"}]
        result = _apply_web_search_default_location_tools(tools)
        assert result[0]["user_location"] == {"type": "approximate"}

    def test_mixed_tools_only_web_search_modified(self) -> None:
        """When mixing web_search and non-web-search tools, only web_search gets modified."""
        func_tool = {"type": "function", "function": {"name": "foo"}}
        ws_tool = {"type": "web_search"}
        tools = [func_tool, ws_tool]
        result = _apply_web_search_default_location_tools(tools)
        # function tool is unchanged
        assert result[0] is func_tool
        # web_search tool is a new dict with user_location injected
        assert result[1]["user_location"] == {"type": "approximate"}
        assert result[1]["type"] == "web_search"

    def test_web_search_preserves_other_keys(self) -> None:
        """Injecting user_location should not drop other keys on the tool dict."""
        tools = [{"type": "web_search", "extra_key": "value"}]
        result = _apply_web_search_default_location_tools(tools)
        assert result[0]["extra_key"] == "value"
        assert result[0]["user_location"] == {"type": "approximate"}

    def test_non_dict_tool_not_modified(self) -> None:
        """Non-dict tools (e.g. string shorthand) should pass through."""
        tools = ["web_search"]  # string, not dict
        result = _apply_web_search_default_location_tools(tools)
        assert result is tools  # unchanged
