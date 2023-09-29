import asyncio
from typing import Iterator

import pytest

pytest.register_assert_rewrite("tests.utils")


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
