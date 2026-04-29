from typing import cast

from openai._models import construct_type
from openai.types.responses.response_function_web_search import ActionSearch, ResponseFunctionWebSearch


def test_action_search_source_allows_api_sources() -> None:
    response = cast(
        ResponseFunctionWebSearch,
        construct_type(
            type_=ResponseFunctionWebSearch,
            value={
                "id": "ws_123",
                "type": "web_search_call",
                "status": "completed",
                "action": {
                    "type": "search",
                    "query": "openai docs",
                    "queries": ["openai docs"],
                    "sources": [
                        {
                            "type": "api",
                            "name": "OpenAI Docs",
                        }
                    ],
                },
            },
        ),
    )

    action = cast(ActionSearch, response.action)
    assert action.type == "search"
    assert action.sources is not None
    assert action.sources[0].type == "api"
    assert action.sources[0].name == "OpenAI Docs"
    assert action.sources[0].url is None
