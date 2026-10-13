"""Map three supplied image sizes to current browser CSS coordinates on a local canvas."""

from __future__ import annotations

import json
import math
import asyncio
import argparse
from typing import Any
from pathlib import Path

from driver_inspector import inspect_call, open_inspector

from openai.lib.browser import AsyncBrowserToolset
from openai.types.responses import ResponseFunctionToolCall


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []
    async with open_inspector() as (base, page, origin):
        await base.navigate({"tab_id": None, "url": origin + "/canvas"})
        record = await page.locator("#workspace").element_handle()
        canvas = await page.locator("#board").element_handle()
        assert record is not None and canvas is not None
        stopped = False
        pointer = await base.owned_browser(record, cancelled=lambda: stopped, canvases=[canvas])
        approved = True

        async def confirm(_context: Any) -> bool:
            return approved

        helper = AsyncBrowserToolset(pointer, members=["screenshot", "hover_at", "click_at"], confirm=confirm)
        viewport = await page.evaluate("() => ({width:innerWidth,height:innerHeight})")
        for scale_x, scale_y in ((1, 1), (2, 2), (0.5, 0.75)):
            image = await helper.execute(
                ResponseFunctionToolCall(
                    id="image",
                    call_id="image",
                    status="completed",
                    type="function_call",
                    name="browser_screenshot",
                    arguments=json.dumps({"tab_id": None}),
                )
            )
            output = image["output"]
            assert not isinstance(output, str)
            parts = list(output)
            text = next(part["text"] for part in parts if part["type"] == "input_text")
            image_url = next(part.get("image_url") for part in parts if part["type"] == "input_image")
            assert isinstance(image_url, str)
            assert json.loads(text)["ok"]
            sent = {"width": round(viewport["width"] * scale_x), "height": round(viewport["height"] * scale_y)}
            picked = {
                "x": round(570 * sent["width"] / viewport["width"]),
                "y": round(315 * sent["height"] / viewport["height"]),
            }
            css = {
                "x": math.floor(picked["x"] * viewport["width"] / sent["width"]),
                "y": math.floor(picked["y"] * viewport["height"] / sent["height"]),
            }
            moved = await inspect_call(helper, "hover_at", {"tab_id": None, **css}, cancelled=lambda: stopped)
            assert moved["ok"]
            assert await page.evaluate("() => ({open:coordinateProof.opened,held:coordinateProof.held})") == {
                "open": True,
                "held": 0,
            }
            assert (await inspect_call(helper, "screenshot", {"tab_id": None}))["ok"]
            clicked = await inspect_call(
                helper, "click_at", {"tab_id": None, **css, "button": "left", "click_count": 1, "keys": []}
            )
            assert clicked["ok"]
            rows.append(
                {
                    "viewport": viewport,
                    "sent": sent,
                    "picked": picked,
                    "css": css,
                    "image": image_url,
                }
            )
        assert await page.evaluate("() => coordinateProof.clicks") == 3
        assert (await inspect_call(helper, "screenshot", {"tab_id": None}))["ok"]
        approved = False
        assert not (await inspect_call(helper, "hover_at", {"tab_id": None, "x": 10, "y": 10}))["ok"]
        assert await page.evaluate("() => coordinateProof.opened")
        approved = True
        stopped = True
        try:
            await inspect_call(helper, "hover_at", {"tab_id": None, "x": 10, "y": 10}, cancelled=lambda: stopped)
        except Exception:
            pass
        else:
            raise AssertionError("Stop must prevent the hover")
        assert await page.evaluate("() => coordinateProof.held") == 0
        stopped = False
        # The owned test double distrusts geometry without changing any page globals.
        view = await page.evaluate(
            "() => [innerWidth,innerHeight,scrollX,scrollY,devicePixelRatio,"
            "visualViewport.width,visualViewport.height,visualViewport.scale]"
        )
        evaluate, screenshot = page.evaluate, page.screenshot
        captures = 0

        async def reported_view(*_args: Any, **_kwargs: Any) -> Any:
            return view

        async def capture(*args: Any, **kwargs: Any) -> bytes:
            nonlocal captures
            captures += 1
            return await screenshot(*args, **kwargs)

        page.evaluate, page.screenshot = reported_view, capture
        try:
            await record.evaluate(
                """node => {
                    const input=document.createElement('input');
                    input.id='private-probe';node.appendChild(input);
                }"""
            )
            assert not (await inspect_call(helper, "screenshot", {"tab_id": None}))["ok"]
            assert captures == 0
            await page.locator("#private-probe").evaluate("node => node.remove()")
            assert (await inspect_call(helper, "screenshot", {"tab_id": None}))["ok"]
            assert captures == 1
            await canvas.evaluate("node => node.replaceWith(node.cloneNode(true))")
            assert not (await inspect_call(helper, "screenshot", {"tab_id": None}))["ok"]
            assert captures == 1
            await record.evaluate("(node,original) => node.querySelector('#board').replaceWith(original)", canvas)
            await record.evaluate(
                """node => {
                    const host=document.createElement('div');host.id='shape-probe';
                    host.attachShadow({mode:'open'}).textContent='Fixture text outside the admitted light DOM';
                    node.append(host);
                }"""
            )
            assert not (await inspect_call(helper, "screenshot", {"tab_id": None}))["ok"]
            assert captures == 1, "Never request pixels from an unsupported shadow document"
            await page.locator("#shape-probe").evaluate("node => node.remove()")
            await record.evaluate(
                """node => {
                    const host=document.createElement('fixture-extra');host.id='shape-probe';node.append(host);
                }"""
            )
            assert not (await inspect_call(helper, "screenshot", {"tab_id": None}))["ok"]
            assert captures == 1, "Never request pixels containing an unadmitted custom element"
            await page.locator("#shape-probe").evaluate("node => node.remove()")

            async def missing_view(*_args: Any, **_kwargs: Any) -> None:
                return None

            page.evaluate = missing_view
            assert (await inspect_call(helper, "screenshot", {"tab_id": None}))["ok"]
            assert captures == 2, "A clean fixture gets geometry from the trusted scan"
        finally:
            page.evaluate, page.screenshot = evaluate, screenshot
        assert (await inspect_call(helper, "screenshot", {"tab_id": None}))["ok"]
        await page.locator("#workspace").evaluate("(node) => node.replaceWith(node.cloneNode(true))")
        assert not (await inspect_call(helper, "hover_at", {"tab_id": None, "x": 570, "y": 315}))["ok"]
    if args.report:
        sections: list[str] = []
        for index, row in enumerate(rows):
            original, sent, picked, css, image = (row[key] for key in ("viewport", "sent", "picked", "css", "image"))
            sections.append(f"""
<section><h2>Case {index + 1}</h2><p>Original {original["width"]} × {original["height"]} CSS pixels.
Supplied {sent["width"]} × {sent["height"]}. Pick ({picked["x"]}, {picked["y"]}) → CSS ({css["x"]}, {css["y"]}).</p>
<div class="pair"><figure><figcaption>Original</figcaption><div class="frame"><img width="{original["width"]}" height="{original["height"]}" src="{image}"><span class="mark" style="left:{css["x"]}px;top:{css["y"]}px" aria-label="Mapped CSS point"></span></div></figure>
<figure><figcaption>Supplied size</figcaption><div class="frame"><img width="{sent["width"]}" height="{sent["height"]}" src="{image}"><span class="mark" style="left:{picked["x"]}px;top:{picked["y"]}px" aria-label="Picked image point"></span></div></figure></div></section>""")
        with args.report.open("x", encoding="utf-8") as file:
            args.report.chmod(0o600)
            file.write(
                """<!doctype html><meta charset="utf-8"><title>Coordinate mapping</title>
<style>body{font:18px system-ui;margin:2rem;background:#f6f4ec;color:#172a1f}.pair{display:flex;gap:2rem;overflow:auto}
figure{margin:0}img{display:block;object-fit:fill}figcaption{margin:1rem 0}.frame{position:relative;outline:1px solid #999}.mark{position:absolute;width:22px;height:22px;box-sizing:border-box;border:3px solid #fff;border-radius:50%;background:#e74726;outline:2px solid #172a1f;transform:translate(-50%,-50%)}</style>
<h1>From image coordinates to browser coordinates</h1>
<p>Move and click used the mapped CSS point in the real local fixture. Each original came from a new checked screenshot.
The second image shows the supplied dimensions for that case. Scroll sideways to compare at their actual sizes.</p>"""
                + "".join(sections)
            )
    print(
        json.dumps(
            {
                "checks": [{key: value for key, value in row.items() if key != "image"} for row in rows],
                "clicks": 3,
                "refused": True,
                "stopHeld": 0,
                "replaced": True,
                "trustedViewportAdmission": True,
            }
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
