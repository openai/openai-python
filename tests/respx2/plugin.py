from typing import cast

import pytest

from tests import respx2 as respx

from .router import MockRouter


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "respx2(assert_all_called=False, assert_all_mocked=False, base_url=...): "
        "configure the respx2_mock fixture. "
        "See https://lundberg.github.io/respx/api.html#configuration",
    )


@pytest.fixture
def respx2_mock(request):
    respx_marker = request.node.get_closest_marker("respx2")

    mock_router: MockRouter = (
        respx.mock
        if respx_marker is None
        else cast(MockRouter, respx.mock(**respx_marker.kwargs))
    )

    with mock_router:
        yield mock_router
