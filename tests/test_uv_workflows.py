from __future__ import annotations

import os
import re
import sys
import json
import subprocess
from pathlib import Path

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]


def test_dependency_update_age_policy() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    uv = project["tool"]["uv"]
    assert uv["exclude-newer"] == "8 days"
    for cutoff in uv.get("exclude-newer-package", {}).values():
        # Exceptions must be bounded, reviewable UTC timestamps, never a
        # permanent exemption or a rolling zero-day window.
        assert isinstance(cutoff, str)
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", cutoff)


def test_dependabot_delays_only_ordinary_version_updates() -> None:
    path = ROOT / ".github/dependabot.yml"
    if not path.exists():
        pytest.skip("GitHub configuration is not included in source distributions")
    config = path.read_text()
    entries = re.findall(r"^  - package-ecosystem: ([\w-]+)\n(.*?)(?=^  - |\Z)", config, re.M | re.S)
    assert {name for name, _ in entries} == {"uv", "github-actions", "npm"}
    for _, entry in entries:
        assert re.search(r"^    cooldown:\n      default-days: 8$", entry, re.M)
        assert re.search(r"^    directory: /$", entry, re.M)
        assert "ignore:" not in entry
        assert "target-branch:" not in entry
        assert "open-pull-requests-limit: 0" not in entry


def dependency_lock_source_command() -> str:
    path = ROOT / ".github/workflows/ci.yml"
    if not path.exists():
        pytest.skip("GitHub workflows are not included in source distributions")

    line = next(
        entry
        for entry in path.read_text().splitlines()
        if "python -c '" in entry and "Use only the public PyPI registry" in entry
    )
    command = line.split("python -c '", 1)[1].rsplit("'", 1)[0]
    if sys.version_info < (3, 11):
        command = "import sys, tomli; sys.modules['tomllib'] = tomli; " + command
    return command


def run_dependency_lock_source_check(
    tmp_path: Path, packages: list[dict[str, object]]
) -> subprocess.CompletedProcess[str]:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    (tmp_path / "pyproject.toml").write_text(
        f"[project]\nname = {json.dumps(project['name'])}\nversion = {json.dumps(project['version'])}\n"
    )

    lines: list[str] = []
    for package in packages:
        lines.extend(
            [
                "[[package]]",
                f"name = {json.dumps(package['name'])}",
                f"version = {json.dumps(package['version'])}",
            ]
        )
        source = package.get("source")
        if source is not None:
            assert isinstance(source, dict)
            values = ", ".join(f"{key} = {json.dumps(value)}" for key, value in source.items())
            lines.append("source = { " + values + " }")
        lines.append("")

    (tmp_path / "uv.lock").write_text("\n".join(lines))
    return subprocess.run(
        [sys.executable, "-c", dependency_lock_source_command()],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("source", "accepted"),
    [
        pytest.param({"registry": "https://pypi.org/simple"}, True, id="public-pypi"),
        pytest.param({"git": "https://github.com/unreviewed/package"}, False, id="git"),
        pytest.param({"url": "https://unreviewed.example/package.whl"}, False, id="url"),
        pytest.param({"path": "../unreviewed"}, False, id="path"),
        pytest.param({"directory": "../unreviewed"}, False, id="directory"),
        pytest.param({"editable": "."}, False, id="third-party-editable-root"),
        pytest.param({"registry": "https://private.example/simple"}, False, id="private-registry"),
        pytest.param({}, False, id="empty-source"),
        pytest.param(None, False, id="missing-source"),
        pytest.param({"unknown": "unreviewed"}, False, id="unknown-source"),
        pytest.param(
            {"registry": "https://pypi.org/simple", "git": "https://github.com/unreviewed/package"},
            False,
            id="hybrid-registry-source",
        ),
    ],
)
def test_dependency_lock_accepts_only_public_registry_dependencies(
    tmp_path: Path, source: dict[str, str] | None, accepted: bool
) -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    root: dict[str, object] = {
        "name": project["name"],
        "version": project["version"],
        "source": {"editable": "."},
    }
    dependency: dict[str, object] = {"name": "reviewed-dependency", "version": "1.0.0"}
    if source is not None:
        dependency["source"] = source

    result = run_dependency_lock_source_check(tmp_path, [root, dependency])

    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr
    if not accepted:
        assert "Use only the public PyPI registry" in result.stderr


@pytest.mark.parametrize(
    "variant", ["missing", "duplicate", "wrong-name", "wrong-version", "wrong-path", "hybrid-root"]
)
def test_dependency_lock_requires_one_exact_editable_root(tmp_path: Path, variant: str) -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    root: dict[str, object] = {
        "name": project["name"],
        "version": project["version"],
        "source": {"editable": "."},
    }
    dependency: dict[str, object] = {
        "name": "reviewed-dependency",
        "version": "1.0.0",
        "source": {"registry": "https://pypi.org/simple"},
    }
    if variant == "wrong-name":
        root["name"] = "unreviewed-root"
    elif variant == "wrong-version":
        root["version"] = "0.0.0"
    elif variant == "wrong-path":
        root["source"] = {"editable": "../unreviewed"}
    elif variant == "hybrid-root":
        root["source"] = {"editable": ".", "registry": "https://pypi.org/simple"}

    packages = [dependency] if variant == "missing" else [root, dependency]
    if variant == "duplicate":
        packages.append(dict(root))

    result = run_dependency_lock_source_check(tmp_path, packages)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "Use only the public PyPI registry" in result.stderr


def test_dependency_lock_source_check_accepts_the_committed_lock() -> None:
    result = subprocess.run(
        [sys.executable, "-c", dependency_lock_source_command()],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def dependency_workflow_jobs() -> dict[str, str]:
    path = ROOT / ".github/workflows/ci.yml"
    if not path.exists():
        pytest.skip("GitHub workflows are not included in source distributions")

    workflow = path.read_text().split("\njobs:\n", 1)[1]
    return {
        match.group("name"): match.group("body")
        for match in re.finditer(
            r"^  (?P<name>[\w-]+):\n(?P<body>.*?)(?=^  [\w-]+:\n|\Z)",
            workflow,
            re.MULTILINE | re.DOTALL,
        )
    }


def dependency_installer_jobs(jobs: dict[str, str]) -> set[str]:
    return {
        name
        for name, job in jobs.items()
        if name != "dependency-locks"
        and (
            "astral-sh/setup-uv@" in job
            or "./.github/actions/setup-node-tooling" in job
            or re.search(
                r"\b(?:uv\s+(?:sync|run)|pip\s+install|(?:npm|pnpm)\s+(?:ci|install|add))\b",
                job,
            )
            or re.search(r"run:\s*\./scripts/(?:bootstrap|build)\b", job)
        )
    }


def test_dependency_provenance_runs_before_tool_setup() -> None:
    gate = dependency_workflow_jobs()["dependency-locks"]
    source = next(line for line in gate.splitlines() if "Use only the public PyPI registry" in line)
    assert source.strip().startswith("python -c '")

    before = gate.split(source, 1)[0]
    actions = re.findall(r"^      - uses:\s*(\S+)", before, re.MULTILINE)
    assert len(actions) == 1
    assert re.fullmatch(r"actions/checkout@[0-9a-f]{40}", actions[0])
    assert "persist-credentials: false" in before
    assert not re.search(
        r"^\s*(?:- )?(?:run:|uses:).*(?:setup-uv|setup-node|uv\s|pip\s|npm\s|pnpm\s|scripts/)",
        before,
        re.MULTILINE,
    )


@pytest.mark.parametrize(
    "source",
    [
        pytest.param({"git": "https://github.com/unreviewed/package"}, id="git"),
        pytest.param({"path": "../unreviewed"}, id="path"),
        pytest.param({"url": "https://unreviewed.example/package.whl"}, id="url"),
    ],
)
def test_untrusted_provenance_leaves_no_dependency_install_reachable(tmp_path: Path, source: dict[str, str]) -> None:
    jobs = dependency_workflow_jobs()
    installers = dependency_installer_jobs(jobs)
    assert installers == {"lint", "build", "test", "test-httpx2", "examples", "compatibility"}

    needs = {name: re.findall(r"^    needs:\s*([^\s#]+)", jobs[name], re.MULTILINE) for name in installers}
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    root: dict[str, object] = {
        "name": project["name"],
        "version": project["version"],
        "source": {"editable": "."},
    }
    dependency: dict[str, object] = {
        "name": "reviewed-dependency",
        "version": "1.0.0",
        "source": source,
    }
    rejected = run_dependency_lock_source_check(tmp_path, [root, dependency])
    assert rejected.returncode != 0
    reachable = {
        name
        for name in installers
        if not needs[name] or (needs[name] == ["dependency-locks"] and rejected.returncode == 0)
    }
    assert not reachable

    dependency["source"] = {"registry": "https://pypi.org/simple"}
    accepted = run_dependency_lock_source_check(tmp_path, [root, dependency])
    assert accepted.returncode == 0
    assert {
        name for name in installers if needs[name] == ["dependency-locks"] and accepted.returncode == 0
    } == installers


def test_scheduled_compatibility_keeps_dependency_provenance_gate() -> None:
    jobs = dependency_workflow_jobs()
    assert not re.search(r"^    if:.*schedule", jobs["dependency-locks"], re.MULTILINE)
    assert re.search(r"^    needs:\s*dependency-locks\s*$", jobs["compatibility"], re.MULTILINE)
    assert "github.event_name == 'schedule'" in jobs["compatibility"]
    assert "github.event_name == 'workflow_dispatch'" in jobs["compatibility"]


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
