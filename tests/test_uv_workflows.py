from __future__ import annotations

import os
import re
import sys
import json
import subprocess
from typing import cast
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from packaging.requirements import Requirement

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]


def is_public_pypi_artifact(url: str) -> bool:
    try:
        parsed = urlsplit(url)
    except ValueError:
        return False
    return (
        parsed.scheme == "https"
        and parsed.netloc == "files.pythonhosted.org"
        and parsed.path.startswith("/packages/")
        and not parsed.query
        and not parsed.fragment
    )


@pytest.mark.parametrize(
    "url",
    [
        "http://files.pythonhosted.org/packages/example.whl",
        "https://files.pythonhosted.org.example.com/packages/example.whl",
        "https://user:password@files.pythonhosted.org/packages/example.whl",
        "https://files.pythonhosted.org:443/packages/example.whl",
        "https://files.pythonhosted.org/other/example.whl",
        "https://files.pythonhosted.org/packages/example.whl?token=fake",
        "https://files.pythonhosted.org/packages/example.whl#fragment",
    ],
)
def test_public_artifact_check_rejects_unexpected_locations(url: str) -> None:
    assert not is_public_pypi_artifact(url)


def assert_public_registry_references(value: object) -> None:
    if isinstance(value, dict):
        mapping = cast("dict[str, object]", value)
        if "registry" in mapping:
            public_registry = mapping["registry"] == "https://pypi.org/simple"
            assert public_registry, "Unexpected registry reference in the public lockfile"
        for child in mapping.values():
            assert_public_registry_references(child)
    elif isinstance(value, list):
        for child in cast("list[object]", value):
            assert_public_registry_references(child)


def test_lockfile_uses_public_package_sources() -> None:
    lock = tomllib.loads((ROOT / "uv.lock").read_text())
    assert_public_registry_references(lock)
    for package in lock["package"]:
        name = package["name"]
        expected_source = {"editable": "."} if name == "openai" else {"registry": "https://pypi.org/simple"}
        public_source = package["source"] == expected_source
        # Do not print an unexpected URL: a local registry URL may contain credentials.
        assert public_source, f"{name}: unexpected package source in the public lockfile"
        if name == "openai":
            continue
        artifacts = [*package.get("wheels", [])]
        if "sdist" in package:
            artifacts.append(package["sdist"])
        assert artifacts, f"{name}: no hashed distribution artifacts"
        for artifact in artifacts:
            public_artifact = is_public_pypi_artifact(artifact["url"])
            valid_hash = re.fullmatch(r"sha256:[0-9a-f]{64}", artifact["hash"]) is not None
            assert public_artifact, f"{name}: unexpected artifact host in the public lockfile"
            assert valid_hash, f"{name}: missing SHA-256 artifact hash"


def test_dependency_update_age_policy() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    uv = project["tool"]["uv"]
    assert uv["exclude-newer"] == "8 days"
    for cutoff in uv.get("exclude-newer-package", {}).values():
        # Exceptions must be bounded, reviewable UTC timestamps, never a
        # permanent exemption or a rolling zero-day window.
        assert isinstance(cutoff, str)
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", cutoff)


@pytest.mark.parametrize(
    ("name", "affected", "patched"),
    [
        ("azure-core", "1.36.0", "1.38.0"),
        ("cryptography", "46.0.3", "50.0.0"),
        ("msal", "1.36.0", "1.37.0"),
        ("pygments", "2.19.2", "2.20.0"),
        ("pyjwt", "2.10.1", "2.13.0"),
        ("requests", "2.32.5", "2.33.0"),
        ("pytest", "8.4.2", "9.0.3"),
        ("pytest-asyncio", "1.2.0", "1.4.0"),
    ],
)
def test_development_dependency_security_floors(name: str, affected: str, patched: str) -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    values = project["dependency-groups"]["dev"] + project["tool"]["uv"]["constraint-dependencies"]
    requirements = [Requirement(value) for value in values]
    matches = [requirement for requirement in requirements if requirement.name == name]
    assert len(matches) == 1
    assert affected not in matches[0].specifier
    assert patched in matches[0].specifier
    assert name not in {Requirement(value).name for value in project["project"]["dependencies"]}


def test_dependabot_delays_only_ordinary_version_updates() -> None:
    path = ROOT / ".github/dependabot.yml"
    if not path.exists():
        pytest.skip("GitHub configuration is not included in source distributions")
    config = path.read_text()
    entries = re.findall(r"^  - package-ecosystem: ([\w-]+)\n(.*?)(?=^  - |\Z)", config, re.M | re.S)
    assert {name for name, _ in entries} == {"uv", "github-actions"}
    for _, entry in entries:
        assert re.search(r"^    cooldown:\n      default-days: 8$", entry, re.M)
        assert re.search(r"^    directory: /$", entry, re.M)
        assert "ignore:" not in entry
        assert "target-branch:" not in entry
        assert "open-pull-requests-limit: 0" not in entry


def test_agents_integration_selects_its_typechecking_runtime() -> None:
    path = ROOT / ".github/workflows/detect-breaking-changes.yml"
    if not path.exists():
        pytest.skip("GitHub workflows are not included in source distributions")
    integration = path.read_text().split("\n  agents_sdk:\n", 1)[1]
    setup = integration.split("      - name: Set up uv\n", 1)[1].split("\n      - name:", 1)[0]
    assert "working-directory: openai-python" in setup
    assert "python-version: '3.14'" in setup


@pytest.mark.parametrize("name", ["create-releases.yml", "publish-pypi.yml"])
def test_release_build_remains_separate_from_oidc_publish(name: str) -> None:
    path = ROOT / ".github/workflows" / name
    if not path.exists():
        pytest.skip("GitHub workflows are not included in source distributions")
    workflow = path.read_text()
    build = workflow.split("\n  build:\n", 1)[1].split("\n  publish:\n", 1)[0]
    publish = workflow.split("\n  publish:\n", 1)[1]
    assert "contents: read" in build
    assert "id-token:" not in build
    assert "./scripts/build" in build
    assert "enable-cache: false" in build
    assert "needs: build" in publish
    assert "environment: publish" in publish
    assert "id-token: write" in publish
    assert "pypa/gh-action-pypi-publish@" in publish
    assert "run:" not in publish
    assert "actions/checkout@" not in publish
    for ref in re.findall(r"uses: (\S+)", workflow):
        assert re.fullmatch(r"[^@]+@[0-9a-f]{40}", ref), ref


def fake_uv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    log = tmp_path / "calls.jsonl"
    executable = tmp_path / "uv"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json, os, pathlib, sys\n"
        "with open(os.environ['UV_TEST_LOG'], 'a') as f:\n"
        "    f.write(json.dumps({'args': sys.argv[1:], 'environment': os.environ.get('UV_PROJECT_ENVIRONMENT')}) + '\\n')\n"
        "if sys.argv[1] == 'export':\n"
        "    pathlib.Path(sys.argv[sys.argv.index('--output-file') + 1]).write_text('reviewed-build-requirements\\n')\n"
        "if sys.argv[1] == 'build':\n"
        "    assert pathlib.Path(sys.argv[sys.argv.index('--build-constraints') + 1]).read_text() == 'reviewed-build-requirements\\n'\n"
        "sys.exit(7 if os.environ.get('UV_TEST_FAIL') == sys.argv[1] else 0)\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("UV_TEST_LOG", str(log))
    return log


@pytest.mark.parametrize("fail", [False, True])
def test_pydantic_v1_uses_separate_locked_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fail: bool
) -> None:
    log = fake_uv(tmp_path, monkeypatch)
    environment = str(tmp_path / "compatibility")
    monkeypatch.setenv("OPENAI_PYDANTIC_V1_ENV", environment)
    if fail:
        monkeypatch.setenv("UV_TEST_FAIL", "sync")
    result = subprocess.run([str(ROOT / "scripts/test-pydantic-v1"), "-q", "tests/test_files.py"], check=False)
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    assert result.returncode == (7 if fail else 0)
    assert calls[0] == {
        "args": ["sync", "--locked", "--all-extras", "--no-default-groups", "--group", "dev", "--group", "pydantic-v1"],
        "environment": environment,
    }
    if fail:
        assert len(calls) == 1
    else:
        assert calls[1] == {
            "args": [
                "run",
                "--no-sync",
                "python",
                "-m",
                "pytest",
                "--ignore=tests/functional",
                "-q",
                "tests/test_files.py",
            ],
            "environment": environment,
        }


@pytest.mark.parametrize("fail", [False, True])
def test_build_uses_hashed_locked_build_group(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fail: bool) -> None:
    log = fake_uv(tmp_path, monkeypatch)
    if fail:
        monkeypatch.setenv("UV_TEST_FAIL", "export")
    result = subprocess.run([str(ROOT / "scripts/build"), "--out-dir", str(tmp_path / "dist")], check=False)
    calls = [json.loads(line)["args"] for line in log.read_text().splitlines()]
    assert result.returncode == (7 if fail else 0)
    assert calls[0][:-1] == [
        "export",
        "--locked",
        "--only-group",
        "build",
        "--no-emit-project",
        "--format",
        "requirements.txt",
        "--output-file",
    ]
    constraints = calls[0][-1]
    assert not Path(constraints).exists()
    if fail:
        assert len(calls) == 1
    else:
        assert calls[1] == [
            "build",
            "--no-sources",
            "--build-constraints",
            constraints,
            "--require-hashes",
            "--out-dir",
            str(tmp_path / "dist"),
        ]
