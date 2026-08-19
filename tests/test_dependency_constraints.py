from __future__ import annotations

from importlib.metadata import requires

import pytest
from packaging.requirements import Requirement


@pytest.mark.parametrize(
    ("name", "version", "allowed"),
    [
        ("jiter", "0.15.0", False),
        ("jiter", "0.16.0", True),
        ("pydantic", "1.10.12", False),
        ("pydantic", "1.10.13", True),
        ("pydantic", "1.10.26", True),
        ("pydantic", "2.0.3", False),
        ("pydantic", "2.1.1", False),
        ("pydantic", "2.2.1", False),
        ("pydantic", "2.3.0", False),
        ("pydantic", "2.4.0", True),
        ("pydantic", "2.12.5", True),
        ("pydantic", "3.0.0", False),
    ],
)
def test_runtime_dependency_security_floors(name: str, version: str, allowed: bool) -> None:
    requirements = [Requirement(value) for value in requires("openai") or []]
    matches = [requirement for requirement in requirements if requirement.name == name]
    assert len(matches) == 1
    assert matches[0].marker is None
    assert (version in matches[0].specifier) is allowed


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
