"""Native input and public pixels for explicitly granted, fixed owned fixtures."""

from __future__ import annotations

import base64
import asyncio
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Callable, Awaitable, cast
from typing_extensions import Literal

from playwright.async_api import Page, JSHandle, FloatRect, ElementHandle

from openai.lib.browser import BrowserError
from openai.lib.computer import Screenshot, ComputerActionInput
from openai.types.responses.response_input_image_content_param import ResponseInputImageContentParam

if TYPE_CHECKING:
    from browser_driver import PlaywrightBrowser

    from openai.lib.browser import TabInput, BrowserState, ClickAtInput, DragPathInput, HoldKeysInput

# Count hidden nodes as well. This grants no pixel authority from a filtered text read.
PUBLIC_VIEW = """() => {
 const walk=document.createTreeWalker(document.documentElement,NodeFilter.SHOW_ELEMENT);
 let count=0,node=walk.currentNode;
 while(node){
   if(++count>2000 || Object.hasOwn(node.dataset,'browserPrivate') ||
     node.matches('input,textarea,select,[contenteditable]:not([contenteditable=false]),iframe,frame,object,embed,video,audio')
     || node.shadowRoot || node.localName.includes('-'))return null;
   node=walk.nextNode();
 }
 const v=visualViewport;
 if(!v || v.scale!==1 || v.offsetLeft!==0 || v.offsetTop!==0)return null;
 return [innerWidth,innerHeight,scrollX,scrollY,devicePixelRatio,v.width,v.height,v.scale];
}"""
CHECK = """(root,{doc,before,at,focus}) => {
 const v=visualViewport,now=[innerWidth,innerHeight,scrollX,scrollY,devicePixelRatio,v?.width,v?.height,v?.scale];
 if(!root.isConnected || root.ownerDocument!==doc || doc!==document ||
     (before && !now.every((n,i)=>n===before[i])))return false;
 if(!at && !focus)return true;
 const hit=focus?document.activeElement:document.elementFromPoint(at.x,at.y);
 if(!hit || !root.contains(hit) || hit.getClientRects().length===0)return false;
 for(let node=hit;node;node=node.parentElement){
   const style=getComputedStyle(node);
   if(style.visibility!=='visible' || Number(style.opacity)===0 || node.matches(':disabled'))return false;
 }
 return !focus || focus==='record' || hit.matches('button[role=menuitem]');
}"""


def refused() -> BrowserError:
    return BrowserError("Owned viewport is stale, private, unsupported or busy.")


def image(png: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


async def read_public_view(page: Page, canvases: list[ElementHandle]) -> list[float] | None:
    # Owned Chromium fixtures require DOM wrappers that page scripts cannot alter.
    session = await page.context.new_cdp_session(page)
    try:
        send = cast("Callable[[str, dict[str, object]], Awaitable[dict[str, Any]]]", session.send)  # pyright: ignore[reportUnknownMemberType] -- Playwright leaves the CDP dictionaries untyped.
        tree = await send("Page.getFrameTree", {})
        world = await send(
            "Page.createIsolatedWorld",
            {"frameId": tree["frameTree"]["frame"]["id"], "worldName": "openai-owned-viewport"},
        )
        result = await send(
            "Runtime.evaluate",
            {"expression": f"({PUBLIC_VIEW})()", "contextId": world["executionContextId"], "returnByValue": True},
        )
        view = result["result"].get("value")
        if result.get("exceptionDetails") or not isinstance(view, list) or len(cast("list[object]", view)) != 8:
            return None
    finally:
        await session.detach()
    current_canvases = page.locator("css=canvas")
    count = await current_canvases.count()
    if count > 2000 or count > len(canvases):
        return None
    for index in range(count):
        current = await current_canvases.nth(index).element_handle()
        try:
            allowed = await current.evaluate(
                """(node, originals) => {
                    for(let index=0;index<originals.length;index+=1){
                        if(node===originals[index])return true;
                    }
                    return false;
                }""",
                canvases,
            )
            if not allowed:
                return None
        finally:
            await current.dispose()
    return cast("list[float]", view)


class OwnedPointer:
    def __init__(self, browser: PlaywrightBrowser) -> None:
        self.browser = browser
        self.busy = False

    def claim(self) -> None:
        if self.busy:
            raise refused()
        self.busy = True

    async def capture(
        self,
        page: Page,
        region: list[int] | None,
        cancelled: Callable[[], bool],
        canvases: list[ElementHandle] | None = None,
    ) -> tuple[bytes, list[float], int]:
        browser = self.browser
        generation = browser._generation
        if cancelled() or browser.page(None)[1] is not page or page.url not in browser.public_viewports:
            raise refused()
        view = await read_public_view(page, canvases or [])
        if not view:
            raise refused()
        box = region if region is not None else [0, 0, int(view[0]), int(view[1])]
        if (
            len(box) != 4
            or any(type(n) is not int or n < 0 or n > 9007199254740991 for n in box)
            or box[0] >= box[2]
            or box[1] >= box[3]
            or box[2] > view[0]
            or box[3] > view[1]
            or (box[2] - box[0]) * (box[3] - box[1]) > 4194304
        ):
            raise refused()
        clip: FloatRect | None = (
            None if region is None else {"x": box[0], "y": box[1], "width": box[2] - box[0], "height": box[3] - box[1]}
        )
        png = await page.screenshot(type="png", full_page=False, scale="css", clip=clip)
        after = await read_public_view(page, canvases or [])
        if (
            cancelled()
            or generation != browser._generation
            or browser.page(None)[1] is not page
            or page.url not in browser.public_viewports
            or view != after
            or len(png) < 24
            or len(png) > 16 * 1024 * 1024
            or png[:8] != b"\x89PNG\r\n\x1a\n"
            or png[12:16] != b"IHDR"
            or int.from_bytes(png[16:20], "big") != box[2] - box[0]
            or int.from_bytes(png[20:24], "big") != box[3] - box[1]
        ):
            raise refused()
        return png, view, generation

    async def browser_capture(
        self, tab_id: str | None, region: list[int] | None, *, cancelled: Callable[[], bool] | None = None
    ) -> ResponseInputImageContentParam:
        self.claim()
        try:

            async def observe() -> ResponseInputImageContentParam:
                png, _, _ = await self.capture(self.browser.page(tab_id)[1], region, cancelled or (lambda: False))
                return {"type": "input_image", "detail": "auto", "image_url": image(png)}

            return await self.browser._observation(observe, cancelled)
        finally:
            self.busy = False

    async def create(
        self,
        record: ElementHandle,
        cancelled: Callable[[], bool],
        *,
        canvases: list[ElementHandle] | None = None,
        browser_mode: bool = False,
    ) -> OwnedComputer:
        browser = self.browser
        allowed = list(canvases or [])
        _, page = browser.page(None)
        if not callable(cancelled) or cancelled() or page.url not in browser.public_viewports:
            raise refused()
        if allowed and not browser_mode:
            raise refused()

        async def prepare() -> OwnedComputer:
            if await record.owner_frame() is not page.main_frame:
                raise refused()
            for canvas in allowed:
                if await canvas.owner_frame() is not page.main_frame or not await canvas.evaluate(
                    "node => node.tagName === 'CANVAS'"
                ):
                    raise refused()
            document = await page.evaluate_handle("document")
            try:
                result = OwnedComputer(self, page, record, document, cancelled, allowed, browser_mode)
                await result.check(None, None)
                browser.page(None)
                return result
            except BaseException:
                await document.dispose()
                raise

        return await browser._observation(prepare, cancelled)

    async def create_browser(
        self, record: ElementHandle, cancelled: Callable[[], bool], canvases: list[ElementHandle] | None = None
    ) -> OwnedBrowser:
        return OwnedBrowser(await self.create(record, cancelled, canvases=canvases, browser_mode=True))


class OwnedComputer:
    def __init__(
        self,
        owner: OwnedPointer,
        page: Page,
        record: ElementHandle,
        document: JSHandle,
        cancelled: Callable[[], bool],
        canvases: list[ElementHandle],
        browser_mode: bool,
    ) -> None:
        self.owner, self.page, self.record, self.document, self.cancelled = owner, page, record, document, cancelled
        self.url = page.url
        self.canvases, self.browser_mode = canvases, browser_mode
        self.permit: tuple[bytes, list[float], int] | None = None

    async def check(
        self,
        view: list[float] | None,
        at: dict[str, object] | None,
        focus: bool | Literal["record"] = False,
        cancelled: Callable[[], bool] | None = None,
    ) -> None:
        browser = self.owner.browser
        if (
            self.cancelled()
            or (cancelled is not None and cancelled())
            or browser.page(None)[1] is not self.page
            or self.page.url != self.url
            or self.url not in browser.public_viewports
        ):
            raise refused()
        current = await read_public_view(self.page, self.canvases)
        if current is None or (view is not None and current != view):
            raise refused()
        ok = await self.record.evaluate(CHECK, {"doc": self.document, "before": view, "at": at, "focus": focus})
        if self.cancelled() or (cancelled is not None and cancelled()) or ok is not True:
            raise refused()

    async def screenshot(self, *, cancelled: Callable[[], bool] | None = None) -> Screenshot:
        self.permit = None
        self.owner.claim()
        try:

            def current_cancelled() -> bool:
                return self.cancelled() or (cancelled is not None and cancelled())

            async def observe() -> Screenshot:
                await self.check(None, None, cancelled=current_cancelled)
                captured = await self.owner.capture(self.page, None, current_cancelled, self.canvases)
                await self.check(captured[1], None, cancelled=current_cancelled)
                if captured[2] != self.owner.browser._generation:
                    raise refused()
                self.permit = captured
                return {"type": "computer_screenshot", "image_url": image(captured[0])}

            return await self.owner.browser._observation(observe, current_cancelled)
        finally:
            self.owner.busy = False

    async def unsupported(self, action: ComputerActionInput) -> None:
        del action
        self.permit = None
        raise refused()

    double_click = unsupported
    scroll = unsupported
    type = unsupported
    wait = unsupported

    async def gesture(self, action: ComputerActionInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        await self._gesture(action.to_dict(), cancelled)

    async def _gesture(self, action: dict[str, object], cancelled: Callable[[], bool] | None = None) -> None:
        saved, self.permit = self.permit, None
        self.owner.claim()
        browser, page = self.owner.browser, self.page
        effect = False
        revoked = False
        mouse: str | None = None
        held: list[str] = []

        def current_cancelled() -> bool:
            return revoked or self.cancelled() or (cancelled is not None and cancelled())

        try:
            if saved is None or saved[2] != browser._generation:
                raise refused()
            raw = deepcopy(action)
            kind = raw.get("type")
            fields = (
                {
                    "click": {"type", "button", "x", "y", "keys"},
                    "move": {"type", "x", "y", "keys"},
                    "drag": {"type", "path", "keys"},
                    "keypress": {"type", "keys"},
                }.get(kind)
                if type(kind) is str
                else None
            )
            if fields is not None and self.browser_mode:
                if kind == "click":
                    fields.add("click_count")
                elif kind == "keypress":
                    fields.add("duration_ms")
            if fields is None or raw.keys() - fields:
                raise refused()
            is_key = kind == "keypress"
            supplied_keys: object = raw.get("keys")
            if supplied_keys is None:
                supplied_keys = []
            if type(supplied_keys) is not list:
                raise refused()
            keys = cast(list[object], supplied_keys)
            if self.browser_mode:
                modifiers = ["Control", "Alt", "Meta", "Shift"]
                allowed_keys = (
                    modifiers
                    + [
                        "Enter",
                        "Escape",
                        "ArrowUp",
                        "ArrowDown",
                        "ArrowLeft",
                        "ArrowRight",
                        "Space",
                        "Home",
                        "End",
                        "PageUp",
                        "PageDown",
                    ]
                    if is_key
                    else modifiers
                )
                if (
                    any(type(key) is not str or key not in allowed_keys for key in keys)
                    or len(set(cast(list[str], keys))) != len(keys)
                    or not ((1 <= len(keys) <= 8) if is_key else len(keys) <= 4)
                ):
                    raise refused()
                if kind == "click" and (type(raw.get("click_count")) is not int or raw["click_count"] not in (1, 2, 3)):
                    raise refused()
                if is_key and (
                    type(raw.get("duration_ms")) is not int or not 1 <= cast(int, raw["duration_ms"]) <= 3000
                ):
                    raise refused()
            elif (is_key and (len(keys) != 1 or type(keys[0]) is not str or keys[0] not in ("Enter", "Escape"))) or (
                not is_key and (len(keys) > 1 or (keys and keys != ["Shift"]))
            ):
                raise refused()
            buttons = ("left", "right", "middle") if self.browser_mode else ("left", "right")
            if kind == "click" and raw.get("button") not in buttons:
                raise refused()
            supplied_path: object = raw.get("path") if kind == "drag" else ([] if is_key else [raw])
            if type(supplied_path) is not list:
                raise refused()
            path = cast(list[object], supplied_path)
            if kind == "drag" and not 2 <= len(path) <= 100:
                raise refused()
            points: list[dict[str, object]] = []
            for at in path:
                if type(at) is not dict:
                    raise refused()
                point = cast(dict[str, object], at)
                if kind == "drag" and point.keys() - {"x", "y"}:
                    raise refused()
                x, y = point.get("x"), point.get("y")
                if type(x) is not int or type(y) is not int or not (0 <= x < saved[1][0] and 0 <= y < saved[1][1]):
                    raise refused()
                points.append({"x": x, "y": y})
            first = points[0] if points else None
            focus: bool | Literal["record"] = ("record" if self.browser_mode else True) if is_key else False
            await browser._observation(lambda: self.check(saved[1], first, focus, current_cancelled), current_cancelled)
            fresh = await browser._observation(
                lambda: self.owner.capture(page, None, current_cancelled, self.canvases), current_cancelled
            )
            if fresh[2] != saved[2] or fresh[0] != saved[0]:
                raise refused()
            await browser._observation(browser.invalidate_references, current_cancelled)
            generation = browser._generation

            async def check(at: dict[str, object] | None, focus_mode: bool | Literal["record"] = focus) -> None:
                if generation != browser._generation:
                    raise refused()
                await self.check(saved[1], at, focus_mode, current_cancelled)
                if generation != browser._generation:
                    raise refused()

            async def perform_input() -> None:
                nonlocal effect, mouse
                click_target: JSHandle | None = None
                try:
                    if self.browser_mode and kind == "click" and raw["click_count"] in (2, 3):
                        click_target = await page.evaluate_handle("({x,y}) => document.elementFromPoint(x,y)", first)
                    for supplied_key in keys:
                        await check(first)
                        key = cast(str, supplied_key)
                        held.append(key)
                        effect = True
                        await page.keyboard.down(key)
                        if is_key:
                            await check(None, False)
                    if self.browser_mode and is_key:
                        deadline = asyncio.get_running_loop().time() + cast(int, raw["duration_ms"]) / 1000
                        while (left := deadline - asyncio.get_running_loop().time()) > 0:
                            if current_cancelled():
                                raise refused()
                            await asyncio.sleep(min(0.025, left))
                    if not is_key:
                        for index, at in enumerate(points):
                            await check(at)
                            effect = True
                            await page.mouse.move(cast(int, at["x"]), cast(int, at["y"]))
                            await check(at)
                            if index == 0 and kind != "move":
                                mouse = cast(str, raw["button"]) if kind == "click" else "left"
                                await page.mouse.down(button=cast("Literal['left', 'right', 'middle']", mouse))
                                await check(at)
                    if mouse:
                        await page.mouse.up(button=cast("Literal['left', 'right', 'middle']", mouse))
                        mouse = None
                    if click_target is not None:
                        for click_count in range(2, cast(int, raw["click_count"]) + 1):
                            await check(first)
                            if not await click_target.evaluate(
                                "(node,at) => node?.isConnected && document.elementFromPoint(at.x,at.y) === node", first
                            ):
                                raise refused()
                            if current_cancelled() or generation != browser._generation:
                                raise refused()
                            mouse = cast(str, raw["button"])
                            await page.mouse.down(
                                button=cast("Literal['left', 'right', 'middle']", mouse), click_count=click_count
                            )
                            await check(first)
                            await page.mouse.up(
                                button=cast("Literal['left', 'right', 'middle']", mouse), click_count=click_count
                            )
                            mouse = None
                    while held:
                        key = held[-1]
                        await page.keyboard.up(key)
                        held.pop()
                    await check(None, False)
                finally:
                    if click_target is not None:
                        try:
                            await click_target.dispose()
                        except Exception:
                            pass

            pending = asyncio.create_task(perform_input())
            try:
                while not pending.done():
                    if current_cancelled():
                        raise refused()
                    await asyncio.wait({pending}, timeout=0.05)
                if current_cancelled():
                    raise refused()
                pending.result()
            except BaseException:
                # The gesture owner releases and retires; a late native reply cannot resume its input.
                revoked = True
                pending.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
                raise
        except BaseException as error:
            if effect:
                # Revoke before cleanup. Repeated cancellation cannot reopen this owned context.
                browser._unusable = True
                browser._revoke()

                async def release() -> None:
                    try:
                        if mouse:
                            await page.mouse.up(button=cast("Literal['left', 'right', 'middle']", mouse))
                    finally:
                        for key in reversed(held):
                            try:
                                await page.keyboard.up(key)
                            except Exception:
                                pass

                task = asyncio.create_task(release())
                task_cancelled = isinstance(error, asyncio.CancelledError)
                until = asyncio.get_running_loop().time() + 5
                while not task.done() and (left := until - asyncio.get_running_loop().time()) > 0:
                    try:
                        await asyncio.wait_for(asyncio.shield(task), left)
                    except asyncio.CancelledError:
                        task_cancelled = True
                        continue
                    except (Exception, asyncio.TimeoutError):
                        break
                if not task.done():
                    task.cancel()
                    task.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
                if browser._retirement is None:
                    browser._retirement = asyncio.create_task(browser.context.close())
                try:
                    await browser._join_retirement(
                        lambda: task_cancelled or self.cancelled() or (cancelled is not None and cancelled())
                    )
                except Exception:
                    pass
                if isinstance(error, asyncio.CancelledError):
                    raise
                if task_cancelled:
                    raise asyncio.CancelledError from None
                raise RuntimeError("Owned native input outcome is unknown; context retired.") from None
            raise
        finally:
            self.owner.busy = False

    click = gesture
    move = gesture
    drag = gesture
    keypress = gesture


class OwnedBrowser:
    """Optional pointer methods for one original public record and its declared canvases."""

    def __init__(self, pointer: OwnedComputer) -> None:
        self.pointer = pointer

    def _current(self, tab_id: str | None) -> None:
        if self.pointer.owner.browser.page(tab_id)[1] is not self.pointer.page:
            self.pointer.permit = None
            raise refused()

    async def state(self) -> BrowserState:
        return await self.pointer.owner.browser.state()

    async def screenshot(
        self, action: TabInput, *, cancelled: Callable[[], bool] | None = None
    ) -> ResponseInputImageContentParam:
        self._current(action["tab_id"])
        result = await self.pointer.screenshot(cancelled=cancelled)
        url = result.get("image_url")
        if not isinstance(url, str):
            raise refused()
        return {"type": "input_image", "detail": "auto", "image_url": url}

    async def click_at(self, action: ClickAtInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        self._current(action["tab_id"])
        raw: dict[str, object] = dict(action)
        raw.pop("tab_id")
        await self.pointer._gesture({"type": "click", **raw}, cancelled)

    async def hover_at(self, action: dict[str, object], *, cancelled: Callable[[], bool] | None = None) -> None:
        self._current(cast("str | None", action["tab_id"]))
        raw = dict(action)
        raw.pop("tab_id")
        await self.pointer._gesture({"type": "move", **raw}, cancelled)

    async def drag_path(self, action: DragPathInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        self._current(action["tab_id"])
        raw: dict[str, object] = dict(action)
        raw.pop("tab_id")
        await self.pointer._gesture({"type": "drag", **raw}, cancelled)

    async def hold_keys(self, action: HoldKeysInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        self._current(action["tab_id"])
        raw: dict[str, object] = dict(action)
        raw.pop("tab_id")
        await self.pointer._gesture({"type": "keypress", **raw}, cancelled)
