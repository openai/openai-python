"""Exercise the real reader and SDK with local controlled responses, never an API provider."""

from __future__ import annotations

import json
import asyncio
from typing import Any
from pathlib import Path
from unittest.mock import patch

import httpx2 as httpx
from read_only import open_reader, answer_question
from playwright.async_api import Page, Response as PlaywrightResponse

from openai import AsyncOpenAI
from openai.lib.browser import BrowserError
from openai.types.responses import ResponseFunctionToolCall


def call(member: str, args: dict[str, Any], identity: str = "manual") -> dict[str, Any]:
    return {
        "type": "function_call",
        "id": identity,
        "call_id": identity,
        "name": f"browser_{member}",
        "arguments": json.dumps(args),
        "status": "completed",
    }


def payload(output: Any) -> dict[str, Any]:
    parts = output["output"]
    return json.loads(
        parts if isinstance(parts, str) else next(part["text"] for part in parts if part["type"] == "input_text")
    )


async def main() -> None:
    documents = json.loads(Path(__file__).with_name("reader-site.json").read_text())
    original = json.dumps(documents)
    async with open_reader(documents) as reader:
        original_goto = Page.goto

        async def committed_failure(page: Page, url: str, **kwargs: Any) -> PlaywrightResponse | None:
            await original_goto(page, url, **kwargs)
            assert page.url == url
            raise RuntimeError("Local fixture failed after navigation commit")

        with patch.object(Page, "goto", committed_failure):
            try:
                await reader.execute(
                    ResponseFunctionToolCall(**call("navigate", {"tab_id": None, "url": "http://reader.invalid/hours"}))
                )
            except RuntimeError as error:
                assert str(error) == "Browser state report failed."
            else:
                raise AssertionError("A retired reader supplied state after a failed navigation.")
        try:
            after = await reader.execute(ResponseFunctionToolCall(**call("get_page_text", {"tab_id": None})))
        except RuntimeError as error:
            assert str(error) == "Browser state report failed."
        else:
            assert payload(after)["ok"] is False, "A reader must retire after an uncertain navigation."
    boundary = "/" + "a" * (16_384 - len("http://reader.invalid/".encode()))
    custom: dict[str, Any] = {
        "/": {"title": "Index", "paragraphs": [], "links": {"/group hours": "Hours", "/地図": "Map"}},
        "/group hours": {"title": "Hours", "paragraphs": ["11:15 to 19:00"], "links": {"/地図": "Map"}},
        "/地図": {"title": "Map", "paragraphs": ["North gate"], "links": {"/guide!v2%20today": "Notes"}},
        "/guide!v2%20today": {"title": "Notes", "paragraphs": ["Current guide"], "links": {}},
    }
    async with open_reader(custom) as reader:
        for destination, content in (
            ("http://reader.invalid/group%20hours", "11:15 to 19:00"),
            ("http://reader.invalid/%E5%9C%B0%E5%9B%B3", "North gate"),
            ("http://reader.invalid/guide!v2%20today", "Current guide"),
        ):
            text = payload(await reader.execute(ResponseFunctionToolCall(**call("get_page_text", {"tab_id": None}))))
            assert destination in text["result"]
            moved = payload(
                await reader.execute(ResponseFunctionToolCall(**call("navigate", {"tab_id": None, "url": destination})))
            )
            assert moved["ok"] is True, (destination, moved)
            text = payload(await reader.execute(ResponseFunctionToolCall(**call("get_page_text", {"tab_id": None}))))
            assert content in text["result"]
    try:
        async with open_reader({**custom, "/group%20hours": custom["/group hours"]}):
            raise AssertionError("Two document keys resolved to the same route")
    except ValueError as error:
        assert "alias" in str(error)
    try:
        async with open_reader({**documents, boundary + "b": documents["/"]}):
            raise AssertionError("A reader URL over 16 KiB was accepted")
    except ValueError as error:
        assert "16 KiB" in str(error)
    async with open_reader(
        {
            **documents,
            "/": {**documents["/"], "title": "😺" * 256 + "é" + "large" * 2000},
            boundary: {"title": "Short guide title", "paragraphs": [], "links": {}},
        }
    ) as reader:
        initial = payload(await reader.execute(ResponseFunctionToolCall(**call("list_tabs", {}))))
        assert initial["state"]["tabs"][0]["title"] == "😺" * 256
        destination = "http://reader.invalid" + boundary
        next_page = payload(
            await reader.execute(ResponseFunctionToolCall(**call("navigate", {"tab_id": None, "url": destination})))
        )
        assert next_page["ok"] is True
        assert next_page["state"]["tabs"][0]["url"] == "http://reader.invalid"
        assert next_page["state"]["tabs"][0]["title"] == "Short guide title"
    for key in (
        "data:,local-text",
        "about:blank",
        "https://outside.invalid/",
        "//outside.invalid/",
        "/hours#fragment",
        "/hours?view=short",
        "relative",
        "/group\\hours",
        "/other/%2e%2e/hours",
    ):
        try:
            async with open_reader({**documents, key: documents["/"]}):
                raise AssertionError("An unsupported document key was admitted.")
        except ValueError as error:
            assert "document keys" in str(error)
    for question, target, expected in (
        ("When is the museum closed?", "/hours", "closed on Monday"),
        ("Where is the accessible entrance?", "/groups", "East Courtyard"),
    ):
        step = 0
        transport_error: Exception | None = None

        def dispatch(
            request: httpx.Request, question: str = question, target: str = target, expected: str = expected
        ) -> httpx.Response:
            nonlocal step, transport_error
            try:
                body = json.loads(request.content)
                step += 1
                output: list[dict[str, Any]]
                if step == 1:
                    assert question in json.dumps(body["input"])
                    assert sorted(tool["name"] for tool in body["tools"]) == [
                        "browser_get_page_text",
                        "browser_list_tabs",
                        "browser_navigate",
                    ]
                    output = [call("get_page_text", {"tab_id": None}, f"read-{step}")]
                elif step == 2:
                    assert f"http://reader.invalid{target}" in payload(body["input"][-1])["result"]
                    output = [call("navigate", {"tab_id": None, "url": f"http://reader.invalid{target}"}, f"go-{step}")]
                elif step == 3:
                    output = [call("get_page_text", {"tab_id": None}, f"read-{step}")]
                else:
                    text = payload(body["input"][-1])["result"]
                    assert expected in text
                    output = [
                        {
                            "type": "message",
                            "id": "answer",
                            "role": "assistant",
                            "status": "completed",
                            "content": [{"type": "output_text", "text": text, "annotations": []}],
                        }
                    ]
                return httpx.Response(
                    200,
                    json={
                        "id": f"response-{step}",
                        "object": "response",
                        "status": "completed",
                        "output": output,
                    },
                )
            except Exception as error:
                transport_error = error
                raise

        async with (
            open_reader(documents) as reader,
            AsyncOpenAI(
                api_key="synthetic-local-reader",
                max_retries=0,
                http_client=httpx.AsyncClient(transport=httpx.MockTransport(dispatch)),
            ) as client,
        ):
            try:
                result = await answer_question(client, reader, model="local-reader-check", question=question)
            except Exception:
                if transport_error is not None:
                    raise transport_error from None
                raise
            assert expected in result.output_text and step == 4
            denied = await reader.execute(
                ResponseFunctionToolCall(
                    **call(
                        "navigate",
                        {
                            "tab_id": None,
                            "url": "https://outside.invalid/",
                        },
                    )
                )
            )
            assert payload(denied)["ok"] is False
            try:
                await reader.execute(ResponseFunctionToolCall(**call("click", {"tab_id": None, "target": "invented"})))
            except BrowserError:
                pass
            else:
                raise AssertionError("A disabled mutation must not execute.")
            assert json.dumps(documents) == original

    documents["/hours"]["paragraphs"] = ["Today only: the museum closes at 14:35."]
    async with open_reader(documents) as reader:
        await reader.execute(
            ResponseFunctionToolCall(**call("navigate", {"tab_id": None, "url": "http://reader.invalid/hours"}))
        )
        output = await reader.execute(ResponseFunctionToolCall(**call("get_page_text", {"tab_id": None})))
        assert "14:35" in payload(output)["result"] and "17:00" not in payload(output)["result"]
    sources: tuple[dict[str, str | list[str] | dict[str, str]], ...] = (
        {"title": "Large guide", "paragraphs": ["😀" * 9000], "links": {}},
        {"title": "Many guide entries", "paragraphs": ["item"] * 2100, "links": {}},
        {"title": "Large link", "paragraphs": ["Read the index."], "links": {"/" + "x" * 17_000: "Long"}},
    )
    for source in sources:
        async with open_reader({"/": source}) as reader:
            output = await reader.execute(ResponseFunctionToolCall(**call("get_page_text", {"tab_id": None})))
            text = payload(output)["result"]
            assert isinstance(text, str) and len(text.encode()) <= 16_384
            assert text.endswith("[Some document content was omitted.]")
            assert "http://reader.invalid/xxx" not in text, "Never expose a partial URL as a destination"
    print(
        "PASS two questions, current page content, outside navigation refusal, bounded documents and disabled mutations"
    )


if __name__ == "__main__":
    asyncio.run(main())
