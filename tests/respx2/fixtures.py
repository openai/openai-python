try:
    import pytest
except ImportError:  # pragma: nocover
    pass
else:
    import asyncio

    @pytest.fixture(scope="session")
    def session_event_loop():
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()
