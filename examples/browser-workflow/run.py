"""Run a resource booking through the SDK, or explore the local apps without a key."""

import signal
import asyncio
import argparse
from types import FrameType
from pathlib import Path

from workflow import main

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--mode", choices=("run", "serve"), default="run")
parser.add_argument("--api", choices=("responses", "decisions"), default="responses")
parser.add_argument("--fixture", default="A")
parser.add_argument("--data", type=Path)
parser.add_argument("--receipt", type=Path)
parser.add_argument("--headed", action="store_true")


async def cli() -> None:
    # Python 3.10's asyncio.run otherwise cancels Playwright's connection along
    # with this task, before it can read the saved records and close the browser.
    loop = asyncio.get_running_loop()
    task = asyncio.current_task()
    assert task is not None

    def stop(_number: int, _frame: FrameType | None) -> None:
        loop.call_soon_threadsafe(task.cancel)

    previous = signal.signal(signal.SIGINT, stop)
    try:
        await main(parser.parse_args())
    finally:
        signal.signal(signal.SIGINT, previous)


if __name__ == "__main__":
    asyncio.run(cli())
