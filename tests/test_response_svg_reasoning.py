from typing import Optional

import httpx2
import pytest

from openai import OpenAI
from openai.types.responses.tool import ImageGeneration


@pytest.mark.parametrize(
    ("svg", "expected"),
    [({"reasoning": {"effort": "high"}}, "high"), ({"reasoning": None}, None), ({}, None)],
    ids=["value", "null", "omitted"],
)
def test_response_svg_reasoning(svg: dict[str, object], expected: Optional[str]) -> None:
    paths: list[str] = []

    def reply(request: httpx2.Request) -> httpx2.Response:
        paths.append(request.url.path)
        return httpx2.Response(200, json={"tools": [{"type": "image_generation", "svg": svg}]})

    with OpenAI(
        api_key="test-key",
        base_url="https://example.test/v1",
        http_client=httpx2.Client(transport=httpx2.MockTransport(reply)),
    ) as client:
        tool = client.responses.retrieve("resp_fixture").tools[0]

    assert paths == ["/v1/responses/resp_fixture"]
    assert isinstance(tool, ImageGeneration)
    assert tool.svg is not None
    reasoning = tool.svg.reasoning
    assert (reasoning.effort if reasoning is not None else None) == expected
