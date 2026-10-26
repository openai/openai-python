"""A partial BrowserDriver for Fieldwork's owned reservation page only."""

from __future__ import annotations

import base64
import secrets
from collections.abc import Callable

from playwright.async_api import Page, Route, ElementHandle, BrowserContext

from openai.lib.browser import (
    TabInput,
    TypeInput,
    ClickInput,
    BrowserError,
    BrowserState,
    BrowserReadV1,
    ReadPageInput,
    SelectOptionInput,
    BrowserReadElement,
)
from openai.types.responses import ResponseInputImageContentParam


class BookingBrowser:
    def __init__(self, context: BrowserContext, url: str) -> None:
        self.context, self.url = context, url
        self.task_page: Page | None = None
        self.refs: dict[str, tuple[str, ElementHandle]] = {}
        self.generation = 0

    async def guard(self, route: Route) -> None:
        if route.request.url == self.url and route.request.method == "GET":
            await route.continue_()
        else:
            await route.abort()

    async def open(self) -> None:
        self.task_page = await self.context.new_page()
        await self.task_page.goto(self.url, wait_until="domcontentloaded", timeout=5000)

    def page(self, tab_id: str | None) -> tuple[str, Page]:
        page = self.task_page
        if tab_id not in (None, "task") or not page or page.is_closed() or page.url != self.url:
            raise BrowserError("The reservation page is no longer available.")
        return "task", page

    async def invalidate_references(self) -> None:
        self.generation += 1
        await self.clear_references()

    async def clear_references(self) -> None:
        held, self.refs = self.refs, {}
        for _, handle in held.values():
            await handle.dispose()

    def check(self, cancelled: Callable[[], bool] | None) -> Page:
        if cancelled and cancelled():
            raise BrowserError("This browser operation was interrupted.")
        return self.page(None)[1]

    async def state(self, *, cancelled: Callable[[], bool] | None = None) -> BrowserState:
        page = self.check(cancelled)
        revision = await page.locator("body").evaluate("body => Number(body.dataset.revision)")
        self.check(cancelled)
        return {
            "tabs": [{"id": "task", "url": self.url, "title": "Book a table", "active": True}],
            "observation": {
                "version": 1,
                "sequence": revision + self.generation,
                "changes": [],
                "dropped_changes": 0,
                "title_truncated": False,
            },
        }

    async def read_page(self, args: ReadPageInput, *, cancelled: Callable[[], bool] | None = None) -> BrowserReadV1:
        page = self.check(cancelled)
        self.page(args["tab_id"])
        await self.clear_references()
        elements: list[BrowserReadElement] = []
        controls = (
            ("Guest name", "textbox"),
            ("Party size", "combobox"),
            ("Time", "combobox"),
            ("Seating", "combobox"),
            ("Reserve table", "button"),
        )
        for label, role in controls:
            locator = (
                page.get_by_role("button", name=label, exact=True)
                if role == "button"
                else page.get_by_label(label, exact=True)
            )
            handle = await locator.element_handle(timeout=5000)
            self.check(cancelled)
            if not handle or not await handle.is_visible() or not await handle.is_enabled():
                if handle:
                    await handle.dispose()
                continue
            ref = secrets.token_hex(12)
            if role == "textbox":
                item: BrowserReadElement = {
                    "ref": ref,
                    "role": "textbox",
                    "label": label,
                    "value": await handle.input_value(),
                }
            elif role == "combobox":
                item = {
                    "ref": ref,
                    "role": "combobox",
                    "label": label,
                    "value": await handle.input_value(),
                    "options": await handle.evaluate(
                        "select => Array.from(select.options, option => ({label: option.label, value: option.value, selected: option.selected}))"
                    ),
                }
            else:
                item = {"ref": ref, "role": "button", "label": label}
            self.refs[ref] = (label, handle)
            elements.append(item)
        self.check(cancelled)
        return {
            "version": 1,
            "text": "Book a table at The Garden Room. " + await page.locator("[role=status]").inner_text(),
            "elements": elements,
            "omitted": [],
        }

    async def get_page_text(self, args: TabInput, *, cancelled: Callable[[], bool] | None = None) -> BrowserReadV1:
        self.page(args["tab_id"])
        page = self.check(cancelled)
        text = await page.locator("[role=status]").inner_text()
        self.check(cancelled)
        return {"version": 1, "text": text, "elements": [], "omitted": []}

    async def screenshot(
        self, args: TabInput, *, cancelled: Callable[[], bool] | None = None
    ) -> ResponseInputImageContentParam:
        self.page(args["tab_id"])
        page = self.check(cancelled)
        pixels = await page.screenshot(type="jpeg", quality=80)
        self.check(cancelled)
        return {"type": "input_image", "image_url": "data:image/jpeg;base64," + base64.b64encode(pixels).decode()}

    def target(
        self, ref: str | None, tab_id: str | None, cancelled: Callable[[], bool] | None
    ) -> tuple[str, ElementHandle]:
        self.check(cancelled)
        self.page(tab_id)
        if ref is None or ref not in self.refs:
            raise BrowserError("Read the reservation again before using this reference.")
        return self.refs[ref]

    async def click(self, args: ClickInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        label, element = self.target(args["target"], args["tab_id"], cancelled)
        if label != "Reserve table":
            raise BrowserError("This reservation control cannot be clicked.")
        await element.click(timeout=5000)
        self.check(cancelled)

    async def type(self, args: TypeInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        label, element = self.target(args["target"], args["tab_id"], cancelled)
        if label != "Guest name":
            raise BrowserError("This reservation control does not accept text.")
        await element.fill(args["text"], timeout=5000)
        self.check(cancelled)

    async def select_option(self, args: SelectOptionInput, *, cancelled: Callable[[], bool] | None = None) -> None:
        label, element = self.target(args["target"], args["tab_id"], cancelled)
        if label not in ("Party size", "Time", "Seating"):
            raise BrowserError("This reservation control is not a selection.")
        await element.select_option(value=args["values"], timeout=5000)
        self.check(cancelled)
