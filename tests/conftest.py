import asyncio
import logging
from typing import Iterator

import pytest

pytest.register_assert_rewrite("tests.utils")

logging.getLogger("openai").setLevel(logging.DEBUG)


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
