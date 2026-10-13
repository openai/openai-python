import asyncio
from collections.abc import Callable

import httpx2 as httpx
from server import serve
from exercise import JSONMap, binding


async def main() -> None:
    async with serve(0) as app, httpx.AsyncClient(base_url=app.origin, timeout=20) as client:
        client.headers["X-Demo-Token"] = app.token

        async def state() -> JSONMap:
            return (await client.get("/api/state")).json()["run"]

        async def wait_for(predicate: Callable[[JSONMap], object]) -> JSONMap:
            for _ in range(400):
                run = await state()
                if predicate(run):
                    return run
                assert run["owner"] != "stopped", run
                await asyncio.sleep(0.05)
            raise AssertionError("Run did not settle")

        response = await client.post("/api/start", json={"taskId": "invoices", "api": "decisions", "mode": "rehearsal"})
        assert response.status_code == 200, response.text
        ready = await wait_for(lambda run: run["approval"] and run["view"]["status"] == "live")
        response = await client.post("/api/take-control", json=binding(ready))
        assert response.status_code == 200, response.text
        human = await wait_for(lambda run: run["owner"] == "human" and run["view"]["status"] == "live")
        captured = await client.post(
            "/api/inspect",
            json={**binding(human), "name": "browser_screenshot", "args": {"tab_id": None}, "consent": True},
        )
        assert captured.status_code == 200, captured.text
        assert any(item["type"] == "input_image" for item in captured.json()["output"]["output"])
        response = await client.post("/api/input", json={**binding(human), "action": "open_notes"})
        assert response.status_code == 200, response.text
        await wait_for(lambda run: run["browser"]["role"] == "Notes" and run["view"]["status"] == "live")

        page = await app.browser.new_page()
        await page.goto(app.launch_url)
        keys = await page.locator("#human-key option:not(#desktop-save)").all_text_contents()
        assert "ControlOrMeta+A" in keys and "PageDown" in keys, keys
        checks = [
            *[({"action": "key", "key": key}, 200) for key in keys],
            ({"action": "key", "key": "ControlOrMeta+L"}, 400),
            ({"action": "key", "key": "ControlOrMeta+S"}, 400),
            ({"action": "type", "text": ""}, 400),
            ({"action": "type", "text": "x" * 2000}, 200),
            ({"action": "type", "text": "x" * 2001}, 400),
            ({"action": "type", "text": "line one\nline two"}, 200),
            ({"action": "type", "text": "\U0001f642" * 1000}, 200),
            ({"action": "type", "text": "\U0001f642" * 1000 + "a"}, 400),
            ({"action": "scroll", "direction": "down", "amount": 1}, 200),
            ({"action": "scroll", "direction": "up", "amount": 2048}, 200),
            ({"action": "scroll", "direction": "right", "amount": 2049}, 400),
            ({"action": "scroll", "direction": "left", "amount": 0}, 400),
            ({"action": "scroll", "direction": "down", "amount": 1.5}, 400),
        ]
        for action, expected in checks:
            current = await wait_for(lambda run: not run["humanInputBusy"] and run["view"]["status"] == "live")
            response = await client.post("/api/input", json={**binding(current), **action})
            assert response.status_code == expected, (action, response.status_code, response.text)
        assert (await state())["requests"] == 0
        for _ in range(257):
            current = await wait_for(lambda run: not run["humanInputBusy"] and run["view"]["status"] == "live")
            response = await client.post("/api/input", json={**binding(current), "action": "key", "key": "ArrowLeft"})
            assert response.status_code == 200, response.text
        bounded = await wait_for(lambda run: not run["humanInputBusy"])
        assert len(bounded["events"]) == 256
        assert bounded["eventsDropped"] > 0
        assert bounded["events"][0]["kind"] == "human"
        await page.wait_for_function(
            "document.querySelector('#timeline-dropped').textContent.includes('earlier events omitted')"
        )
        await page.close()
        print(f"PASS {len(checks)} browser control cases from shared UI and accepted/rejected boundaries")


if __name__ == "__main__":
    asyncio.run(main())
