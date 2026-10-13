"""Verify a real owned target before asking for approval, without consuming its ref."""

from __future__ import annotations

import json
import asyncio

from workflow import serve, open_browser, approval_text, open_workflow

from openai.lib.browser import BrowserError, BrowserCancelledError, BrowserConfirmContext


async def main() -> None:
    with serve() as server:
        questions: list[str] = []

        async def confirm(action: BrowserConfirmContext) -> bool:
            question = await approval_text(workflow.driver, action)
            questions.append(question)
            return "Reserve" not in question

        async with open_workflow(server, "A", confirm=confirm) as workflow:
            read = json.loads(await workflow.observe())
            original = next(e for e in read["elements"] if e["label"] == "Open REQ-401")
            describe = workflow.driver.describe_target
            assert describe is not None
            assert await describe({"tab_id": None, "target": original["ref"]}) == {
                "role": "button",
                "label": "Open REQ-401",
            }
            assert await describe({"tab_id": None, "target": original["ref"]}) == {
                "role": "button",
                "label": "Open REQ-401",
            }
            assert await workflow.stored() == {"bookings": {}, "correspondence": {}}
            opened = await workflow.execute("click", {"tab_id": None, "target": original["ref"]})
            assert opened["ok"], "describing must leave the ref valid"
            assert questions == ['Allow click {"label": "Open REQ-401", "role": "button"}? [y/N] ']
            second = json.loads(await workflow.observe())
            booking = next(e for e in second["elements"] if e["label"] == "Reserve R2 Garden")
            try:
                await workflow.execute("click", {"tab_id": None, "target": booking["ref"]})
                raise AssertionError("Refused booking must stop the workflow")
            except BrowserCancelledError:
                pass
            assert "Reserve R2 Garden" in questions[-1] and booking["ref"] not in questions[-1]
            assert workflow.stopped
            assert await asyncio.wait_for(workflow.stored(allow_stopped=True), 5) == {
                "bookings": {},
                "correspondence": {},
            }

        questions.clear()

        async def renamed_confirm(action: BrowserConfirmContext) -> bool:
            questions.append(await approval_text(renamed.driver, action))
            return True

        async with open_workflow(server, "A", confirm=renamed_confirm) as renamed:
            read = json.loads(await renamed.observe())
            original = next(e for e in read["elements"] if e["label"] == "Open REQ-401")
            describe = renamed.driver.describe_target
            assert describe is not None
            await renamed.page.locator('[data-request="REQ-401"]').evaluate(
                "button => { button.textContent = 'Open a different request'; }"
            )
            try:
                await describe({"tab_id": None, "target": original["ref"]})
                raise AssertionError("Renamed target must be rejected")
            except BrowserError:
                pass
            failed = await renamed.execute("click", {"tab_id": None, "target": original["ref"]})
            assert not failed["ok"]
            assert questions == []
            assert await renamed.stored() == {"bookings": {}, "correspondence": {}}
            refreshed = json.loads(await renamed.observe())
            replacement = next(e for e in refreshed["elements"] if e["label"] == "Open a different request")
            await renamed.observe()
            try:
                await describe({"tab_id": None, "target": replacement["ref"]})
                raise AssertionError("Ref from earlier read must be rejected")
            except BrowserError:
                pass
            assert await renamed.stored() == {"bookings": {}, "correspondence": {}}

        async with open_browser(server[0] + "/inbox?fixture=A") as ordinary:
            assert ordinary.describe_target is None, "ordinary driver cannot describe owned refs"
    print(
        "PASS checked approval labels, refusal before booking, stale/renamed refs, no effect and owned-only description."
    )


if __name__ == "__main__":
    asyncio.run(main())
