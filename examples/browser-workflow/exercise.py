"""Exercise the real local apps with no API key; write observations for cross-SDK comparison."""

import os
import sys
import json
import asyncio
import argparse
from copy import deepcopy
from typing import Any, AsyncGenerator
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

from workflow import Workflow, main as workflow_main, serve, open_workflow
from playwright.async_api import Playwright, async_playwright

from openai import AsyncOpenAI
from openai.lib.browser import BrowserCancelledError, BrowserConfirmContext
from openai.lib.responses_tool_runner import ToolRunnerError, AsyncResponsesToolRunner


async def allow(_action: BrowserConfirmContext) -> bool:
    return True


async def refuse(_action: BrowserConfirmContext) -> bool:
    return False


async def stored_after_stop(workflow: Workflow) -> dict[str, Any]:
    return json.loads(
        await workflow.page.evaluate(
            """id => JSON.stringify({
          bookings: JSON.parse(localStorage.getItem(`workflow.${id}.bookings`) || '{}'),
          correspondence: JSON.parse(localStorage.getItem(`workflow.${id}.correspondence`) || '{}')
        })""",
            workflow.variant,
        )
    )


async def check_serve_stop() -> None:
    started = asyncio.Event()
    args = argparse.Namespace(mode="serve", receipt=None, data=None, fixture="A")

    def ready(*_args: object, **_kwargs: object) -> None:
        started.set()

    with patch("builtins.print", side_effect=ready):
        running = asyncio.create_task(workflow_main(args))
        try:
            await asyncio.wait_for(started.wait(), 5)
            running.cancel()
            await asyncio.wait_for(running, 5)
        finally:
            if not running.done():
                running.cancel()
                await asyncio.gather(running, return_exceptions=True)


async def check_headed() -> None:
    display = {
        "DISPLAY": ":77",
        "WAYLAND_DISPLAY": "wayland-77",
        "XAUTHORITY": "/tmp/local-display-cookie",
        "XDG_RUNTIME_DIR": "/tmp/local-wayland-runtime",
    }
    # Start the actual host transport before simulating the Linux caller's launch settings.
    async with async_playwright() as playwright:

        @asynccontextmanager
        async def started() -> AsyncGenerator[Playwright, None]:
            yield playwright

        with serve() as server:
            for headed in (True, False):
                launch = AsyncMock(side_effect=RuntimeError("Controlled launch boundary"))
                with (
                    patch("browser_driver.async_playwright", started),
                    patch.object(playwright.chromium, "launch", launch),
                    patch.object(sys, "platform", "linux"),
                    patch.dict(
                        os.environ,
                        {
                            **display,
                            "OPENAI_API_KEY": "synthetic-secret-never-forward",
                            "PYTHONPATH": "synthetic-private",
                        },
                    ),
                ):
                    try:
                        async with open_workflow(server, "A", confirm=allow, headed=headed):
                            raise AssertionError("The controlled launch must refuse browser creation")
                    except RuntimeError as error:
                        assert str(error) == "Controlled launch boundary"
                launch.assert_awaited_once()
                call = launch.await_args
                assert call is not None
                options = call.kwargs
                assert options["headless"] is not headed
                allowed = {"PATH", "HOME", "TMPDIR"}
                if headed:
                    allowed.update(display)
                assert set(options["env"]).issubset(allowed)
                if headed:
                    assert {key: options["env"][key] for key in display} == display
    print("PASS Linux headed workflow admits only trusted display settings and excludes private SDK environment")


async def main(output: Path | None) -> None:
    await check_serve_stop()
    await check_headed()
    receipts: list[dict[str, Any]] = []
    with patch("workflow.os.getuid", None, create=True):
        try:
            await workflow_main(argparse.Namespace(receipt="unsupported-private-receipt.json"))
        except RuntimeError as error:
            assert "owner-only POSIX file permissions" in str(error)
        else:
            raise AssertionError("A private receipt started without owner-only file permissions")
    with serve() as server:
        approvals: list[str] = []

        async def approve_navigation(action: BrowserConfirmContext) -> bool:
            approvals.append(action["member"])
            return True

        async with open_workflow(server, "A", confirm=approve_navigation) as navigation:
            initial_url = navigation.page.url
            for url in (
                server[0] + "/fixtures.json",
                server[0] + "/app.js",
                "about:blank",
                server[0] + "/inbox?fixture=B",
            ):
                navigation_result = await navigation.execute("navigate", {"tab_id": None, "url": url})
                assert not navigation_result["ok"], "Navigation must stay within the selected workflow pages"
                assert navigation.page.url == initial_url
                assert approvals == []
            for route in ("/schedule", "/dispatch", "/inbox"):
                url = server[0] + route + "?fixture=A"
                navigation_result = await navigation.execute("navigate", {"tab_id": None, "url": url})
                assert navigation_result["ok"]
                assert navigation.page.url == url
                await navigation.observe()
            assert approvals == ["navigate", "navigate", "navigate"]
        async with AsyncOpenAI(api_key="synthetic-no-requests") as client:
            for stage in ("runner", "verification"):
                async with open_workflow(server, "A", confirm=allow) as current:
                    mock_run = AsyncMock()
                    mock_verify = AsyncMock()
                    if stage == "runner":
                        mock_run.side_effect = ToolRunnerError("Maximum tool steps reached.", [], [])
                    else:
                        mock_verify.side_effect = ToolRunnerError("PRIVATE_VERIFICATION_SENTINEL", [], [])
                    with (
                        patch.object(AsyncResponsesToolRunner, "run", mock_run),
                        patch.object(current, "verify", mock_verify),
                    ):
                        try:
                            await current.run(client, "local", "responses")
                        except ToolRunnerError:
                            pass
                        else:
                            raise AssertionError("The controlled failure was not raised.")
                    expected = (
                        {"name": "ToolRunnerError", "message": "Maximum tool steps reached."}
                        if stage == "runner"
                        else None
                    )
                    assert current.runner_error == expected
                    assert "PRIVATE_VERIFICATION_SENTINEL" not in json.dumps(current.runner_error)
        for variant, id, slot, recipient in (
            ("A", "REQ-401", "R2 Garden", "cedar@example.test"),
            ("B", "REQ-718", "T2 Garden", "aster@example.test"),
        ):
            async with open_workflow(server, variant, confirm=allow) as w:
                assert not await w.verify(), "Done at the start must stay unverified"
                checks: list[dict[str, Any]] = []
                for label in (f"Open {id}", f"Reserve {slot}", "Outgoing", f"Send {id} to {recipient}"):
                    observation = json.loads(await w.observe())
                    actions = await w.candidates(json.dumps(observation))
                    checks.append(
                        {
                            "text": observation["text"],
                            "actions": [
                                {"id": a["id"], "description": a["description"], "done": bool(a.get("done"))}
                                for a in actions
                            ],
                        }
                    )
                    action = next(a for a in actions if a["description"] == f"Click {label}")
                    assert "execute" in action
                    result = await action["execute"]()
                    assert isinstance(result, dict)
                    assert result["ok"], result
                await w.page.reload(wait_until="domcontentloaded")
                assert await w.verify(), "Saved records must pass after reload"
                receipts.append({"variant": variant, "checks": checks, "stored": await w.stored(), "verified": True})

        async with open_workflow(server, "A", confirm=allow) as stale_store:
            await stale_store.page.evaluate(
                """() => {
                  localStorage.setItem('workflow.A.bookings', '{"unfinished":');
                  localStorage.setItem('workflow.A.selected', JSON.stringify('REQ-401'));
                }"""
            )
            await stale_store.page.goto(server[0] + "/dispatch?fixture=A")
            assert "No saved bookings" in await stale_store.page.locator("#app").inner_text()
            assert await stale_store.page.evaluate(
                """() => ({bookings: localStorage.getItem('workflow.A.bookings'),
                   selected: localStorage.getItem('workflow.A.selected')})"""
            ) == {"bookings": None, "selected": json.dumps("REQ-401")}
            assert not await stale_store.verify()
            await stale_store.page.evaluate(
                """() => localStorage.setItem('workflow.A.bookings', JSON.stringify({
                    obsolete: {request:'obsolete', slot:'R2', time:'10:00'},
                    'REQ-401': null,
                }))"""
            )
            await stale_store.page.goto(server[0] + "/dispatch?fixture=A")
            assert await stale_store.page.locator("[data-send]").count() == 0
            assert await stale_store.page.locator("[data-revise]").count() == 2
            await stale_store.page.locator('[data-revise="obsolete"]').click()
            await stale_store.page.locator('[data-revise="REQ-401"]').click()
            assert await stale_store.stored() == {"bookings": {}, "correspondence": {}}
            assert not await stale_store.verify()
        for loss in ("page", "context"):
            async with open_workflow(server, "A", confirm=allow) as session:
                assert not session.stopped
                if loss == "page":
                    await session.page.close()
                else:
                    await session.driver.context.close()
                assert session.stopped, loss
        allow_revision = True

        async def confirm_revision(_action: BrowserConfirmContext) -> bool:
            return allow_revision

        async with open_workflow(server, "A", confirm=confirm_revision) as wrong:
            for label in ("Open REQ-401", "Reserve R1 Marina", "Outgoing", "Send REQ-401 to cedar@example.test"):
                actions = await wrong.candidates(await wrong.observe())
                action = next(a for a in actions if a["description"] == f"Click {label}")
                assert "execute" in action
                result = await action["execute"]()
                assert isinstance(result, dict)
                assert result["ok"], result
            assert not await wrong.verify(), "Approved undersized room must stay unverified"
            assert (await wrong.stored())["bookings"]["REQ-401"]["slot"] == "R1", "Do not repair a wrong choice"
            assert "do not meet the request" in json.loads(await wrong.observe())["lastVerification"]
            for label in (
                "Rooms",
                "Revise booking REQ-401",
                "Reserve R2 Garden",
                "Outgoing",
                "Send REQ-401 to cedar@example.test",
                "Rooms",
            ):
                actions = await wrong.candidates(await wrong.observe())
                action = next(a for a in actions if a["description"] == f"Click {label}")
                assert "execute" in action
                result = await action["execute"]()
                assert isinstance(result, dict) and result["ok"]
                if label == "Revise booking REQ-401":
                    assert await wrong.stored() == {"bookings": {}, "correspondence": {}}
                    assert json.loads(await wrong.observe())["lastVerification"] is None
            await wrong.page.wait_for_url("**/schedule?fixture=A")
            assert await wrong.verify(), "An approved revision can correct the saved result"
            corrected = await wrong.stored()
            revise = next(
                a
                for a in await wrong.candidates(await wrong.observe())
                if a["description"] == "Click Revise booking REQ-401"
            )
            allow_revision = False
            assert "execute" in revise
            try:
                await revise["execute"]()
                raise AssertionError("Revision was not refused")
            except BrowserCancelledError:
                pass
            assert await stored_after_stop(wrong) == corrected, "Refusing revision preserves both saved records"

        async with open_workflow(server, "A", confirm=refuse) as w:
            action = next(a for a in await w.candidates(await w.observe()) if a["description"] == "Click Open REQ-401")
            assert "execute" in action
            try:
                await action["execute"]()
            except BrowserCancelledError:
                assert w.stopped
            assert w.stopped
            assert w.refused, "A refusal must remain distinct from Stop"
            try:
                await action["execute"]()
                raise AssertionError("A refusal cannot be retried")
            except BrowserCancelledError:
                pass
            assert await stored_after_stop(w) == {"bookings": {}, "correspondence": {}}

        async with open_workflow(server, "A", confirm=allow) as w:
            old = next(a for a in await w.candidates(await w.observe()) if a["description"] == "Click Open REQ-401")
            await w.observe()
            assert "execute" in old
            result = await old["execute"]()
            assert isinstance(result, dict)
            assert not result["ok"], "Do not follow refs replaced by a newer observation"
            assert await w.stored() == {"bookings": {}, "correspondence": {}}
            stopped = next(a for a in await w.candidates(await w.observe()) if a["description"] == "Click Open REQ-401")
            assert "execute" in stopped
            w.stopped = True
            assert not w.refused, "Stop is not a refusal"
            try:
                await stopped["execute"]()
                raise AssertionError("A stopped session cannot act")
            except BrowserCancelledError:
                pass
            assert await stored_after_stop(w) == {"bookings": {}, "correspondence": {}}
        with TemporaryDirectory(prefix="workflow-fixture-") as directory:
            fixture = deepcopy(server[1]["A"])
            fixture["task"] = "Complete request REQ-401. Reserve the cheapest eligible room and send confirmation."
            custom_data = {"C": fixture}
            fixture["requests"].insert(0, {**fixture["requests"][0], "id": "REQ-4"})
            path = Path(directory) / "fixtures.json"
            path.write_text(json.dumps(custom_data))
            read_bytes = Path.read_bytes

            def replace_after_read(source: Path) -> bytes:
                data = read_bytes(source)
                if source == path:
                    path.write_text(json.dumps({"C": {**fixture, "task": "Replacement file"}}))
                return data

            with patch.object(Path, "read_bytes", replace_after_read), serve(path) as custom:
                path.write_text("{}")
                async with open_workflow(custom, "C", confirm=allow) as w:
                    browser_fixtures = await w.page.evaluate("window.workflowFixtures")
                    assert browser_fixtures["C"]["task"] == fixture["task"], "Startup data must match the verifier"
                    for label in (
                        "Open REQ-401",
                        "Reserve R2 Garden",
                        "Outgoing",
                        "Send REQ-401 to cedar@example.test",
                    ):
                        actions = await w.candidates(await w.observe())
                        action = next(item for item in actions if item["description"] == f"Click {label}")
                        assert "execute" in action
                        result = await action["execute"]()
                        assert isinstance(result, dict) and result["ok"]
                    assert await w.verify(), "Verification must use the exact selected ID"
            for request_id in ("constructor", "__proto__"):
                named = deepcopy(server[1]["A"])
                named["requestId"] = request_id
                named["requests"][0]["id"] = request_id
                path.write_text(json.dumps({"C": named}))
                with serve(path) as named_server:
                    async with open_workflow(named_server, "C", confirm=allow) as w:
                        for label in (
                            f"Open {request_id}",
                            "Reserve R2 Garden",
                            "Outgoing",
                            f"Send {request_id} to cedar@example.test",
                        ):
                            action = next(
                                a for a in await w.candidates(await w.observe()) if a["description"] == f"Click {label}"
                            )
                            assert "execute" in action
                            result = await action["execute"]()
                            assert isinstance(result, dict) and result["ok"]
                        assert await w.verify()
                        await w.page.reload()
                        assert await w.verify(), "Saved IDs survive JSON storage and reload"
            for group, field, value in (
                ("requests", "name", None),
                ("requests", "recipient", 3),
                ("requests", "time", ""),
                ("requests", "equipment", []),
                ("requests", "people", True),
                ("requests", "people", 1.5),
                ("requests", "people", 9_007_199_254_740_993),
                ("requests", "budget", -1),
                ("requests", "budget", None),
                ("requests", "budget", 9_007_199_254_740_992),
                ("slots", "id", False),
                ("slots", "room", []),
                ("slots", "time", ""),
                ("slots", "equipment", "projector"),
                ("slots", "equipment", [7]),
                ("slots", "capacity", 0),
                ("slots", "capacity", 1.5),
                ("slots", "capacity", 9_007_199_254_740_992),
                ("slots", "price", -1),
                ("slots", "price", None),
                ("slots", "price", 1e100),
            ):
                invalid: dict[str, Any] = dict(deepcopy(server[1]["A"]))
                invalid[group][0][field] = value
                path.write_text(json.dumps({"C": invalid}))
                try:
                    with serve(path):
                        raise AssertionError(f"Invalid {group}.{field} accepted")
                except ValueError as error:
                    assert f"{group}[0].{field} is invalid" in str(error)
            for group in ("requests", "slots"):
                invalid = dict(deepcopy(server[1]["A"]))
                invalid[group][1]["id"] = invalid[group][0]["id"]
                path.write_text(json.dumps({"C": invalid}))
                try:
                    with serve(path):
                        raise AssertionError(f"Duplicate {group} ID accepted")
                except ValueError as error:
                    assert "unique" in str(error) or "one exact requestId" in str(error)
            fixture["requests"].append(deepcopy(fixture["requests"][1]))
            path.write_text(json.dumps(custom_data))
            try:
                with serve(path):
                    raise AssertionError("Duplicate selected ID accepted")
            except ValueError:
                pass
    if output:
        output.write_text(json.dumps(receipts, indent=2) + "\n")
    print(
        "PASS A, B, persisted IDs, approved revision, refused revision, invalid custom data, early Done, Stop and stale refs."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    asyncio.run(main(parser.parse_args().output))
