import httpx
import pytest
from openai import AsyncOpenAI, DefaultAsyncHttpxClient

@pytest.mark.anyio
async def test_images_generate_includes_content_filter_results_async():
    """
    Ensure the Image model exposes optional fields returned by the API,
    specifically `content_filter_results` (keeping `revised_prompt` coverage).
    """
    mock_json = {
        "created": 1711111111,
        "data": [
            {
                "url": "https://example.test/cat.png",
                "revised_prompt": "a cute cat wearing sunglasses",
                "content_filter_results": {
                    "sexual_minors": {"filtered": False},
                    "violence": {"filtered": False},
                },
            }
        ],
    }

    # Async handler because we'll use AsyncOpenAI (httpx.AsyncClient under the hood)
    async def ahandler(request: httpx.Request) -> httpx.Response:
        assert "images" in str(request.url).lower()
        return httpx.Response(200, json=mock_json)

    atransport = httpx.MockTransport(ahandler)

    client = AsyncOpenAI(
        api_key="test",
        http_client=DefaultAsyncHttpxClient(transport=atransport),
        timeout=10.0,
    )

    resp = await client.images.generate(model="gpt-image-1", prompt="cat with glasses")  # type: ignore

    assert hasattr(resp, "data") and isinstance(resp.data, list) and resp.data
    item = resp.data[0]

    # existing field
    assert item.revised_prompt == "a cute cat wearing sunglasses"

    # new optional field
    cfr = item.content_filter_results
    assert isinstance(cfr, dict), f"content_filter_results should be dict, got {type(cfr)}"
    assert cfr.get("violence", {}).get("filtered") is False
    assert cfr.get("sexual_minors", {}).get("filtered") is False
