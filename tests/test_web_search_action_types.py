from openai.types.responses.response_function_web_search import ResponseFunctionWebSearch
from openai.types.responses.response_function_web_search_param import ActionFind as ActionFindParam


def test_find_in_page_action_allows_missing_url() -> None:
    item = ResponseFunctionWebSearch.model_validate(
        {
            "id": "ws_test",
            "type": "web_search_call",
            "status": "completed",
            "action": {"type": "find_in_page", "pattern": "og:image"},
        }
    )

    assert item.action.type == "find_in_page"
    assert item.action.url is None
    assert "url" not in ActionFindParam.__required_keys__
