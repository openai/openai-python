from openai._compat import model_parse
from openai.types.beta.beta_response_function_web_search import BetaResponseFunctionWebSearch
from openai.types.beta.beta_response_function_web_search_param import ActionFindInPage as BetaActionFindParam
from openai.types.responses.response_function_web_search import ResponseFunctionWebSearch
from openai.types.responses.response_function_web_search_param import ActionFind as ActionFindParam


def _find_payload() -> dict[str, object]:
    return {
        "id": "ws_test",
        "type": "web_search_call",
        "status": "completed",
        "action": {"type": "find_in_page", "pattern": "og:image"},
    }


def test_find_in_page_action_allows_missing_url() -> None:
    item = model_parse(ResponseFunctionWebSearch, _find_payload())

    assert item.action.type == "find_in_page"
    assert item.action.url is None
    assert "url" not in ActionFindParam.__required_keys__


def test_beta_find_in_page_action_allows_missing_url() -> None:
    item = model_parse(BetaResponseFunctionWebSearch, _find_payload())

    assert item.action.type == "find_in_page"
    assert item.action.url is None
    assert "url" not in BetaActionFindParam.__required_keys__
