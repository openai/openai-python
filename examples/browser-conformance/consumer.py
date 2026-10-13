"""Run with the clean wheel consumer's Python -I -B; no checkout imports."""

import sys
import json
import asyncio
import hashlib
import inspect
import argparse
import platform
import subprocess
from types import SimpleNamespace
from typing import Any, Callable, Awaitable, cast
from pathlib import Path
from zipfile import ZipFile
from functools import partial
from contextlib import AsyncExitStack
from collections.abc import Generator, AsyncGenerator

import httpx2

from openai import OpenAI, AsyncOpenAI, __file__ as openai_file
from openai.lib.browser import BrowserToolset, AsyncBrowserToolset
from openai.lib.computer import ComputerToolset, AsyncComputerToolset
from openai.types.responses import ResponseFunctionToolCall
from openai.lib.responses_tool_runner import (
    ToolRunnerError,
    RegisteredFunction,
    ResponsesRunnerTurn,
    ResponsesToolLedger,
    ResponsesToolRunner,
    AsyncRegisteredFunction,
    AsyncResponsesToolLedger,
    AsyncResponsesToolRunner,
)
from openai.types.responses.tool_param import FunctionToolParam
from openai.types.responses.response_create_params import ResponseCreateParamsNonStreaming

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "vectors.json").read_text())
CHECKS: list[dict[str, Any]] = []


def clone(value: Any) -> Any:
    return json.loads(json.dumps(value))


def sha(file: Path) -> str:
    return hashlib.sha256(file.read_bytes()).hexdigest()


def call(member: str, args: Any, id: str | None = None, raw: str | None = None) -> ResponseFunctionToolCall:
    return ResponseFunctionToolCall(
        id="fc_" + (id or member),
        name="browser_" + member,
        type="function_call",
        call_id=id or member,
        status="completed",
        arguments=raw if raw is not None else json.dumps(args),
    )


def payload(output: Any) -> Any:
    assert output["type"] == "function_call_output"
    assert output["output"][0]["type"] == "input_text"
    return json.loads(output["output"][0]["text"])


async def invoke(result: Any) -> Any:
    return await result if inspect.isawaitable(result) else result


def adapt(lane: str, callback: Callable[..., Any]) -> Callable[..., Any]:
    if lane == "sync":
        return callback

    async def awaited(*args: Any) -> Any:
        await asyncio.sleep(0)
        return callback(*args)

    return awaited


def computer_driver(lane: str, **overrides: Callable[..., Any]) -> SimpleNamespace:
    def unexpected(*_args: Any) -> None:
        raise RuntimeError("Unexpected computer action in conformance fixture")

    fail = adapt(lane, unexpected)
    return SimpleNamespace(
        **{
            "click": fail,
            "double_click": fail,
            "drag": fail,
            "keypress": fail,
            "move": fail,
            "scroll": fail,
            "type": fail,
            "wait": fail,
            "screenshot": fail,
            **overrides,
        }
    )


async def check(lane: str, id: str, operation: Callable[[], Awaitable[None]]) -> None:
    try:
        await operation()
        CHECKS.append({"lane": lane, "id": id, "pass": True})
    except Exception as exc:
        CHECKS.append({"lane": lane, "id": id, "pass": False, "error": repr(exc)})


def vector(member: str) -> Any:
    return next(item for item in DATA["browser"] if item["member"] == member)


class Rig:
    def __init__(self, lane: str, item: Any, *, confirm: Callable[..., Any] | None = None) -> None:
        self.events: list[Any] = []
        self.state = clone(DATA["state"])
        self.lane, self.item = lane, item

        class Driver(SimpleNamespace):
            marker = "receiver"

        self.driver = Driver()
        self.driver.state = adapt(lane, self.report)
        member = item["member"]
        if member != "list_tabs":
            # This descriptor binds the actual returned method to the driver's receiver.
            def method(receiver: Driver, args: Any) -> Any:
                assert receiver.marker == "receiver"
                self.events.append(["effect", clone(args)])
                self.state["tabs"][0]["title"] = "After"
                return clone(DATA["image"]) if member == "screenshot" else "completed:" + member

            if lane == "sync":
                setattr(Driver, member, method)
            else:

                async def async_method(receiver: Driver, args: Any) -> Any:
                    await asyncio.sleep(0)
                    return method(receiver, args)

                setattr(Driver, member, async_method)
        cls = BrowserToolset if lane == "sync" else AsyncBrowserToolset
        self.browser = cls(
            cast(Any, self.driver),
            members=[member],
            confirm=adapt(lane, confirm or self.confirm),
            url_policy=adapt(lane, self.policy),
        )

    def report(self) -> Any:
        self.events.append("state")
        return self.state

    def confirm(self, ctx: Any) -> bool:
        self.events.append("confirm")
        assert ctx["state"]["tabs"][0]["title"] == "Before"
        return True

    def policy(self, _ctx: Any, url: str) -> bool:
        self.events.append("url")
        assert url == self.item["arguments"]["url"]
        return True

    async def execute(self, action: ResponseFunctionToolCall | None = None, **kwargs: Any) -> Any:
        return await invoke(self.browser.execute(action or call(self.item["member"], self.item["arguments"]), **kwargs))


async def expect_error(operation: Callable[[], Awaitable[Any]]) -> Exception:
    try:
        await operation()
    except Exception as exc:
        return exc
    raise AssertionError("Expected operation to halt before it produced an output")


async def basic(lane: str) -> None:
    for item in DATA["browser"]:

        async def member_case(item: Any = item) -> None:
            rig = Rig(lane, item)
            member = item["member"]
            assert [t["name"] for t in rig.browser.tools] == ["browser_" + member]
            output = await rig.execute()
            result = payload(output)
            assert result["ok"] is True
            assert output["call_id"] == member
            if member == "list_tabs":
                assert result["state"] == DATA["reported_state"]
                assert rig.events == ["state", "state"]
            else:
                expected: list[Any] = ["state"] + (["url"] if item.get("url") else [])
                expected += ["confirm"] if item["change"] else []
                expected += [["effect", item["arguments"]], "state"]
                assert rig.events == expected, (rig.events, expected)
                assert result["state"]["tabs"][0]["title"] == "After"
                if member == "screenshot":
                    assert output["output"][1] == DATA["image"]
                else:
                    assert result["result"] == "completed:" + member

        await check(lane, "member:" + item["member"], member_case)

    for bad in DATA["invalid_states"]:
        for phase in ("initial", "final", "list_tabs"):

            async def bad_state(bad: Any = bad, phase: str = phase) -> None:
                rig = Rig(lane, vector("list_tabs" if phase == "list_tabs" else "click"))
                reads = 0

                def report() -> Any:
                    nonlocal reads
                    reads += 1
                    return clone(bad["value"] if reads == (2 if phase == "final" else 1) else DATA["state"])

                rig.driver.state = adapt(lane, report)
                err = await expect_error(rig.execute)
                assert str(err) == "Browser state report failed.", repr(err)
                assert sum(isinstance(e, list) for e in rig.events) == (1 if phase == "final" else 0)

            await check(lane, "state:" + bad["id"] + ":" + phase, bad_state)

    for bad in DATA["invalid_arguments"]:

        async def bad_args(bad: Any = bad) -> None:
            rig = Rig(lane, vector(bad["member"]))
            result = payload(await rig.execute(call(bad["member"], None, bad["id"], bad["raw"])))
            assert result["ok"] is False
            assert rig.events == ["state", "state"]

        await check(lane, "arguments:" + bad["id"], bad_args)

    for index, value in enumerate(DATA["refuse_values"]):

        async def refusal(value: Any = value) -> None:
            def confirm(_ctx: Any) -> Any:
                return clone(value)

            rig = Rig(lane, vector("click"), confirm=confirm)
            assert payload(await rig.execute())["ok"] is False
            assert rig.events == ["state", "state"]

        await check(lane, "strict-confirm:" + str(index), refusal)

    for entry in DATA["entry_policies"]:
        for phase in ("missing", "removed"):

            async def entry_policy(entry: Any = entry, phase: str = phase) -> None:
                events: list[Any] = []

                def report() -> Any:
                    events.append("state")
                    return clone(DATA["state"])

                class Driver(SimpleNamespace):
                    @property
                    def state(self) -> Callable[..., Any]:
                        events.append("state-getter")
                        return adapt(lane, report)

                driver = Driver()

                def effect(_args: Any) -> str:
                    events.append("effect")
                    return "done"

                def confirm(_ctx: Any) -> bool:
                    events.append("confirm")
                    return True

                def url_policy(_ctx: Any, _url: str) -> bool:
                    events.append("url")
                    return True

                setattr(driver, entry["member"], adapt(lane, effect))
                options: dict[str, Any] = {
                    "members": [entry["member"]],
                    "confirm": adapt(lane, confirm),
                    "url_policy": adapt(lane, url_policy),
                }
                cls = BrowserToolset if lane == "sync" else AsyncBrowserToolset
                if phase == "missing":
                    del options[entry["id"]]
                    await expect_error(lambda: invoke(cls(cast(Any, driver), **options)))
                    assert events == [], events
                else:
                    browser = cls(cast(Any, driver), **options)
                    assert events == [], events
                    setattr(browser, entry["id"], None)
                    result = await invoke(browser.execute(call(entry["member"], vector(entry["member"])["arguments"])))
                    assert payload(result)["ok"] is False
                    assert events == ["state-getter", "state", "state"], events

            await check(lane, "entry-policy:" + entry["id"] + ":" + phase, entry_policy)

    async def excluded() -> None:
        effects: list[str] = []

        class Driver(SimpleNamespace):
            @property
            def click(self) -> Any:
                raise RuntimeError("excluded getter read")

        d = Driver()
        d.state = adapt(lane, lambda: clone(DATA["state"]))

        def read(_args: Any) -> str:
            effects.append("read")
            return "text"

        d.get_page_text = adapt(lane, read)
        cls = BrowserToolset if lane == "sync" else AsyncBrowserToolset
        browser = cls(cast(Any, d), members=["get_page_text"])
        await expect_error(lambda: invoke(browser.execute(call("click", vector("click")["arguments"]))))
        assert effects == []
        assert payload(await invoke(browser.execute(call("get_page_text", {"tab_id": None}))))["result"] == "text"
        assert effects == ["read"]

    await check(lane, "excluded-getter-and-disabled-dispatch", excluded)

    async def snapshots() -> None:
        rig = Rig(lane, vector("navigate"))
        events: list[Any] = []

        def replacement(_args: Any) -> str:
            rig.events.append(["replaced-effect"])
            return "replaced"

        def denied_url(_ctx: Any, _url: str) -> bool:
            return False

        def denied_confirm(_ctx: Any) -> bool:
            return False

        def allowed_confirm(_ctx: Any) -> bool:
            return True

        def state() -> Any:
            events.append("original-state")
            rig.driver.state = adapt(lane, lambda: {"tabs": []})
            rig.driver.navigate = adapt(lane, replacement)
            rig.browser.url_policy = adapt(lane, denied_url)
            return clone(DATA["state"])

        def policy(_ctx: Any, _url: str) -> bool:
            events.append("url")
            rig.browser.confirm = adapt(lane, denied_confirm)
            return True

        rig.driver.state = adapt(lane, state)
        rig.browser.url_policy = adapt(lane, policy)
        first = payload(await rig.execute())
        assert first["ok"] is True and first["state"] == DATA["reported_state"]
        assert events == ["original-state", "url", "original-state"], events
        assert rig.events == ["confirm", ["effect", rig.item["arguments"]]]
        # The next call's only denial is the URL policy captured from the first state callback.
        rig.browser.confirm = adapt(lane, allowed_confirm)
        assert payload(await rig.execute())["ok"] is False
        assert sum(isinstance(e, list) for e in rig.events) == 1

    await check(lane, "async-handler-policy-state-snapshots", snapshots)

    async def before_getter() -> None:
        events: list[Any] = []

        def report() -> Any:
            events.append("state")
            return clone(DATA["state"])

        def deny(_ctx: Any) -> bool:
            events.append("deny")
            return False

        def allow(_ctx: Any) -> bool:
            events.append("allow")
            return True

        def effect(_args: Any) -> str:
            events.append("effect")
            return "done"

        class Driver(SimpleNamespace):
            @property
            def state(self) -> Callable[..., Any]:
                events.append("state-getter")
                browser.confirm = adapt(lane, allow)
                return adapt(lane, report)

        driver = Driver()
        driver.click = adapt(lane, effect)
        cls = BrowserToolset if lane == "sync" else AsyncBrowserToolset
        browser = cls(cast(Any, driver), members=["click"], confirm=adapt(lane, deny))
        action = call("click", vector("click")["arguments"])
        assert payload(await invoke(browser.execute(action)))["ok"] is False
        assert events == ["state-getter", "state", "deny", "state"], events
        assert payload(await invoke(browser.execute(action)))["ok"] is True
        assert events == [
            "state-getter",
            "state",
            "deny",
            "state",
            "state-getter",
            "state",
            "allow",
            "effect",
            "state",
        ], events

    await check(lane, "policy-captured-before-state-getter", before_getter)

    async def cancellation() -> None:
        cancelled = False

        def confirm(_ctx: Any) -> bool:
            nonlocal cancelled
            cancelled = True
            return True

        rig = Rig(lane, vector("click"), confirm=confirm)
        await expect_error(lambda: rig.execute(cancelled=lambda: cancelled))
        assert sum(isinstance(e, list) for e in rig.events) == 0

    await check(lane, "cancellation-before-effect", cancellation)

    async def generic_error() -> None:
        def confirm(_ctx: Any) -> bool:
            raise ValueError("SYNTHETIC private callback detail")

        rig = Rig(lane, vector("click"), confirm=confirm)
        output = await rig.execute()
        assert payload(output)["ok"] is False
        assert "SYNTHETIC" not in json.dumps(output)
        assert rig.events == ["state", "state"]

    await check(lane, "generic-callback-error-not-shared", generic_error)


def observation(value: Any) -> Any:
    result = clone(DATA["state"])
    if value is not None:
        result["observation"] = clone(value)
    return result


async def observed(lane: str, first: Any, last: Any, phase: str, invalid: bool) -> None:
    listing = phase == "list"
    member = "navigate" if phase == "policy" else "click"
    rig = Rig(lane, vector("list_tabs" if listing else member))
    count = 0

    def report() -> Any:
        nonlocal count
        count += 1
        return first if count == 1 else last

    def refuse(_ctx: Any) -> bool:
        return False

    def failure(_ctx: Any) -> bool:
        raise RuntimeError("SYNTHETIC_PRIVATE")

    rig.driver.state = adapt(lane, report)
    if phase == "refusal":
        rig.browser.confirm = adapt(lane, refuse)
    if phase == "error":
        rig.browser.confirm = adapt(lane, failure)
    if invalid:
        error = await expect_error(rig.execute)
        assert str(error) == "Browser state report failed.", (error, phase)
    else:
        output = payload(await rig.execute())
        assert output["ok"] == (phase not in ("error", "refusal"))
        assert output["state"].get("observation") == last.get("observation")
        if listing:
            assert output["result"] is None
        assert "SYNTHETIC_PRIVATE" not in json.dumps(output)
    assert sum(isinstance(e, list) for e in rig.events) == int(phase == "final" and count == 2)
    if phase == "policy":
        assert rig.events == [], "Invalid initial state must not reach policy, consent or driver"


async def v1(lane: str) -> None:
    for bad in DATA["v1"]["invalid_observations"]:
        for phase in ("initial", "final", "list", "refusal", "error"):
            malformed = clone(DATA["state"])
            malformed["observation"] = bad["value"]
            valid = observation(DATA["v1"]["empty"])
            await check(
                lane,
                f"v1:invalid:{bad['id']}:{phase}",
                partial(observed, lane, malformed if phase == "initial" else valid, malformed, phase, True),
            )

    for transition in DATA["v1"]["transitions"]:
        for phase in ("final", "list", "refusal", "error"):
            await check(
                lane,
                f"v1:transition:{transition['id']}:{phase}",
                partial(
                    observed,
                    lane,
                    observation(transition["before"]),
                    observation(transition["after"]),
                    phase,
                    not transition["valid"],
                ),
            )

    for url in DATA["v1"]["urls"]:

        async def url_case(url: Any = url) -> None:
            rig = Rig(lane, vector("list_tabs"))
            value = observation(DATA["v1"]["empty"])
            value["tabs"][0]["url"] = url["value"]
            rig.driver.state = adapt(lane, lambda: value)
            if url["origin"] is None:
                error = await expect_error(rig.execute)
                assert str(error) == "Browser state report failed.", error
            else:
                output = payload(await rig.execute())
                assert output["state"]["tabs"][0]["url"] == url["origin"]
                assert output["result"] is None

        await check(lane, f"v1:url:{url['id']}", url_case)

    for url in DATA["v1"]["authority_reads"]:
        bad = observation(DATA["v1"]["empty"])
        bad["tabs"][0]["url"] = url["value"]
        first = bad if url["phase"] == "policy" else observation(DATA["v1"]["empty"])
        await check(
            lane,
            f"v1:authority:{url['id']}:{url['phase']}",
            partial(observed, lane, first, bad, url["phase"], True),
        )

    for text in DATA["v1"]["text"]:

        async def text_case(text: Any = text) -> None:
            rig = Rig(lane, vector("list_tabs"))
            value = observation(DATA["v1"]["empty"])
            value["tabs"][0][text["field"]] = text["value"]
            rig.driver.state = adapt(lane, lambda: value)
            if text["valid"]:
                assert payload(await rig.execute())["state"]["tabs"][0][text["field"]] == text["value"]
            else:
                error = await expect_error(rig.execute)
                assert str(error) == "Browser state report failed.", error

        await check(lane, f"v1:text:{text['id']}", text_case)

    for tabs in DATA["v1"]["tab_counts"]:

        async def tabs_case(tabs: Any = tabs) -> None:
            rig = Rig(lane, vector("list_tabs"))
            value = observation(DATA["v1"]["empty"])
            value["tabs"] = [{**value["tabs"][0], "id": str(i), "active": i == 0} for i in range(tabs["count"])]
            rig.driver.state = adapt(lane, lambda: value)
            if tabs["valid"]:
                assert len(payload(await rig.execute())["state"]["tabs"]) == tabs["count"]
            else:
                error = await expect_error(rig.execute)
                assert str(error) == "Browser state report failed.", error

        await check(lane, f"v1:tabs:{tabs['count']}", tabs_case)

    async def projection() -> None:
        rig = Rig(lane, vector("navigate"))
        value = observation(DATA["v1"]["events"])
        value["tabs"][0]["url"] = "https://user:pw@EXAMPLE.com:443/private?q=SYNTHETIC_PRIVATE"
        value["tabs"][0]["private"] = object()
        value["observation"]["private"] = object()
        value["observation"]["changes"][0]["private"] = object()
        rig.driver.state = adapt(lane, lambda: value)

        def policy(ctx: Any, url: str) -> bool:
            assert url == rig.item["arguments"]["url"] and ctx["arguments"]["url"] == url
            assert ctx["state"]["tabs"][0]["url"] == "https://example.com"
            assert ctx["state"]["observation"] == DATA["v1"]["events"]
            ctx["state"]["observation"]["changes"].clear()
            ctx["state"]["tabs"][0]["title"] = "Callback-only"
            return True

        def allow(_ctx: Any, _url: str) -> bool:
            return True

        rig.browser.url_policy = adapt(lane, policy)
        output = payload(await rig.execute())
        assert output["ok"] and output["state"]["observation"] == DATA["v1"]["events"]
        assert output["state"]["tabs"][0]["url"] == "https://example.com"
        assert value["tabs"][0]["title"] == "Before"
        rig.driver.state = adapt(lane, lambda: observation(DATA["v1"]["empty"]))
        rig.browser.url_policy = adapt(lane, allow)
        assert payload(await rig.execute())["ok"]

    await check(lane, "v1:policy-projection-and-new-call-reset", projection)


def sse(response: Any, interrupted: bool, completed_output: Any = None) -> bytes:
    events: list[dict[str, Any]] = [
        {"type": "response.created", "response": {**response, "status": "in_progress", "output": []}}
    ]
    for index, item in enumerate(response["output"]):
        events.append(
            {
                "type": "response.output_item.added",
                "output_index": index,
                "item": {**item, "arguments": ""} if item["type"] == "function_call" else item,
            }
        )
        if item["type"] == "function_call":
            events.append(
                {
                    "type": "response.function_call_arguments.delta",
                    "output_index": index,
                    "item_id": item["id"],
                    "delta": item["arguments"],
                }
            )
        events.append({"type": "response.output_item.done", "output_index": index, "item": item})
    if not interrupted:
        events.append(
            {
                "type": "response.completed",
                "response": response if completed_output is None else {**response, "output": completed_output},
            }
        )
    return (
        "".join("data: " + json.dumps({**e, "sequence_number": n}) + "\n\n" for n, e in enumerate(events)).encode()
        + b"data: [DONE]\n\n"
    )


async def mixed(lane: str, stream: bool, eager: bool, interrupt: bool = False) -> None:
    bodies: list[Any] = []
    events: list[str] = []
    effects: list[str] = []

    class Driver(SimpleNamespace):
        pass

    d = Driver()
    d.state = adapt(lane, lambda: clone(DATA["state"]))

    def read(_args: Any) -> str:
        effects.append("read")
        return "r1: invoice"

    def image(_args: Any) -> Any:
        effects.append("image")
        return clone(DATA["image"])

    def native_type(action: Any) -> None:
        effects.append("native:" + action.text)

    def native_image() -> Any:
        effects.append("native-shot")
        return {"type": "computer_screenshot", "image_url": DATA["image"]["image_url"]}

    def record(args: Any) -> Any:
        effects.append("function:" + args["text"])
        return args["text"]

    d.read_page, d.screenshot = adapt(lane, read), adapt(lane, image)
    native = computer_driver(lane, type=adapt(lane, native_type), screenshot=adapt(lane, native_image))
    reader = call("read_page", {"tab_id": None, "filter": "all"}, "read").to_dict()
    ordinary = call("record", {"text": "filed"}, "record").to_dict()
    ordinary["name"] = "record"
    picture = call("screenshot", {"tab_id": None}, "picture").to_dict()
    turns = [[DATA["reasoning"], reader, ordinary, DATA["native"], picture], [DATA["final"]]]

    def transport(req: httpx2.Request) -> httpx2.Response:
        request = json.loads(req.content)
        output = turns[len(bodies)]
        bodies.append(request)
        response = {
            "id": "resp_" + str(len(bodies)),
            "object": "response",
            "created_at": 0,
            "model": "",
            "status": "completed",
            "output": output,
        }
        if stream:
            return httpx2.Response(200, headers={"content-type": "text/event-stream"}, content=sse(response, interrupt))
        return httpx2.Response(200, json=response)

    def on_event(event: Any) -> None:
        events.append(event.type)

    params: ResponseCreateParamsNonStreaming = {"model": "", "input": "Process the local fixture", "store": False}
    failed = None
    try:
        if lane == "sync":
            runner = ResponsesToolRunner(
                browser=BrowserToolset(cast(Any, d), members=["read_page", "screenshot"]),
                computer=ComputerToolset(cast(Any, native)),
                functions=[RegisteredFunction(tool=DATA["record_tool"], execute=record)],
            )
            with OpenAI(
                api_key="synthetic-unused",
                base_url="http://fixture.invalid/v1",
                max_retries=0,
                http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
            ) as client:
                result = runner.run(client, params, stream=stream, eager=eager, on_event=on_event, max_steps=3)
        else:
            async_runner = AsyncResponsesToolRunner(
                browser=AsyncBrowserToolset(cast(Any, d), members=["read_page", "screenshot"]),
                computer=AsyncComputerToolset(cast(Any, native)),
                functions=[AsyncRegisteredFunction(tool=DATA["record_tool"], execute=adapt(lane, record))],
            )
            async with AsyncOpenAI(
                api_key="synthetic-unused",
                base_url="http://fixture.invalid/v1",
                max_retries=0,
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
            ) as async_client:
                result = await async_runner.run(
                    async_client, params, stream=stream, eager=eager, on_event=adapt(lane, on_event), max_steps=3
                )
        assert result.output_text == "Fixture complete"
    except Exception as exc:
        failed = exc
    performed = ["read", "function:filed", "native:Receipt", "native-shot", "image"]
    if interrupt:
        assert isinstance(failed, ToolRunnerError), f"interrupted stream must stop with evidence: {failed!r}"
        assert len(bodies) == 1, (failed, bodies)
        assert effects == (performed if eager else []), (failed, effects)
        assert failed.attempted_call_ids == (("read", "record", "native_one", "picture") if eager else ())
        return
    if failed:
        raise failed
    assert effects == performed, effects
    assert len(bodies) == 2
    history = bodies[1]["input"]
    assert [x["call_id"] for x in history if x.get("type", "").endswith("_call_output")] == [
        "read",
        "record",
        "native_one",
        "picture",
    ]
    assert next(x for x in history if x.get("type") == "reasoning")["encrypted_content"] == "fixture-reasoning"
    assert (
        next(x for x in history if x.get("type") == "computer_call_output")["output"]["type"] == "computer_screenshot"
    )
    assert (
        next(x for x in history if x.get("type") == "function_call_output" and x["call_id"] == "picture")["output"][1]
        == DATA["image"]
    )
    assert ("response.output_item.done" in events) is stream
    assert "parsed_arguments" not in json.dumps(history)


async def iteration(lane: str, item: Any) -> None:
    bodies: list[Any] = []
    effects: list[str] = []

    def read(_args: Any) -> str:
        effects.append("read")
        return "r1: invoice"

    def record(args: Any) -> str:
        effects.append("function:" + args["text"])
        return str(args["text"])

    driver = SimpleNamespace(state=adapt(lane, lambda: clone(DATA["state"])), read_page=adapt(lane, read))
    ordinary = call("record", {"text": "filed"}, "record").to_dict()
    ordinary["name"] = "record"
    outputs = [
        [ordinary, call("read_page", {"tab_id": None, "filter": "all"}, "read").to_dict()],
        [DATA["final"]],
    ]

    def transport(req: httpx2.Request) -> httpx2.Response:
        response = {
            "id": "resp_" + str(len(bodies)),
            "object": "response",
            "created_at": 0,
            "model": "",
            "status": "completed",
            "output": outputs[len(bodies)],
        }
        bodies.append(json.loads(req.content))
        if item["stream"]:
            return httpx2.Response(200, headers={"content-type": "text/event-stream"}, content=sse(response, False))
        return httpx2.Response(200, json=response)

    params: ResponseCreateParamsNonStreaming = {"model": "", "input": "Process the local fixture", "store": False}
    turns: Generator[ResponsesRunnerTurn, None, None] | AsyncGenerator[ResponsesRunnerTurn, None]
    async with AsyncExitStack() as stack:
        if lane == "sync":
            client = stack.enter_context(
                OpenAI(
                    api_key="synthetic-unused",
                    base_url="http://fixture.invalid/v1",
                    max_retries=0,
                    http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
                )
            )
            runner = ResponsesToolRunner(
                browser=BrowserToolset(cast(Any, driver), members=["read_page"]),
                functions=[RegisteredFunction(DATA["record_tool"], record, allow_output_override=True)],
            )
            turns = runner.iterate(client, params, stream=item["stream"], eager=item["eager"])
            turn = next(turns)
            stack.callback(turns.close)
        else:
            async_client = await stack.enter_async_context(
                AsyncOpenAI(
                    api_key="synthetic-unused",
                    base_url="http://fixture.invalid/v1",
                    max_retries=0,
                    http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
                )
            )
            async_runner = AsyncResponsesToolRunner(
                browser=AsyncBrowserToolset(cast(Any, driver), members=["read_page"]),
                functions=[
                    AsyncRegisteredFunction(DATA["record_tool"], adapt(lane, record), allow_output_override=True)
                ],
            )
            turns = async_runner.iterate(async_client, params, stream=item["stream"], eager=item["eager"])
            turn = await turns.__anext__()
            stack.push_async_callback(turns.aclose)
        assert turn.step == 1 and not turn.final
        assert len(bodies) == 1 and turn.tools_executed is item["eager"]
        assert turn.attempted_call_ids == turn.completed_call_ids == (("record", "read") if item["eager"] else ())
        assert effects == (["function:filed", "read"] if item["eager"] else [])
        if item["scenario"] == "eager":
            try:
                turn.supply_outputs([])
            except ValueError:
                pass
            else:
                raise AssertionError("eager setter was accepted")
        elif item["scenario"] == "reject":
            result: Any = {"type": "function_call_output", "call_id": "record", "output": "accepted"}
            turn.supply_outputs([result])
            try:
                turn.supply_outputs([result, {"type": "function_call_output", "call_id": "unknown", "output": ""}])
            except ValueError:
                pass
            else:
                raise AssertionError("unknown setter was accepted")
        elif item["scenario"] == "supply":
            result = {
                "type": "function_call_output",
                "call_id": "record",
                "output": [
                    {"type": "input_text", "text": "human result"},
                    clone(DATA["image"]),
                    {"type": "input_file", "file_id": "file_fixture"},
                ],
            }
            turn.supply_outputs([result])
            result["output"][0]["text"] = "MUTATED"
            original = cast(ResponseFunctionToolCall, turn.response.output[1])
            original.call_id, original.arguments = "changed", '{"tab_id":"other","filter":"all"}'
            final = await turns.__anext__() if isinstance(turns, AsyncGenerator) else next(turns)
            assert final.step == 2 and final.final and not final.tools_executed
            assert final.attempted_call_ids == final.completed_call_ids == ("record", "read")
            assert effects == ["read"] and len(bodies) == 2
            history = bodies[1]["input"]
            calls = [entry for entry in history if entry.get("type") == "function_call"]
            assert [c["call_id"] for c in calls] == ["record", "read"]
            assert json.loads(calls[1]["arguments"]) == {"tab_id": None, "filter": "all"}
            returned = [entry for entry in history if entry.get("type") == "function_call_output"]
            assert [entry["call_id"] for entry in returned] == ["record", "read"]
            assert returned[0]["output"] == [
                {"type": "input_text", "text": "human result"},
                DATA["image"],
                {"type": "input_file", "file_id": "file_fixture"},
            ]
            try:
                turn.supply_outputs([])
            except ValueError:
                pass
            else:
                raise AssertionError("stale setter was accepted")
        else:
            assert item["scenario"] == "inspect"
    assert effects == (
        ["read"] if item["scenario"] == "supply" else (["function:filed", "read"] if item["eager"] else [])
    )
    assert len(bodies) == (2 if item["scenario"] == "supply" else 1)
    try:
        turn.supply_outputs([])
    except ValueError:
        pass
    else:
        raise AssertionError("closed setter was accepted")


async def ledger_case(lane: str, item: Any) -> None:
    scenario = str(item["scenario"])
    bodies: list[Any] = []
    effects: list[str] = []
    observations: list[str] = []
    writes: list[Any] = []
    resumed = False
    save_failure = True

    def fail() -> None:
        raise RuntimeError("synthetic callback failure")

    def state() -> Any:
        observations.append("state")
        return clone(DATA["state"])

    def read(_args: Any) -> str:
        effects.append("read")
        return "r1: invoice"

    def click(_args: Any) -> str:
        effects.append("click")
        if scenario == "browser-error":
            fail()
        return "clicked"

    def confirm(_ctx: Any) -> bool:
        observations.append("confirm")
        return scenario != "browser-refusal"

    def native_type(action: Any) -> None:
        effects.append("native:" + action.text)

    def native_wait(_action: Any) -> None:
        if scenario == "native-partial":
            fail()

    def native_image() -> Any:
        effects.append("native-shot")
        return {"type": "computer_screenshot", "image_url": DATA["image"]["image_url"]}

    def record(args: Any) -> str:
        effects.append("function:" + args["text"])
        if scenario == "function-throw":
            fail()
        if scenario == "nested-error":
            raise ToolRunnerError("synthetic nested failure", ["child"], [])
        return str(args["text"])

    driver = SimpleNamespace(state=adapt(lane, state), read_page=adapt(lane, read), click=adapt(lane, click))
    native = computer_driver(
        lane, type=adapt(lane, native_type), wait=adapt(lane, native_wait), screenshot=adapt(lane, native_image)
    )
    reader = call("read_page", {"tab_id": None, "filter": "all"}, "read").to_dict()
    ordinary = call("record", {"text": "filed"}, "record").to_dict()
    ordinary["name"] = "record"
    native_call = clone(DATA["native"])
    if scenario == "native-partial":
        native_call["actions"].append({"type": "wait"})
    batch = [ordinary, reader]
    if scenario in ("browser-error", "browser-refusal", "save-before-attempt"):
        batch = [call("click", vector("click")["arguments"], "click").to_dict(), ordinary]
    if scenario == "native-partial":
        batch = [native_call, ordinary]
    if scenario in ("resume-boundary", "invalid-registry"):
        batch = [DATA["reasoning"], ordinary, reader, native_call]
    streaming = scenario in ("inspection", "eager-interruption")

    def transport(req: httpx2.Request) -> httpx2.Response:
        bodies.append(json.loads(req.content))
        if scenario == "retry-budget":
            return httpx2.Response(500, json={"error": {"message": "fixture retry", "type": "server_error"}})
        response = {
            "id": "resp_" + str(len(bodies)),
            "object": "response",
            "created_at": 0,
            "model": "",
            "status": "completed",
            "output": [DATA["final"]] if resumed or scenario == "invalid-history" else batch,
        }
        if streaming:
            return httpx2.Response(
                200,
                headers={"content-type": "text/event-stream"},
                content=sse(response, scenario == "eager-interruption"),
            )
        return httpx2.Response(200, json=response)

    def save(checkpoint: Any) -> None:
        attempting = checkpoint["phase"] == "pending" and len(checkpoint["attempted_call_ids"]) == 1
        returning = attempting and len(checkpoint["returned_call_ids"]) == 1
        if save_failure and scenario == "save-before-attempt" and attempting:
            fail()
        if save_failure and scenario == "save-after-return" and returning:
            fail()
        if writes and checkpoint["revision"] <= writes[-1]["revision"]:
            fail()
        writes.append(clone(checkpoint))
        boundary = checkpoint["phase"] == "boundary" and len(checkpoint["returned_call_ids"]) > 0
        if save_failure and (
            (scenario == "lost-ack" and returning) or (scenario in ("resume-boundary", "invalid-registry") and boundary)
        ):
            fail()

    params: Any = {"model": "", "input": "Process the local fixture", "store": False}
    cls = ResponsesToolLedger if lane == "sync" else AsyncResponsesToolLedger
    # Lane-specific instances are real installed public API objects. Only the CLI's lane varies.
    options: Any = {
        "max_steps": 1 if scenario == "retry-budget" else 3,
        "stream": streaming,
        "eager": scenario == "eager-interruption",
        "ledger": cls("fixture-run", adapt(lane, save)),
    }
    async with AsyncExitStack() as stack:
        if lane == "sync":
            client: Any = stack.enter_context(
                OpenAI(
                    api_key="synthetic-unused",
                    base_url="http://fixture.invalid/v1",
                    max_retries=2,
                    http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
                )
            )
            runner: Any = ResponsesToolRunner(
                browser=BrowserToolset(cast(Any, driver), members=["read_page", "click"], confirm=confirm),
                computer=ComputerToolset(cast(Any, native)),
                functions=[RegisteredFunction(DATA["record_tool"], record)],
            )
        else:
            client = await stack.enter_async_context(
                AsyncOpenAI(
                    api_key="synthetic-unused",
                    base_url="http://fixture.invalid/v1",
                    max_retries=2,
                    http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
                )
            )
            runner = AsyncResponsesToolRunner(
                browser=AsyncBrowserToolset(
                    cast(Any, driver), members=["read_page", "click"], confirm=adapt(lane, confirm)
                ),
                computer=AsyncComputerToolset(cast(Any, native)),
                functions=[AsyncRegisteredFunction(DATA["record_tool"], adapt(lane, record))],
            )
        if scenario == "invalid-history":
            historical = {
                "type": "computer_call_output",
                "call_id": native_call["call_id"],
                "output": {"type": "computer_screenshot", "image_url": DATA["image"]["image_url"]},
            }
            history = [native_call, historical, {"role": "user", "content": "Current fixture"}]
            success = await invoke(runner.run(client, {**params, "input": history}, **options))
            assert success.output_text == "Fixture complete"
            history_count = (len(bodies), len(writes), len(effects))
            for output in ({}, {"type": "computer_screenshot"}, {"type": "computer_screenshot", "image_url": " "}):
                try:
                    await invoke(
                        runner.run(
                            client, {**params, "input": [native_call, {**historical, "output": output}]}, **options
                        )
                    )
                except (ToolRunnerError, ValueError):
                    pass
                else:
                    raise AssertionError("malformed native history was accepted")
                assert (len(bodies), len(writes), len(effects)) == history_count
            return
        if scenario == "inspection":
            turns: Generator[ResponsesRunnerTurn, None, None] | AsyncGenerator[ResponsesRunnerTurn, None]
            turns = runner.iterate(client, params, **options)
            turn = await turns.__anext__() if isinstance(turns, AsyncGenerator) else next(turns)
            assert not turn.tools_executed
            if isinstance(turns, AsyncGenerator):
                await turns.aclose()
            else:
                turns.close()
            try:
                turn.supply_outputs([])
            except ValueError:
                pass
            else:
                raise AssertionError("closed setter was accepted")
        else:
            try:
                await invoke(runner.run(client, params, **options))
            except ToolRunnerError as error:
                if scenario in ("function-throw", "nested-error", "save-after-return", "lost-ack"):
                    assert error.attempted_call_ids == ("record",), error
                if scenario in ("save-after-return", "lost-ack"):
                    assert error.completed_call_ids == ("record",), error
            else:
                raise AssertionError("uncertain or rejected run continued")
        assert len(bodies) == 1
        assert client.max_retries == 2
        previous = clone(writes[-1])
        save_failure = False
        resumed = True
        fresh = [{"role": "user", "content": [{"type": "input_text", "text": "Fresh fixture observation"}]}]
        resume: Any = {"ledger": cls("fixture-run", adapt(lane, save), previous)}
        if scenario == "resume-boundary":
            assert previous["phase"] == "boundary"
            assert previous["returned_call_ids"] == ["record", "read", "native_one"]
            performed = effects[:]
            final = await invoke(runner.run(client, {**params, "input": fresh}, **resume))
            assert final.output_text == "Fixture complete"
            assert effects == performed
            assert bodies[1]["input"] == previous["history"] + fresh
            assert writes[-1]["max_steps"] == 3 and writes[-1]["consumed_requests"] == 2
            returned = [entry for entry in bodies[1]["input"] if entry.get("type", "").endswith("_call_output")]
            assert [entry["call_id"] for entry in returned] == ["record", "read", "native_one"]
            assert returned[-1]["output"] == {"type": "computer_screenshot", "image_url": DATA["image"]["image_url"]}
            try:
                await invoke(runner.run(client, {**params, "input": fresh}, **resume))
            except ToolRunnerError:
                pass
            else:
                raise AssertionError("stale revision passed caller save")
            assert len(bodies) == 2 and effects == performed
            return
        if scenario == "invalid-registry":
            previous["tools"] = [declaration for declaration in previous["tools"] if declaration["type"] != "computer"]
        elif scenario == "retry-budget":
            assert previous["phase"] == "boundary" and previous["consumed_requests"] == 1
        else:
            assert previous["phase"] == "pending"
            expected = {
                "function-throw": ["function:filed"],
                "nested-error": ["function:filed"],
                "save-before-attempt": [],
                "save-after-return": ["function:filed"],
                "lost-ack": ["function:filed"],
                "browser-error": ["click"],
                "browser-refusal": [],
                "native-partial": ["native:Receipt"],
                "inspection": [],
                "eager-interruption": ["function:filed", "read"],
            }
            assert effects == expected[scenario], effects
            if scenario in ("inspection", "save-before-attempt"):
                assert observations == []
            if scenario in ("lost-ack", "browser-error", "browser-refusal"):
                assert len(previous["returned_call_ids"]) == 1
            if scenario in ("function-throw", "nested-error", "save-after-return", "native-partial"):
                assert len(previous["returned_call_ids"]) == 0
        count = (len(bodies), len(writes), len(effects), len(observations))
        try:
            await invoke(runner.run(client, {**params, "input": fresh}, **resume))
        except (ToolRunnerError, ValueError):
            pass
        else:
            raise AssertionError("unsafe or exhausted resume continued")
        assert (len(bodies), len(writes), len(effects), len(observations)) == count


async def budget_case(lane: str, item: Any) -> None:
    scenario = item["scenario"]
    streaming = item["stream"]
    bodies: list[Any] = []
    writes: list[Any] = []
    effects: list[str] = []
    choices: list[Any] = []
    stopped = False
    entered = asyncio.Event()
    release = asyncio.Event()
    large = "PRIVATE_FULL_HISTORY " * 260

    def photo(id: str) -> Any:
        return call("screenshot", {"tab_id": "one"}, id).to_dict()

    def native_call(id: str) -> Any:
        return {**clone(DATA["native"]), "id": "item_" + id, "call_id": id}

    record_call = call("record", {"text": "filed"}, "old").to_dict()
    record_call["name"] = "record"

    def browser_photo(_args: Any) -> Any:
        effects.append("browser")
        return clone(DATA["image"])

    def type_text(_action: Any) -> None:
        effects.append("native-type")

    def native_photo() -> Any:
        effects.append("native-shot")
        return {"type": "computer_screenshot", "image_url": DATA["image"]["image_url"]}

    def record(_args: Any) -> Any:
        effects.append("record")
        return [{"type": "input_text", "text": large}, clone(DATA["image"])]

    def state() -> Any:
        return clone(DATA["state"])

    driver = SimpleNamespace(state=adapt(lane, state), screenshot=adapt(lane, browser_photo))
    native = computer_driver(lane, type=adapt(lane, type_text), screenshot=adapt(lane, native_photo))

    def transport(req: httpx2.Request) -> httpx2.Response:
        bodies.append(json.loads(req.content))
        output = [DATA["final"]]
        if scenario == "bounded":
            if len(bodies) == 1:
                output = [DATA["reasoning"], photo("a"), native_call("n1"), record_call]
            if len(bodies) == 2:
                output = [photo("b"), native_call("n2")]
        elif scenario == "replay":
            output = [record_call]
        elif scenario == "resume" and len(bodies) == 1:
            output = [record_call]
        response = {
            "id": "resp_" + str(len(bodies)),
            "object": "response",
            "created_at": 0,
            "model": "",
            "status": "completed",
            "output": output,
        }
        if streaming:
            return httpx2.Response(200, headers={"content-type": "text/event-stream"}, content=sse(response, False))
        return httpx2.Response(200, json=response)

    def save(value: Any) -> None:
        writes.append(clone(value))

    def compact(snapshot: Any) -> Any:
        nonlocal stopped
        ids = snapshot["eligible_call_ids"][:]
        choices.append(ids)
        snapshot["eligible_call_ids"].append("checked")
        snapshot["history"].clear()
        if scenario == "cancel":
            # Sync cannot wait for an asyncio task: test persistent cancellation
            # after its running callback returns. Async below also holds that call.
            stopped = True
        if scenario == "invalid":
            return {"drop_call_ids": ["old", "old"]}
        if scenario == "protected":
            return {"drop_call_ids": ["checked"]}
        return {"drop_call_ids": ids, "summary": "Fixture summary"}

    async def async_compact(snapshot: Any) -> Any:
        if scenario == "cancel":
            entered.set()
            await release.wait()
        return compact(snapshot)

    params: Any = {"model": "", "input": "Process the local fixture", "store": False}
    cls = ResponsesToolLedger if lane == "sync" else AsyncResponsesToolLedger
    context_budget: Any = {
        "max_input_bytes": 3600,
        "max_input_images": 2,
        "compact": compact if lane == "sync" else async_compact,
    }
    options: Any = {
        "stream": streaming,
        "max_steps": 2 if scenario == "resume" else 4,
        "ledger": cls("budget-fixture", adapt(lane, save)),
        "context_budget": context_budget,
        "cancelled": lambda: stopped,
    }
    if scenario in ("invalid", "protected", "replay", "cancel"):
        params["input"] = [
            {"role": "user", "content": "Process the local fixture"},
            record_call,
            {"type": "function_call_output", "call_id": "old", "output": large},
        ]
        if scenario == "protected":
            checked = native_call("checked")
            checked["pending_safety_checks"] = [{"id": "check", "code": "fixture", "message": "confirm"}]
            params["input"].extend(
                [
                    photo("latest"),
                    {"type": "function_call_output", "call_id": "latest", "output": [clone(DATA["image"])]},
                    checked,
                    {
                        "type": "computer_call_output",
                        "call_id": "checked",
                        "acknowledged_safety_checks": clone(checked["pending_safety_checks"]),
                        "output": {"type": "computer_screenshot", "image_url": DATA["image"]["image_url"]},
                    },
                    native_call("current"),
                    {
                        "type": "computer_call_output",
                        "call_id": "current",
                        "output": {"type": "computer_screenshot", "image_url": DATA["image"]["image_url"]},
                    },
                ]
            )
            context_budget["max_input_images"] = 3
    async with AsyncExitStack() as stack:
        if lane == "sync":
            client: Any = stack.enter_context(
                OpenAI(
                    api_key="synthetic-unused",
                    base_url="http://fixture.invalid/v1",
                    max_retries=2,
                    http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
                )
            )
            runner: Any = ResponsesToolRunner(
                browser=BrowserToolset(cast(Any, driver), members=["screenshot"]),
                computer=ComputerToolset(cast(Any, native)),
                functions=[RegisteredFunction(DATA["record_tool"], record)],
            )
        else:
            client = await stack.enter_async_context(
                AsyncOpenAI(
                    api_key="synthetic-unused",
                    base_url="http://fixture.invalid/v1",
                    max_retries=2,
                    http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
                )
            )
            runner = AsyncResponsesToolRunner(
                browser=AsyncBrowserToolset(cast(Any, driver), members=["screenshot"]),
                computer=AsyncComputerToolset(cast(Any, native)),
                functions=[AsyncRegisteredFunction(DATA["record_tool"], adapt(lane, record))],
            )
        if scenario == "cancel" and lane == "async":
            running = asyncio.create_task(runner.run(client, params, **options))
            await entered.wait()
            stopped = True
            assert (len(writes), len(bodies), len(effects)) == (0, 0, 0)
            release.set()
            try:
                await running
            except (ToolRunnerError, ValueError, asyncio.CancelledError):
                pass
            else:
                raise AssertionError("cancelled policy admitted a request")
        elif scenario in ("invalid", "protected", "replay", "cancel"):
            try:
                await invoke(runner.run(client, params, **options))
            except (ToolRunnerError, ValueError, asyncio.CancelledError):
                pass
            else:
                raise AssertionError("invalid decision or replay admitted effects")
        else:
            result = await invoke(runner.run(client, params, **options))
            assert result.output_text == "Fixture complete"
        assert choices, "policy must have actually run"
        if scenario in ("invalid", "protected", "cancel"):
            assert (len(writes), len(bodies), len(effects)) == (0, 0, 0)
            assert choices == [["old"]]
            return
        for request in bodies:
            assert request["truncation"] == "disabled"
            assert len(json.dumps(request["input"], ensure_ascii=False, separators=(",", ":")).encode()) <= 3600
            pictures = 0
            for value in request["input"]:
                if value.get("type") == "computer_call_output":
                    pictures += 1
                elif value.get("type") == "function_call_output" and isinstance(value["output"], list):
                    pictures += sum(block.get("type") == "input_image" for block in value["output"])
            assert pictures <= 2
        final_input = bodies[-1]["input"]
        assert not any(entry.get("call_id") == "old" for entry in final_input)
        receipts = [
            entry
            for entry in final_input
            if entry.get("role") == "user"
            and isinstance(entry.get("content"), str)
            and entry["content"].startswith("Omitted completed tool receipts:")
            and "old" in entry["content"]
        ]
        assert receipts
        receipt = receipts[0]
        assert "external success is unverified" in receipt["content"]
        assert large not in receipt["content"] and DATA["image"]["image_url"] not in receipt["content"]
        assert "call_id" not in receipt
        assert len(writes[-1]) == 14
        assert "PRIVATE_FULL_HISTORY" in json.dumps(writes[-1]["history"])
        assert "Omitted completed tool receipts:" not in json.dumps(writes[-1]["history"])
        if scenario == "bounded":
            assert choices == [["old"], ["a", "n1", "old"]]
            assert effects == [
                "browser",
                "native-type",
                "native-shot",
                "record",
                "browser",
                "native-type",
                "native-shot",
            ]
            assert [entry["call_id"] for entry in final_input if entry.get("type", "").endswith("_call")] == ["b", "n2"]
            assert any(entry.get("type") == "reasoning" for entry in final_input)
            assert writes[-1]["returned_call_ids"] == ["a", "n1", "old", "b", "n2"]
        elif scenario == "replay":
            assert not effects and len(bodies) == 1
        elif scenario == "resume":
            assert effects == ["record"]
            previous = next(
                value
                for value in writes
                if value["phase"] == "boundary"
                and value["consumed_requests"] == 1
                and "old" in value["returned_call_ids"]
            )
            count = len(bodies)
            resume: Any = {
                "stream": streaming,
                "ledger": cls("budget-fixture", adapt(lane, save), previous),
                "context_budget": context_budget,
            }
            await invoke(runner.run(client, {**params, "input": "Fresh observed fixture"}, **resume))
            assert len(bodies) == count + 1
            assert bodies[-1]["input"][-1] == {"role": "user", "content": "Fresh observed fixture"}
            assert effects == ["record"]
            assert writes[-1]["max_steps"] == 2 and writes[-1]["consumed_requests"] == 2
            exhausted = next(
                value for value in reversed(writes) if value["phase"] == "boundary" and value["consumed_requests"] == 2
            )
            before = (len(bodies), len(writes), len(choices), len(effects))
            try:
                await invoke(
                    runner.run(
                        client,
                        {**params, "input": "Fresh again"},
                        **{
                            **resume,
                            "ledger": cls("budget-fixture", adapt(lane, save), exhausted),
                        },
                    )
                )
            except (ToolRunnerError, ValueError):
                pass
            else:
                raise AssertionError("original request lifetime was increased")
            assert (len(bodies), len(writes), len(choices), len(effects)) == before


async def rich_read(lane: str, item: Any) -> None:
    scenario, member = str(item["scenario"]), str(item["member"])
    fixture: dict[str, Any] = clone(DATA["rich_reads"]["report"])
    report: str | dict[str, Any] = fixture
    expected = clone(report)
    events: list[str] = []
    if scenario == "legacy":
        report = json.dumps({**fixture, "owner_private": "SYNTHETIC_PRIVATE"})
    elif scenario == "scalar":
        fixture["text"] = "\ud800"
    elif scenario == "aggregate":
        report = {"version": 1, "text": "", "elements": [], "omitted": []}
        report["text"] = "Visible 😀\n" * 20_000
    if not isinstance(report, str):
        report["private_raw"] = object()
        if report["elements"]:
            report["elements"][0]["record_id"] = object()
            report["elements"][0]["options"][0]["raw_option"] = object()

    def state() -> Any:
        events.append("state")
        if len(events) == 3 and scenario == "state":
            raise ValueError("SYNTHETIC_PRIVATE")
        if len(events) == 3 and scenario == "projection":
            current = cast(dict[str, Any], report)
            current["text"] = "SYNTHETIC_PRIVATE"
            current["elements"][0]["ref"] = "wrong_after_final_state"
            current["elements"][0]["options"][0]["value"] = "SYNTHETIC_PRIVATE"
            current["omitted"].append("private")
        return clone(DATA["state"])

    def read(_args: Any) -> Any:
        events.append("read")
        return report

    driver = SimpleNamespace(state=adapt(lane, state))
    setattr(driver, member, adapt(lane, read))
    cls: Any = BrowserToolset if lane == "sync" else AsyncBrowserToolset
    browser = cls(driver, members=[member])
    action = call(member, vector(member)["arguments"], "read-contract")
    if scenario in ("scalar", "text-refs", "state"):
        error = await expect_error(lambda: invoke(browser.execute(action)))
        assert str(error) == ("Browser state report failed." if scenario == "state" else "Browser read report failed.")
        assert events == (["state", "read", "state"] if scenario == "state" else ["state", "read"])
        return
    output = payload(await invoke(browser.execute(action)))
    assert output["ok"] is True and events == ["state", "read", "state"]
    if scenario == "projection":
        assert output["result"] == expected and "SYNTHETIC_PRIVATE" not in json.dumps(output)
    elif scenario == "legacy":
        assert output["result"] == report
    else:
        current = cast(dict[str, Any], report)
        assert output["result"]["text"] == current["text"] and "private_raw" not in json.dumps(output)
        current["text"] += "\0"
        events.clear()
        next_output = payload(await invoke(browser.execute(action)))
        assert next_output["result"]["text"] == current["text"] and "private_raw" not in json.dumps(next_output)
        assert events == ["state", "read", "state"]


async def selective_case(lane: str, item: Any) -> None:
    variants = {
        "prefix-and-suffix": ["ordered", "local-ordered"],
        "empty-versus-omitted": ["omitted", "null", "empty"],
        "native-names": ["ordinary", "native"],
        "pending-ledger": ["pending"],
        "changed-completion": ["changed", "undeclared"],
        "server-default-override": ["ordered"],
    }[item["scenario"]]
    for variant in variants:
        await selective_run(lane, variant, item["scenario"] == "server-default-override")


async def selective_run(lane: str, variant: str, default_early_policy: bool = False) -> None:
    bodies: list[Any] = []
    effects: list[str] = []
    approvals: list[str] = []
    writes: list[Any] = []
    native_names = variant in ("ordinary", "native")
    names = ["computer"] if native_names else ["fast", "slow"]

    def execute(name: str, args: Any) -> str:
        effects.append(name + ":" + str(args["text"]))
        return str(args["text"])

    def native_type(action: Any) -> None:
        effects.append("native:" + action.text)

    def image() -> Any:
        effects.append("native-shot")
        return {"type": "computer_screenshot", "image_url": DATA["image"]["image_url"]}

    def consent(name: str, _action: Any) -> bool:
        approvals.append(name)
        return True

    def save(checkpoint: Any) -> None:
        writes.append(clone(checkpoint))

    def ordinary(name: str, id: str) -> Any:
        result = call(name, {"text": id}, id).to_dict()
        result["name"] = name
        return result

    fast, slow = ordinary("fast", "one"), ordinary("slow", "two")
    batch = [fast, slow]
    if variant in ("ordered", "local-ordered"):
        batch = [
            fast,
            slow,
            DATA["reasoning"],
            {**DATA["final"], "id": "commentary", "phase": "commentary"},
            ordinary("fast", "three"),
        ]
        if variant == "ordered":
            batch.insert(
                4,
                {
                    "type": "web_search_call",
                    "id": "ws_fixture",
                    "status": "completed",
                    "action": {"type": "search", "query": "fixture"},
                },
            )
    elif variant in ("omitted", "null", "empty"):
        batch = [fast]
    elif native_names:
        native_call = clone(DATA["native"])
        native_call["pending_safety_checks"] = [{"id": "safe", "code": "fixture", "message": "confirm"}]
        named = ordinary("computer", "ordinary")
        batch = [native_call, named] if variant == "native" else [named, native_call]
    elif variant == "undeclared":
        batch.append(
            {
                "type": "file_search_call",
                "id": "fs_fixture",
                "status": "completed",
                "queries": ["fixture"],
                "results": [],
            }
        )
    if variant == "null":
        policy: Any = None
    elif variant == "empty":
        policy = {}
    elif variant == "native":
        policy = {"computer": True}
    else:
        policy = {"functions": ["computer"] if native_names else ["fast"]}
    registration = {} if variant == "omitted" or default_early_policy else {"early_execution": policy}

    def transport(req: httpx2.Request) -> httpx2.Response:
        bodies.append(json.loads(req.content))
        output = batch if len(bodies) == 1 else [DATA["final"]]
        completed = clone(output)
        if variant == "changed" and len(bodies) == 1:
            completed[1]["arguments"] = json.dumps({"text": "retargeted"})
        response = {
            "id": "resp_" + str(len(bodies)),
            "object": "response",
            "created_at": 0,
            "model": "",
            "status": "completed",
            "output": output,
        }
        return httpx2.Response(
            200, headers={"content-type": "text/event-stream"}, content=sse(response, False, completed)
        )

    params: Any = {"model": "", "input": "Process the local fixture", "store": False}
    if variant == "ordered":
        params["tools"] = [{"type": "web_search"}]
    ledger_cls: Any = ResponsesToolLedger if lane == "sync" else AsyncResponsesToolLedger
    ledger = ledger_cls("selective", adapt(lane, save))
    options: Any = {
        "stream": True,
        "eager": True,
        "max_steps": 3,
        "approve_safety_checks": adapt(lane, partial(consent, "safety")),
        "before_action": adapt(lane, partial(consent, "action")),
    }
    if variant == "pending":
        options["ledger"] = ledger
    native = computer_driver(lane, type=adapt(lane, native_type), screenshot=adapt(lane, image))
    async with AsyncExitStack() as stack:
        if lane == "sync":
            client: Any = stack.enter_context(
                OpenAI(
                    api_key="synthetic-unused",
                    base_url="http://fixture.invalid/v1",
                    max_retries=0,
                    http_client=httpx2.Client(transport=httpx2.MockTransport(transport)),
                )
            )
            runner: Any = ResponsesToolRunner(
                computer=ComputerToolset(cast(Any, native)),
                functions=[
                    RegisteredFunction(
                        cast(FunctionToolParam, {**DATA["record_tool"], "name": name}),
                        partial(execute, name),
                        allow_output_override=True,
                    )
                    for name in names
                ],
                **registration,
            )
        else:
            client = await stack.enter_async_context(
                AsyncOpenAI(
                    api_key="synthetic-unused",
                    base_url="http://fixture.invalid/v1",
                    max_retries=0,
                    http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)),
                )
            )
            runner = AsyncResponsesToolRunner(
                computer=AsyncComputerToolset(cast(Any, native)),
                functions=[
                    AsyncRegisteredFunction(
                        cast(FunctionToolParam, {**DATA["record_tool"], "name": name}),
                        adapt(lane, partial(execute, name)),
                        allow_output_override=True,
                    )
                    for name in names
                ],
                **registration,
            )
        turns = runner.iterate(client, params, **options)

        async def advance() -> Any:
            return await turns.__anext__() if lane == "async" else next(turns)

        async def close() -> None:
            if lane == "async":
                await turns.aclose()
            else:
                turns.close()

        stack.push_async_callback(close)
        if variant in ("changed", "undeclared"):
            error = await expect_error(advance)
            assert isinstance(error, ToolRunnerError)
            assert error.attempted_call_ids == error.completed_call_ids == ("one",)
            assert effects == ["fast:one"] and len(bodies) == 1
            return
        turn = await advance()
        assert not turn.final
        first_id = (
            ()
            if variant in ("empty", "ordered")
            else (("native_one" if variant == "native" else "ordinary" if variant == "ordinary" else "one"),)
        )
        assert turn.attempted_call_ids == turn.completed_call_ids == first_id
        assert turn.tools_executed is bool(first_id)
        assert approvals == (["safety", "action", "action"] if variant == "native" else [])
        if variant in ("empty", "omitted", "null"):
            assert effects == ([] if variant == "empty" else ["fast:one"])
            if variant != "empty":
                await expect_error(lambda: invoke(turn.supply_outputs([])))
            await close()
            assert len(bodies) == 1
            await expect_error(lambda: invoke(turn.supply_outputs([])))
            return
        if variant == "pending":
            previous = writes[-1]
            assert previous["phase"] == "pending" and previous["pending_items"] == batch
            assert previous["attempted_call_ids"] == previous["returned_call_ids"] == ["one"]
            await close()
            counts = len(bodies), len(writes), len(effects), len(approvals)
            resume = {**options, "ledger": ledger_cls("selective", adapt(lane, save), previous)}
            await expect_error(
                lambda: invoke(runner.run(client, {**params, "input": "Fresh fixture observation"}, **resume))
            )
            assert (len(bodies), len(writes), len(effects), len(approvals)) == counts
            return
        if variant in ("ordered", "local-ordered"):
            assert effects == ([] if variant == "ordered" else ["fast:one"])
            supplied = {"type": "function_call_output", "call_id": "two", "output": "human result"}
            turn.supply_outputs([supplied])
            forbidden_id = "missing" if variant == "ordered" else "one"
            await expect_error(lambda: invoke(turn.supply_outputs([supplied, {**supplied, "call_id": forbidden_id}])))
        else:
            assert effects == (["native:Receipt", "native-shot"] if variant == "native" else ["computer:ordinary"])
        final = await advance()
        assert final.final and len(bodies) == 2
        history = bodies[1]["input"]
        returned = [value for value in history if value.get("type", "").endswith("_call_output")]
        ids = tuple(value["call_id"] for value in batch if value["type"] in ("function_call", "computer_call"))
        assert final.attempted_call_ids == final.completed_call_ids == ids
        assert tuple(value["call_id"] for value in returned) == ids
        assert [value["id"] for value in history if "id" in value] == [value["id"] for value in batch]
        if variant in ("ordered", "local-ordered"):
            assert effects == ["fast:one", "fast:three"] and returned[1]["output"] == "human result"
        else:
            assert approvals == ["safety", "action", "action"]
            assert effects == (
                ["native:Receipt", "native-shot", "computer:ordinary"]
                if variant == "native"
                else ["computer:ordinary", "native:Receipt", "native-shot"]
            )
            assert next(value for value in returned if value["type"] == "computer_call_output")["output"] == {
                "type": "computer_screenshot",
                "image_url": DATA["image"]["image_url"],
            }
        await expect_error(lambda: invoke(turn.supply_outputs([])))


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consumer", type=Path, required=True, help="Existing installed virtual environment")
    parser.add_argument("--archive", type=Path, required=True, help="Wheel installed in the consumer")
    parser.add_argument("--source", type=Path, required=True, help="SDK source checkout used for hash comparison")
    parser.add_argument("--package-head", required=True, help="Commit whose helper source must match the wheel")
    args = parser.parse_args()
    installed = Path(openai_file).resolve().parent
    consumer = args.consumer.resolve()
    assert Path(sys.prefix).resolve() == consumer, "Run with the specified consumer environment's Python"
    assert "site-packages" in installed.parts and installed.is_relative_to(consumer), "Must use an installed wheel"
    checkout, archive = args.source.resolve(), args.archive.resolve()
    hashes = {}
    with ZipFile(archive) as wheel:
        for name in ("browser", "computer", "responses_tool_runner"):
            file = "openai/lib/" + name + ".py"
            packed = installed / "lib" / (name + ".py")
            assert sha(packed) == sha(checkout / "src" / file), name + " checkout mismatch"
            assert sha(packed) == hashlib.sha256(wheel.read(file)).hexdigest(), name + " archive mismatch"
            revision_file = subprocess.check_output(
                ["git", "-C", str(checkout), "show", args.package_head + ":src/" + file]
            )
            assert sha(packed) == hashlib.sha256(revision_file).hexdigest(), name + " package head mismatch"
            hashes[name] = sha(packed)
    for lane in ("sync", "async"):
        await basic(lane)
        await v1(lane)
        for stream, eager in ((False, False), (True, False), (True, True)):
            await check(
                lane,
                f"mixed:{stream}:{eager}",
                partial(mixed, lane, stream, eager),
            )
        for eager in (False, True):
            await check(lane, f"interruption:{eager}", partial(mixed, lane, True, eager, True))
        for item in DATA["iteration"]:
            await check(lane, item["id"], partial(iteration, lane, item))
        for item in DATA["ledger"]:
            await check(lane, item["id"], partial(ledger_case, lane, item))
        for item in DATA["budget"]:
            await check(lane, item["id"], partial(budget_case, lane, item))
        for item in DATA["rich_reads"]["cases"]:
            await check(lane, item["id"], partial(rich_read, lane, item))
        for item in DATA["selective"]:
            await check(lane, item["id"], partial(selective_case, lane, item))
        for id in DATA["boundary_ids"]:
            assert sum(c["id"] == id and c["lane"] == lane for c in CHECKS) == 1, id
    print(
        json.dumps(
            {
                "runtime": platform.python_version(),
                "installed": str(installed),
                "archive": str(archive),
                "archiveSha256": sha(archive),
                "source": str(checkout),
                "sourceHead": subprocess.check_output(
                    ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
                ).strip(),
                "packageSourceHead": subprocess.check_output(
                    ["git", "-C", str(checkout), "rev-parse", "--verify", args.package_head + "^{commit}"], text=True
                ).strip(),
                "helperHashes": hashes,
                "catalogSha256": sha(HERE / "vectors.json"),
                "checks": CHECKS,
            },
            indent=2,
        )
    )
    if any(not item["pass"] for item in CHECKS):
        sys.exit(1)


asyncio.run(main())
