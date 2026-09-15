from __future__ import annotations

from importlib.metadata import requires

import pytest
from packaging.requirements import Requirement


@pytest.mark.parametrize(
    ("name", "extra", "affected", "patched"),
    [
        ("aiohttp", "aiohttp", "3.14.2", "3.14.3"),
        ("urllib3", "bedrock", "2.6.3", "2.7.0"),
    ],
)
def test_optional_network_dependency_security_floors(name: str, extra: str, affected: str, patched: str) -> None:
    requirements = [Requirement(value) for value in requires("openai") or []]
    matches = [requirement for requirement in requirements if requirement.name == name]
    assert len(matches) == 1
    requirement = matches[0]
    assert requirement.marker is not None
    assert requirement.marker.evaluate({"extra": extra})
    assert not requirement.marker.evaluate({"extra": ""})
    assert affected not in requirement.specifier
    assert patched in requirement.specifier
