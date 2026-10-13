#!/usr/bin/env -S uv run python
"""Run a local fixture, or an explicitly allowed site, with the computer helper."""

from __future__ import annotations

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from contextlib import asynccontextmanager
from urllib.parse import urlsplit
from collections.abc import AsyncGenerator

from playwright_browser import WIDTH, HEIGHT, PlaywrightBrowser, origin
from playwright.async_api import WebSocketRoute, async_playwright

from openai import AsyncOpenAI, AsyncComputerToolset
from openai.lib.computer import ComputerActionInput
from openai.types.responses import ResponseComputerToolCall


@asynccontextmanager
async def open_browser(
    url: str | None, allowed_origins: list[str], *, headless: bool
) -> AsyncGenerator[PlaywrightBrowser]:
    allowed: set[str] = set()
    for value in allowed_origins:
        parsed = urlsplit(value)
        if parsed.path not in ("", "/") or "?" in value or "#" in value:
            raise ValueError("--allow-origin requires an HTTP(S) origin without a path, query, or fragment.")
        allowed.add(origin(value))
    if url is not None and origin(url) not in allowed:
        raise ValueError("--url must also be covered by an explicit --allow-origin.")
    async with async_playwright() as playwright:
        # Playwright uses its own browser with a fresh temporary profile.
        browser = await playwright.chromium.launch(
            headless=headless,
            chromium_sandbox=True,
            timeout=15_000,
            env={
                name: value
                for name in (
                    "PATH",
                    "HOME",
                    "TMPDIR",
                    *(
                        ("DISPLAY", "WAYLAND_DISPLAY", "XAUTHORITY", "XDG_RUNTIME_DIR")
                        if not headless and sys.platform == "linux"
                        else ()
                    ),
                )
                if (value := os.environ.get(name)) is not None
            },
        )
        try:
            context = await browser.new_context(
                viewport={"width": WIDTH, "height": HEIGHT},
                device_scale_factor=1,
                accept_downloads=False,
                service_workers="block",
            )
            page = await context.new_page()
            driver = PlaywrightBrowser(page, allowed)
            await context.route("**/*", driver.guard)

            async def refuse_socket(route: WebSocketRoute) -> None:
                await route.close()

            await context.route_web_socket("**/*", refuse_socket)
            page.set_default_timeout(5_000)
            if url:
                await page.goto(url, wait_until="domcontentloaded")
            else:
                # The only default content is this included page; all network requests are blocked.
                await page.set_content(Path(__file__).with_name("fixture.html").read_text())
            yield driver
        finally:
            await browser.close()


async def ask(question: str) -> bool:
    return (await asyncio.to_thread(input, question + " [y/N] ")).strip().lower() == "y"


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", nargs="?", default="Enter Ada as the name, click Greet, and read the greeting.")
    parser.add_argument(
        "--model", required=True, help="A model available to your account that supports the computer tool"
    )
    parser.add_argument("--url", help="Page to open instead of the included fixture")
    parser.add_argument(
        "--allow-origin", action="append", default=[], help="Permit this exact HTTP(S) origin (repeatable)"
    )
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    async def approve_checks(call: ResponseComputerToolCall) -> bool:
        # ensure_ascii keeps text from the page or model from controlling the terminal.
        checks = json.dumps([check.to_dict() for check in call.pending_safety_checks], ensure_ascii=True)
        return await ask(f"Approve these safety checks? {checks}")

    async def before_action(action: ComputerActionInput) -> bool:
        if action.type in {"screenshot", "wait"}:
            return True
        return await ask(f"Run this action? {json.dumps(action.to_dict(), ensure_ascii=True)}")

    async with open_browser(args.url, args.allow_origin, headless=args.headless) as driver, AsyncOpenAI() as client:
        result = await AsyncComputerToolset(driver).run(
            client,
            {"model": args.model, "input": args.task, "store": False},
            max_steps=20,
            approve_safety_checks=approve_checks,
            before_action=before_action,
        )
        print(result.output_text)


if __name__ == "__main__":
    asyncio.run(main())
