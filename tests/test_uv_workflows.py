from __future__ import annotations

import os
import re
import sys
import json
import subprocess
from typing import Any, cast
from pathlib import Path

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]


def test_lockfile_uses_public_package_sources() -> None:
    lock = tomllib.loads((ROOT / "uv.lock").read_text())
    for package in lock["package"]:
        name = package["name"]
        expected_source = {"editable": "."} if name == "openai" else {"registry": "https://pypi.org/simple"}
        public_source = package["source"] == expected_source
        # Do not print an unexpected URL: a local registry URL may contain credentials.
        assert public_source, f"{name}: unexpected package source in the public lockfile"

    pending: list[Any] = [lock]
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            mapping = cast("dict[str, Any]", value)
            if "registry" in mapping:
                public_registry = mapping["registry"] == "https://pypi.org/simple"
                assert public_registry, "Unexpected registry reference in the public lockfile"
            if "url" in mapping and "hash" in mapping:
                public_artifact = (
                    re.fullmatch(r"https://files\.pythonhosted\.org/packages/[^?#\s]+", mapping["url"]) is not None
                )
                assert public_artifact, "Unexpected artifact URL in the public lockfile"
            pending.extend(mapping.values())
        elif isinstance(value, list):
            pending.extend(cast("list[Any]", value))


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
    tmp_path: Path,
    packages: list[dict[str, object]],
    *,
    build_requires: list[str] | None = None,
    build_group: list[str] | None = None,
    build_constraints: list[str] | None = None,
    backend: str = "hatchling.build",
    backend_path: list[str] | None = None,
    uv_sources: dict[str, dict[str, str]] | None = None,
    uv_index_url: str | None = None,
) -> subprocess.CompletedProcess[str]:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    requires = ["hatchling==1.27.0"] if build_requires is None else build_requires
    group = ["hatchling==1.27.0"] if build_group is None else build_group
    constraints = ["hatchling==1.27.0"] if build_constraints is None else build_constraints
    configuration = (
        f"[project]\nname = {json.dumps(project['name'])}\nversion = {json.dumps(project['version'])}\n"
        + f"[build-system]\nrequires = {json.dumps(requires)}\nbuild-backend = {json.dumps(backend)}\n"
    )
    if backend_path is not None:
        configuration += "backend-path = " + json.dumps(backend_path) + "\n"
    configuration += (
        "[dependency-groups]\nbuild = "
        + json.dumps(group)
        + "\n[tool.uv]\nbuild-constraint-dependencies = "
        + json.dumps(constraints)
        + "\n"
    )
    if uv_index_url is not None:
        configuration += "index-url = " + json.dumps(uv_index_url) + "\n"
    if uv_sources is not None:
        configuration += "[tool.uv.sources]\n"
        for name, source in uv_sources.items():
            values = ", ".join(key + " = " + json.dumps(value) for key, value in source.items())
            configuration += name + " = { " + values + " }\n"
    (tmp_path / "pyproject.toml").write_text(configuration)

    lines: list[str] = []
    reviewed: dict[str, object] = {
        "name": "hatchling",
        "version": "1.27.0",
        "source": {"registry": "https://pypi.org/simple"},
    }
    fixtures = packages if any(package.get("name") == "hatchling" for package in packages) else [*packages, reviewed]
    for package in fixtures:
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
            source_values = cast(dict[str, object], source)
            values = ", ".join(f"{key} = {json.dumps(value)}" for key, value in source_values.items())
            lines.append("source = { " + values + " }")
        artifact = package.get("sdist")
        if "sdist" not in package and source == {"registry": "https://pypi.org/simple"}:
            artifact = {
                "url": "https://files.pythonhosted.org/packages/reviewed-1.0.0.tar.gz",
                "hash": "sha256:" + "a" * 64,
            }
        if artifact is not None:
            assert isinstance(artifact, dict)
            artifact_values = cast(dict[str, object], artifact)
            values = ", ".join(f"{key} = {json.dumps(value)}" for key, value in artifact_values.items())
            lines.append("sdist = { " + values + " }")
        if "wheels" in package:
            wheels = package["wheels"]
            assert isinstance(wheels, list)
            typed_wheels = cast(list[dict[str, object]], wheels)
            wheel_values = [
                "{ " + ", ".join(f"{key} = {json.dumps(value)}" for key, value in wheel.items()) + " }"
                for wheel in typed_wheels
            ]
            lines.append("wheels = [" + ", ".join(wheel_values) + "]")
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


@pytest.mark.parametrize("kind", ["sdist", "wheel"])
@pytest.mark.parametrize(
    ("url", "digest", "accepted"),
    [
        pytest.param("https://files.pythonhosted.org/packages/reviewed.whl", "a" * 64, True, id="public-pypi"),
        pytest.param("https://unreviewed.example/packages/reviewed.whl", "a" * 64, False, id="foreign-host"),
        pytest.param("http://files.pythonhosted.org/packages/reviewed.whl", "a" * 64, False, id="insecure-http"),
        pytest.param(
            "https://user:pass@files.pythonhosted.org/packages/reviewed.whl",
            "a" * 64,
            False,
            id="credentials",
        ),
        pytest.param("https://files.pythonhosted.org:443/packages/reviewed.whl", "a" * 64, False, id="port"),
        pytest.param("https://files.pythonhosted.org/packages/reviewed.whl?redirect=1", "a" * 64, False, id="query"),
        pytest.param("https://files.pythonhosted.org/packages/reviewed.whl#redirect", "a" * 64, False, id="fragment"),
        pytest.param("https://files.pythonhosted.org/redirect/reviewed.whl", "a" * 64, False, id="path"),
        pytest.param(
            "https://files.pythonhosted.org.attacker.test/packages/reviewed.whl", "a" * 64, False, id="suffix"
        ),
        pytest.param("https://files.pythonhosted.org/packages/reviewed.whl", "invalid", False, id="hash"),
    ],
)
def test_dependency_lock_rejects_untrusted_distribution_artifacts(
    tmp_path: Path, kind: str, url: str, digest: str, accepted: bool
) -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    root: dict[str, object] = {
        "name": project["name"],
        "version": project["version"],
        "source": {"editable": "."},
    }
    artifact = {"url": url, "hash": "sha256:" + digest}
    dependency: dict[str, object] = {
        "name": "reviewed-dependency",
        "version": "1.0.0",
        "source": {"registry": "https://pypi.org/simple"},
    }
    if kind == "sdist":
        dependency["sdist"] = artifact
    else:
        dependency["sdist"] = None
        dependency["wheels"] = [artifact]

    result = run_dependency_lock_source_check(tmp_path, [root, dependency])

    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize("artifact", [None, {}, {"url": "https://files.pythonhosted.org/packages/reviewed.whl"}])
def test_dependency_lock_rejects_missing_distribution_artifacts(
    tmp_path: Path, artifact: dict[str, str] | None
) -> None:
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
        "sdist": artifact,
    }
    result = run_dependency_lock_source_check(tmp_path, [root, dependency])
    assert result.returncode != 0, result.stdout + result.stderr


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


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("reviewed-pinned-backend", True, id="reviewed-pinned-backend"),
        pytest.param("safe-python-marker", True, id="reviewed-pinned-python-marker"),
        pytest.param("empty-sources", True, id="benign-empty-source-overrides"),
        pytest.param("direct-url", False, id="root-build-direct-url"),
        pytest.param("git", False, id="root-build-git-source"),
        pytest.param("path", False, id="root-build-local-path"),
        pytest.param("private-index", False, id="root-build-private-index"),
        pytest.param("unpinned", False, id="root-build-unpinned-requirement"),
        pytest.param("missing-pin", False, id="root-build-missing-reviewed-pin"),
        pytest.param("unlocked-version", False, id="root-build-version-missing-from-lock"),
        pytest.param("constraint-url", False, id="build-constraint-direct-url"),
        pytest.param("group-mismatch", False, id="reviewed-build-group-mismatch"),
        pytest.param("unlocked-group", False, id="reviewed-build-group-unlocked-dependency"),
        pytest.param("backend", False, id="unreviewed-build-backend"),
        pytest.param("backend-path", False, id="local-build-backend-path"),
        pytest.param("source-git", False, id="pinned-hatchling-git-override"),
        pytest.param("source-path", False, id="pinned-hatchling-path-override"),
        pytest.param("index-override", False, id="pinned-hatchling-private-index-override"),
        pytest.param("marker-code", False, id="untrusted-build-marker-expression"),
    ],
)
def test_root_build_requirements_must_be_public_locked_and_reviewed(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    root: dict[str, object] = {
        "name": project["name"],
        "version": project["version"],
        "source": {"editable": "."},
    }
    requires = ["hatchling==1.27.0"]
    group = ["hatchling==1.27.0"]
    constraints = ["hatchling==1.27.0"]
    backend = "hatchling.build"
    backend_path: list[str] | None = None
    sources: dict[str, dict[str, str]] | None = None
    index: str | None = None
    if variant == "safe-python-marker":
        requires = group = constraints = ["hatchling==1.27.0; python_version < '3.11'"]
    elif variant == "empty-sources":
        sources = {}
    elif variant == "direct-url":
        requires = ["hatchling @ https://unreviewed.example/hatchling.whl"]
    elif variant == "git":
        requires = ["hatchling @ git+https://github.com/unreviewed/hatchling"]
    elif variant == "path":
        requires = ["hatchling @ file:///tmp/unreviewed"]
    elif variant == "private-index":
        requires = ["hatchling==1.27.0 --index-url https://private.example/simple"]
    elif variant == "unpinned":
        requires = ["hatchling>=1.27.0"]
    elif variant == "missing-pin":
        requires = []
    elif variant == "unlocked-version":
        requires = group = constraints = ["hatchling==9.9.9"]
    elif variant == "constraint-url":
        group = constraints = ["hatchling @ https://unreviewed.example/hatchling.whl"]
    elif variant == "group-mismatch":
        group = ["hatchling==1.26.0"]
    elif variant == "unlocked-group":
        group = constraints = ["hatchling==1.27.0", "packaging==26.3"]
    elif variant == "backend":
        backend = "unreviewed.build"
    elif variant == "backend-path":
        backend_path = ["."]
    elif variant == "source-git":
        sources = {"hatchling": {"git": "https://github.com/unreviewed/hatchling"}}
    elif variant == "source-path":
        sources = {"hatchling": {"path": "../unreviewed"}}
    elif variant == "index-override":
        index = "https://private.example/simple"
    elif variant == "marker-code":
        requires = group = constraints = ['hatchling==1.27.0; __import__("os")']
    result = run_dependency_lock_source_check(
        tmp_path,
        [root],
        build_requires=requires,
        build_group=group,
        build_constraints=constraints,
        backend=backend,
        backend_path=backend_path,
        uv_sources=sources,
        uv_index_url=index,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


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


@pytest.mark.parametrize("name", ["detect_breaking_changes", "agents_sdk"])
def test_breaking_change_installers_validate_provenance_first(name: str) -> None:
    path = ROOT / ".github/workflows/detect-breaking-changes.yml"
    if not path.exists():
        pytest.skip("GitHub workflows are not included in source distributions")

    match = re.search(
        rf"^  {name}:\n(?P<body>.*?)(?=^  [\w-]+:\n|\Z)",
        path.read_text(),
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None
    job = match.group("body")
    steps = re.findall(r"^      - (?:name|uses):\s*(.+)$", job, re.MULTILINE)
    assert re.fullmatch(r"actions/checkout@[0-9a-f]{40}.*", steps[0])
    assert steps[1] == "Verify dependency source provenance before installing tools"
    source = next(line for line in job.splitlines() if "Use only the public PyPI registry" in line)
    command = source.split("python -c '", 1)[1].rsplit("'", 1)[0]
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()
    expected = next(line for line in workflow.splitlines() if "Use only the public PyPI registry" in line)
    assert command == expected.split("python -c '", 1)[1].rsplit("'", 1)[0]
    if name == "agents_sdk":
        gate = job.split("      - name: Verify dependency source provenance before installing tools\n", 1)[1]
        gate = gate.split("\n      - name:", 1)[0]
        assert "working-directory: openai-python" in gate


def security_dependency_floor_program() -> str:
    gate = dependency_workflow_jobs()["dependency-locks"]
    match = re.search(
        r"      - name: Require published minimums for direct security updates\n(?P<body>.*?)(?=\n      - name:|\Z)",
        gate,
        re.DOTALL,
    )
    assert match is not None, "Direct Dependabot security updates must validate published dependency floors"
    body = match.group("body")
    assert "github.actor" not in body, "Maintainer updates must not disable an authored Dependabot security guard"
    for condition in (
        "github.event_name == 'pull_request'",
        "github.event.pull_request.user.login == 'dependabot[bot]'",
        "contains(github.event.pull_request.head.ref, 'python-security')",
    ):
        assert condition in body
    script = re.search(r"          python - <<'PY'\n(?P<source>.*?)(?=\n          PY)", body, re.DOTALL)
    assert script is not None
    program = "\n".join(line[10:] for line in script.group("source").splitlines())
    if sys.version_info < (3, 11):
        program = "import sys, tomli; sys.modules['tomllib'] = tomli\n" + program
    return program


@pytest.mark.parametrize(
    ("actor", "author", "reference", "event", "accepted"),
    [
        pytest.param(
            "maintainer",
            "dependabot[bot]",
            "dependabot/uv/python-security-123",
            "pull_request",
            True,
            id="maintainer-updated-security-pr",
        ),
        pytest.param(
            "dependabot[bot]",
            "dependabot[bot]",
            "dependabot/uv/python-security-123",
            "pull_request",
            True,
            id="dependabot-updated-security-pr",
        ),
        pytest.param(
            "dependabot[bot]",
            "untrusted-maintainer",
            "dependabot/uv/python-security-123",
            "pull_request",
            False,
            id="spoofed-security-pr-author",
        ),
        pytest.param(
            "maintainer",
            "dependabot[bot]",
            "dependabot/uv/python-maintenance-123",
            "pull_request",
            False,
            id="routine-dependency-pr",
        ),
        pytest.param(
            "dependabot[bot]",
            "dependabot[bot]",
            "dependabot/uv/python-security-123",
            "push",
            False,
            id="non-pull-request-event",
        ),
    ],
)
def test_security_floor_guard_uses_immutable_pr_identity(
    actor: str, author: str, reference: str, event: str, accepted: bool
) -> None:
    gate = dependency_workflow_jobs()["dependency-locks"]
    step = gate.split("      - name: Require published minimums for direct security updates\n", 1)[1]
    condition = step.split("        if: >-\n", 1)[1].split("        env:\n", 1)[0]
    values = {
        "github.event_name == 'pull_request'": event == "pull_request",
        "github.actor == 'dependabot[bot]'": actor == "dependabot[bot]",
        "github.event.pull_request.user.login == 'dependabot[bot]'": author == "dependabot[bot]",
        "contains(github.event.pull_request.head.ref, 'python-security')": "python-security" in reference,
    }
    clauses = [line.strip().removeprefix("&& ").strip() for line in condition.splitlines() if line.strip()]
    assert all(clause in values for clause in clauses), clauses
    assert all(values[clause] for clause in clauses) is accepted


def run_security_dependency_floor_check(
    tmp_path: Path,
    *,
    base_requirements: list[str],
    head_requirements: list[str],
    base_packages: list[tuple[str, str]],
    head_packages: list[tuple[str, str]],
    optional: bool = False,
    base_optional_groups: dict[str, list[str]] | None = None,
    head_optional_groups: dict[str, list[str]] | None = None,
    sha: str = "a" * 40,
    base_constraints: list[str] | None = None,
    head_constraints: list[str] | None = None,
    base_build_constraints: list[str] | None = None,
    head_build_constraints: list[str] | None = None,
    base_dependency_groups: dict[str, list[str]] | None = None,
    head_dependency_groups: dict[str, list[str]] | None = None,
    origin: str = "https://github.com/openai/openai-python",
) -> subprocess.CompletedProcess[str]:
    def project(
        requirements: list[str],
        groups: dict[str, list[str]] | None,
        constraints: list[str] | None,
        build_constraints: list[str] | None,
        dependency_groups: dict[str, list[str]] | None,
    ) -> str:
        if optional:
            groups = {"feature": requirements}
            requirements = []
        result = '[project]\nname = "openai"\nversion = "1.0"\ndependencies = ' + json.dumps(requirements) + "\n"
        if groups:
            result += "[project.optional-dependencies]\n"
            for group, dependencies in groups.items():
                result += group + " = " + json.dumps(dependencies) + "\n"
        if dependency_groups:
            result += "[dependency-groups]\n"
            for group, dependencies in dependency_groups.items():
                result += group + " = " + json.dumps(dependencies) + "\n"
        if constraints is not None or build_constraints is not None:
            result += "[tool.uv]\n"
            if constraints is not None:
                result += "constraint-dependencies = " + json.dumps(constraints) + "\n"
            if build_constraints is not None:
                result += "build-constraint-dependencies = " + json.dumps(build_constraints) + "\n"
        return result

    def lock(packages: list[tuple[str, str]]) -> str:
        return "\n".join(
            f"[[package]]\nname = {json.dumps(name)}\nversion = {json.dumps(version)}\n" for name, version in packages
        )

    (tmp_path / "pyproject.toml").write_text(
        project(
            head_requirements, head_optional_groups, head_constraints, head_build_constraints, head_dependency_groups
        )
    )
    (tmp_path / "uv.lock").write_text(lock(head_packages))
    (tmp_path / "base-project.toml").write_text(
        project(
            base_requirements, base_optional_groups, base_constraints, base_build_constraints, base_dependency_groups
        )
    )
    (tmp_path / "base-lock.toml").write_text(lock(base_packages))
    fake_git = tmp_path / "git"
    fake_git.write_text(
        f"#!{sys.executable}\n"
        "import pathlib, sys\n"
        f"root = pathlib.Path({str(tmp_path)!r})\n"
        f"origin = {origin!r}\n"
        f"sha = {sha!r}\n"
        "arguments = sys.argv[1:]\n"
        "if arguments == ['remote', 'get-url', 'origin']:\n"
        "    print(origin)\n"
        "elif arguments == ['fetch', '--no-tags', '--depth=1', 'origin', sha]:\n"
        "    pass\n"
        "elif arguments == ['show', sha + ':pyproject.toml']:\n"
        "    print((root / 'base-project.toml').read_text(), end='')\n"
        "elif arguments == ['show', sha + ':uv.lock']:\n"
        "    print((root / 'base-lock.toml').read_text(), end='')\n"
        "else:\n"
        "    raise SystemExit('Unexpected or unsafe git operation')\n"
    )
    fake_git.chmod(0o755)
    environment = dict(os.environ, BASE_SHA=sha, PATH=str(tmp_path) + os.pathsep + os.environ["PATH"])
    return subprocess.run(
        [sys.executable, "-c", security_dependency_floor_program()],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("base", "head", "before", "after", "optional", "accepted"),
    [
        pytest.param(
            ["Danger_Pkg>=1.0"],
            ["danger-pkg>=1.0"],
            [("danger-pkg", "1.0")],
            [("danger_pkg", "1.1")],
            False,
            False,
            id="direct-lock-only",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.1"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.1")],
            False,
            True,
            id="direct-floor-raised",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.1"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.5")],
            False,
            False,
            id="direct-floor-below-patched-lock",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.5"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.5")],
            False,
            True,
            id="direct-floor-equals-patched-lock",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.6"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.5")],
            False,
            True,
            id="direct-floor-above-patched-lock",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.5"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.5.0")],
            False,
            True,
            id="patched-lock-trailing-zero-equivalence",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.5"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.5rc1")],
            False,
            False,
            id="patched-lock-prerelease-fails-closed",
        ),
        pytest.param(
            ["danger-pkg>=0!9.0"],
            ["danger-pkg>=1!1.0"],
            [("danger-pkg", "9.0")],
            [("danger-pkg", "1!2.0")],
            False,
            False,
            id="epoch-floor-below-patched-lock",
        ),
        pytest.param(
            ["danger-pkg>=2.0"],
            ["danger-pkg>=1.0"],
            [("danger-pkg", "2.0")],
            [("danger-pkg", "2.1")],
            False,
            False,
            id="direct-floor-lowered",
        ),
        pytest.param(
            ["danger-pkg>=1.10"],
            ["danger-pkg>=1.9"],
            [("danger-pkg", "1.10")],
            [("danger-pkg", "1.11")],
            False,
            False,
            id="numeric-release-floor-lowered",
        ),
        pytest.param(
            ["danger-pkg>=1.9"],
            ["danger-pkg>=1.10"],
            [("danger-pkg", "1.9")],
            [("danger-pkg", "1.10")],
            False,
            True,
            id="numeric-release-floor-raised",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.0.0"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.1")],
            False,
            False,
            id="trailing-zero-equivalent-floor",
        ),
        pytest.param(
            ["danger-pkg>=0!9.0"],
            ["danger-pkg>=1!1.0"],
            [("danger-pkg", "9.0")],
            [("danger-pkg", "1!1.0")],
            False,
            True,
            id="epoch-floor-raised",
        ),
        pytest.param(
            ["danger-pkg>=1!1.0"],
            ["danger-pkg>=0!9.0"],
            [("danger-pkg", "1!1.0")],
            [("danger-pkg", "1!1.1")],
            False,
            False,
            id="epoch-floor-lowered",
        ),
        pytest.param(
            ["danger-pkg>=1.0; python_version >= '3.11'"],
            ["danger-pkg>=1.1; python_version >= '3.11'"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.1")],
            False,
            True,
            id="python-version-marker-floor-raised",
        ),
        pytest.param(
            ["Danger_Pkg[extra]>=1.0,<3; python_version >= '3.11'"],
            ["danger-pkg[extra]>=1.1,<3; python_version >= '3.11'"],
            [("danger-pkg", "1.0")],
            [("danger_pkg", "1.1")],
            True,
            True,
            id="optional-alias-extra-and-marker-floor-raised",
        ),
        pytest.param(
            ["websockets >= 12"],
            ["websockets >= 13"],
            [("websockets", "12")],
            [("websockets", "13")],
            True,
            True,
            id="repository-whitespace-websockets",
        ),
        pytest.param(
            ["numpy >= 1"],
            ["numpy >= 2.1"],
            [("numpy", "1")],
            [("numpy", "2.1")],
            True,
            True,
            id="repository-whitespace-numpy",
        ),
        pytest.param(
            ["pandas >= 1.2.3"],
            ["pandas >= 1.5.0"],
            [("pandas", "1.2.3")],
            [("pandas", "1.5.0")],
            True,
            True,
            id="repository-whitespace-pandas",
        ),
        pytest.param(
            ["pydantic>=1.10.13,<3"],
            ["pydantic>=1.10.26,<3"],
            [("pydantic", "1.10.13"), ("pydantic", "2.12.5")],
            [("pydantic", "1.10.26"), ("pydantic", "2.12.5")],
            False,
            True,
            id="unchanged-alternate-pydantic-line-preserved",
        ),
        pytest.param(
            ["pydantic>=1.10.13,<3"],
            ["pydantic>=1.10.26,<3"],
            [("pydantic", "1.10.13"), ("pydantic", "2.12.4")],
            [("pydantic", "1.10.26"), ("pydantic", "2.12.5")],
            False,
            False,
            id="multiple-patched-pydantic-lines-fail-closed",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.0,<3"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.1")],
            False,
            False,
            id="unchanged-lower-bound",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.0"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.1")],
            True,
            False,
            id="optional-lock-only",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.1"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.1")],
            True,
            True,
            id="optional-floor-raised",
        ),
        pytest.param(
            ["numpy>=1", "numpy>=2.0.2"],
            ["numpy>=2.1", "numpy>=2.1,<3"],
            [("numpy", "2.0.2")],
            [("numpy", "2.1.0")],
            True,
            True,
            id="optional-multiple-floors-reach-patched-release",
        ),
        pytest.param(
            ["numpy>=1", "numpy>=2.0.2"],
            ["numpy>=1.1", "numpy>=2.0.2"],
            [("numpy", "2.0.2")],
            [("numpy", "2.1.0")],
            True,
            False,
            id="optional-multiple-floors-below-patched-release",
        ),
        pytest.param(
            ["numpy>=1", "numpy>=2.0.2"],
            ["numpy>=2.1", "numpy>=2.1,<3"],
            [("numpy", "1.26"), ("numpy", "2.0.2")],
            [("numpy", "1.26"), ("numpy", "2.1.0")],
            True,
            True,
            id="unchanged-alternate-numpy-lock-preserved",
        ),
        pytest.param(
            ["numpy>=1", "numpy>=2.0.2"],
            ["numpy>=1.1", "numpy>=2.0.1"],
            [("numpy", "2.0.2")],
            [("numpy", "2.1.0")],
            True,
            False,
            id="optional-multiple-floors-one-lowered",
        ),
        pytest.param(
            ["numpy>=1", "numpy>=2.0.2"],
            ["numpy>=1", "numpy>=2.0.3"],
            [("numpy", "2.0.2")],
            [("numpy", "2.1.0")],
            True,
            False,
            id="optional-multiple-floors-weakest-unchanged",
        ),
        pytest.param(
            ["numpy>=1", "numpy>=2.0.2"],
            ["numpy>=1.1"],
            [("numpy", "2.0.2")],
            [("numpy", "2.1.0")],
            True,
            False,
            id="optional-floor-branch-removed",
        ),
        pytest.param(
            ["other>=2"],
            ["other>=1"],
            [("other", "2")],
            [("other", "2")],
            False,
            False,
            id="unchanged-lock-direct-floor-lowered",
        ),
        pytest.param(
            ["other>=2"],
            ["other"],
            [("other", "2")],
            [("other", "2")],
            False,
            False,
            id="unchanged-lock-direct-floor-removed",
        ),
        pytest.param(
            ["other>=2,<4"],
            ["other>=2,<5"],
            [("other", "2")],
            [("other", "2")],
            False,
            True,
            id="unchanged-lock-equal-floor-preserved",
        ),
        pytest.param(
            ["other>=1"],
            ["other>=2"],
            [("other", "2")],
            [("other", "2")],
            False,
            True,
            id="unchanged-lock-direct-floor-raised",
        ),
        pytest.param(
            ["other>=2"],
            ["other>=2"],
            [("other", "2")],
            [("other", "2")],
            False,
            True,
            id="unchanged-lock-identical-requirement-preserved",
        ),
        pytest.param(
            ["other >= 1.10"],
            ["other >= 1.9"],
            [("other", "1.10")],
            [("other", "1.10")],
            False,
            False,
            id="unchanged-lock-whitespace-numeric-floor-lowered",
        ),
        pytest.param(
            ["other>=1!1"],
            ["other>=0!9"],
            [("other", "1!1")],
            [("other", "1!1")],
            False,
            False,
            id="unchanged-lock-epoch-floor-lowered",
        ),
        pytest.param(
            ["other>=2.0"],
            ["other>=2.0.0,<4"],
            [("other", "2")],
            [("other", "2")],
            False,
            True,
            id="unchanged-lock-trailing-zero-equivalent-floor",
        ),
        pytest.param(
            ["numpy>=1", "numpy>=2.0.2"],
            ["numpy>=1", "numpy>=2.0.1"],
            [("numpy", "2.1")],
            [("numpy", "2.1")],
            True,
            False,
            id="unchanged-lock-optional-floor-lowered",
        ),
        pytest.param(
            ["numpy>=1", "numpy>=2.0.2"],
            ["numpy>=1"],
            [("numpy", "2.1")],
            [("numpy", "2.1")],
            True,
            False,
            id="unchanged-lock-optional-floor-branch-removed",
        ),
        pytest.param(
            ["numpy>=2"],
            ["numpy>=2", "numpy"],
            [("numpy", "2.1")],
            [("numpy", "2.1")],
            True,
            False,
            id="unchanged-lock-unbounded-optional-branch-added",
        ),
        pytest.param(
            ["numpy>=1", "numpy>=2.0.2"],
            ["numpy>=1.1", "numpy>=2.0.2"],
            [("numpy", "2.1")],
            [("numpy", "2.1")],
            True,
            True,
            id="unchanged-lock-optional-floor-branches-preserved",
        ),
        pytest.param(
            ["other>=2; python_version >= '3.11'"],
            ["other>=1; python_version >= '3.11'"],
            [("other", "2")],
            [("other", "2")],
            False,
            False,
            id="unchanged-lock-marker-floor-lowered",
        ),
        pytest.param(
            ["other>=2"],
            ["other>=2rc1"],
            [("other", "2")],
            [("other", "2")],
            False,
            False,
            id="unchanged-lock-unsupported-floor-fails-closed",
        ),
        pytest.param(
            ["other"],
            ["other>=2"],
            [("other", "2")],
            [("other", "2")],
            False,
            True,
            id="unchanged-lock-previously-unbounded-floor-added",
        ),
        pytest.param(
            ["other>=2; python_version < '3.11'", "other>=1; python_version >= '3.11'"],
            ["other>=1; python_version < '3.11'", "other>=2; python_version >= '3.11'"],
            [("other", "2")],
            [("other", "2")],
            False,
            False,
            id="unchanged-lock-marker-context-floors-swapped",
        ),
        pytest.param(
            ["other[secure]>=2", "other[compat]>=1"],
            ["other[secure]>=1", "other[compat]>=2"],
            [("other", "2")],
            [("other", "2")],
            False,
            False,
            id="unchanged-lock-requested-extra-context-floors-swapped",
        ),
        pytest.param(
            ["other>=2; python_version >= '3.11' and sys_platform == 'Linux'"],
            ["other>=2,<4; sys_platform == 'Linux' and python_version >= '3.11'"],
            [("other", "2")],
            [("other", "2")],
            False,
            True,
            id="unchanged-lock-marker-conjunction-reordered",
        ),
        pytest.param(
            ["other[B,A]>=2"],
            ["other[a,b]>=2,<4"],
            [("other", "2")],
            [("other", "2")],
            False,
            True,
            id="unchanged-lock-requested-extras-reordered",
        ),
        pytest.param(
            ["other>=2; sys_platform == 'Linux'"],
            ["other>=2; sys_platform == 'linux'"],
            [("other", "2")],
            [("other", "2")],
            False,
            False,
            id="unchanged-lock-marker-literal-case-preserved",
        ),
        pytest.param(
            ["other>=2; python_version < '3.11' or sys_platform == 'linux'"],
            ["other>=2; python_version < '3.11' or sys_platform == 'linux'"],
            [("other", "2")],
            [("other", "2")],
            False,
            False,
            id="unchanged-lock-ambiguous-or-marker-fails-closed",
        ),
        pytest.param(
            ["other>=2; (python_version < '3.11')"],
            ["other>=2; (python_version < '3.11')"],
            [("other", "2")],
            [("other", "2")],
            False,
            False,
            id="unchanged-lock-parenthesized-marker-fails-closed",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.5"],
            [("danger-pkg", "2.0")],
            [("danger-pkg", "1.5")],
            False,
            False,
            id="downgraded-lock-cannot-be-security-patch",
        ),
        pytest.param(
            ["danger-pkg>=0!1"],
            ["danger-pkg>=0!9"],
            [("danger-pkg", "1!1")],
            [("danger-pkg", "0!9")],
            False,
            False,
            id="downgraded-epoch-lock-cannot-be-security-patch",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=2.4"],
            [("danger-pkg", "1.5"), ("danger-pkg", "2.5")],
            [("danger-pkg", "1.6"), ("danger-pkg", "2.4")],
            False,
            False,
            id="downgraded-alternate-lock-branch-fails-closed",
        ),
        pytest.param(
            ["danger-pkg>=1"],
            ["danger-pkg>=3"],
            [("danger-pkg", "2")],
            [("danger-pkg", "2"), ("danger-pkg", "3")],
            False,
            False,
            id="unpaired-added-lock-release-fails-closed",
        ),
        pytest.param(
            ["danger-pkg>=1"],
            ["danger-pkg>=2"],
            [("danger-pkg", "1"), ("danger-pkg", "2")],
            [("danger-pkg", "2")],
            False,
            False,
            id="unpaired-removed-lock-release-fails-closed",
        ),
        pytest.param(
            ["danger-pkg>=1"],
            ["danger-pkg>=2.0.0"],
            [("danger-pkg", "2.0")],
            [("danger-pkg", "2.0.0")],
            False,
            False,
            id="equivalent-lock-release-is-not-security-upgrade",
        ),
        pytest.param(
            ["danger-pkg>=1.9"],
            ["danger-pkg>=2.0"],
            [("danger-pkg", "1.9")],
            [("danger-pkg", "2.0")],
            False,
            True,
            id="single-lock-major-upgrade-remains-valid",
        ),
        pytest.param(
            ["pydantic>=1.10.13,<3"],
            ["pydantic>=1.10.27,<3"],
            [("pydantic", "1.10.26"), ("pydantic", "2.12.5")],
            [("pydantic", "1.10.27"), ("pydantic", "2.12.5")],
            False,
            True,
            id="independent-pydantic-v1-lock-upgrade-preserves-v2",
        ),
        pytest.param(
            ["danger-pkg>=1"],
            ["danger-pkg>=3"],
            [("danger-pkg", "1.5rc1")],
            [("danger-pkg", "3")],
            False,
            False,
            id="prerelease-removed-lock-fails-closed",
        ),
        pytest.param(
            ["safe-direct>=1.0"],
            ["safe-direct>=1.0"],
            [("safe-direct", "1.0"), ("transitive", "1.0")],
            [("safe-direct", "1.0"), ("transitive", "1.1")],
            False,
            True,
            id="transitive-only",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.0"],
            [("danger-pkg", "1.0"), ("danger-pkg", "2.0")],
            [("danger-pkg", "1.0"), ("danger-pkg", "2.1")],
            False,
            False,
            id="multiple-locked-versions",
        ),
        pytest.param(
            ["danger-pkg"],
            ["danger-pkg>=1.1"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.1")],
            False,
            True,
            id="previously-unbounded",
        ),
        *[
            pytest.param(
                ["danger-pkg>=1.0"],
                ["danger-pkg>=" + version],
                [("danger-pkg", "1.0")],
                [("danger-pkg", "1.1")],
                False,
                False,
                id="unsupported-floor-" + label,
            )
            for label, version in (
                ("prerelease", "1.1rc1"),
                ("postrelease", "1.1.post1"),
                ("development", "1.1.dev1"),
                ("local", "1.1+local"),
            )
        ],
        pytest.param(
            ["danger-pkg>=1.0rc1"],
            ["danger-pkg>=1.1"],
            [("danger-pkg", "1.0rc1")],
            [("danger-pkg", "1.1")],
            False,
            False,
            id="unsupported-previous-floor",
        ),
    ],
)
def test_only_direct_security_updates_must_raise_published_minimums(
    tmp_path: Path,
    base: list[str],
    head: list[str],
    before: list[tuple[str, str]],
    after: list[tuple[str, str]],
    optional: bool,
    accepted: bool,
) -> None:
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base,
        head_requirements=head,
        base_packages=before,
        head_packages=after,
        optional=optional,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("base_groups", "head_groups", "accepted"),
    [
        pytest.param(
            {"datalib": ["numpy>=1"], "voice_helpers": ["numpy>=2"]},
            {"datalib": ["numpy>=2"], "voice_helpers": ["numpy>=1"]},
            False,
            id="actual-numpy-extra-floors-swapped",
        ),
        pytest.param(
            {"datalib": ["numpy>=1"], "voice_helpers": ["numpy>=2"]},
            {"datalib": ["numpy>=1"]},
            False,
            id="actual-numpy-bounded-extra-removed",
        ),
        pytest.param(
            {"datalib": ["numpy>=1"], "voice_helpers": ["numpy>=2"]},
            {"voice_helpers": ["numpy>=2"], "datalib": ["numpy>=1"]},
            True,
            id="actual-numpy-extra-groups-reordered",
        ),
        pytest.param(
            {"voice_helpers": ["numpy>=2"]},
            {"voice-helpers": ["numpy>=2,<4"]},
            True,
            id="canonical-optional-group-spelling-preserved",
        ),
        pytest.param(
            {"voice_helpers": ["numpy>=2"]},
            {"datalib": ["numpy>=2"]},
            False,
            id="bounded-optional-context-replaced",
        ),
        pytest.param(
            {"datalib": ["numpy>=1"], "voice_helpers": ["numpy>=2"]},
            {"datalib": ["numpy>=1.1"], "voice_helpers": ["numpy>=2"]},
            True,
            id="actual-numpy-extra-floor-raised-in-place",
        ),
        pytest.param(
            {"datalib": ["numpy>=1"], "voice_helpers": ["numpy>=2"]},
            {"datalib": ["numpy>=1"], "voice_helpers": ["numpy>=1.9"]},
            False,
            id="actual-numpy-extra-floor-lowered-in-place",
        ),
    ],
)
def test_security_floors_preserve_original_optional_contexts(
    tmp_path: Path,
    base_groups: dict[str, list[str]],
    head_groups: dict[str, list[str]],
    accepted: bool,
) -> None:
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[],
        head_requirements=[],
        base_packages=[("numpy", "2")],
        head_packages=[("numpy", "2")],
        base_optional_groups=base_groups,
        head_optional_groups=head_groups,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("constraint-equal", True, id="uv-security-constraint-preserved"),
        pytest.param("constraint-higher", True, id="uv-security-constraint-raised"),
        pytest.param("constraint-reordered", True, id="uv-security-constraints-reordered"),
        pytest.param("constraint-lowered", False, id="uv-security-constraint-lowered"),
        pytest.param("constraint-removed", False, id="uv-security-constraint-removed"),
        pytest.param("constraint-section-removed", False, id="uv-security-constraint-section-removed"),
        pytest.param("constraint-marker-swap", False, id="uv-security-constraint-markers-swapped"),
        pytest.param("build-pin-preserved", True, id="uv-build-security-pin-preserved"),
        pytest.param("build-pin-lowered", False, id="uv-build-security-pin-lowered"),
        pytest.param("build-pin-removed", False, id="uv-build-security-pin-removed"),
        pytest.param("group-floor-raised", True, id="dependency-group-security-floor-raised"),
        pytest.param("group-floor-lowered", False, id="dependency-group-security-floor-lowered"),
        pytest.param("group-floor-removed", False, id="dependency-group-security-floor-removed"),
        pytest.param("group-pin-lowered", False, id="dependency-group-exact-security-pin-lowered"),
        pytest.param("group-context-swap", False, id="pydantic-dependency-group-contexts-swapped"),
        pytest.param("unbounded-group-preserved", True, id="unbounded-dependency-group-preserved"),
    ],
)
def test_security_updates_preserve_uv_and_dependency_group_floors(tmp_path: Path, variant: str, accepted: bool) -> None:
    base_constraints: list[str] | None = None
    head_constraints: list[str] | None = None
    base_build_constraints: list[str] | None = None
    head_build_constraints: list[str] | None = None
    base_groups: dict[str, list[str]] | None = None
    head_groups: dict[str, list[str]] | None = None
    if variant == "constraint-equal":
        base_constraints = head_constraints = ["cryptography>=50.0.0"]
    elif variant == "constraint-higher":
        base_constraints, head_constraints = ["cryptography>=50.0.0"], ["cryptography>=51.0.0"]
    elif variant == "constraint-reordered":
        base_constraints = ["cryptography>=50.0.0", "requests>=2.33.0"]
        head_constraints = ["requests>=2.33.0", "cryptography>=50.0.0"]
    elif variant == "constraint-lowered":
        base_constraints, head_constraints = ["cryptography>=50.0.0"], ["cryptography>=49.0.0"]
    elif variant == "constraint-removed":
        base_constraints = ["cryptography>=50.0.0", "requests>=2.33.0"]
        head_constraints = ["requests>=2.33.0"]
    elif variant == "constraint-section-removed":
        base_constraints = ["cryptography>=50.0.0"]
    elif variant == "constraint-marker-swap":
        base_constraints = [
            "cryptography>=50; python_version < '3.11'",
            "cryptography>=49; python_version >= '3.11'",
        ]
        head_constraints = [
            "cryptography>=49; python_version < '3.11'",
            "cryptography>=50; python_version >= '3.11'",
        ]
    elif variant == "build-pin-preserved":
        base_build_constraints = head_build_constraints = ["hatchling==1.27.0"]
    elif variant == "build-pin-lowered":
        base_build_constraints, head_build_constraints = ["hatchling==1.27.0"], ["hatchling==1.26.0"]
    elif variant == "build-pin-removed":
        base_build_constraints, head_build_constraints = ["hatchling==1.27.0"], []
    elif variant == "group-floor-raised":
        base_groups, head_groups = {"dev": ["pytest>=9.0.3"]}, {"dev": ["pytest>=9.0.4"]}
    elif variant == "group-floor-lowered":
        base_groups, head_groups = {"dev": ["pytest>=9.0.3"]}, {"dev": ["pytest>=9.0.2"]}
    elif variant == "group-floor-removed":
        base_groups = {"dev": ["pytest>=9.0.3"]}
        head_groups = {"dev": []}
    elif variant == "group-pin-lowered":
        base_groups, head_groups = {"build": ["hatchling==1.27.0"]}, {"build": ["hatchling==1.26.0"]}
    elif variant == "group-context-swap":
        base_groups = {"pydantic-v1": ["pydantic>=1.10"], "pydantic-v2": ["pydantic>=2"]}
        head_groups = {"pydantic-v1": ["pydantic>=2"], "pydantic-v2": ["pydantic>=1.10"]}
    elif variant == "unbounded-group-preserved":
        base_groups = head_groups = {"dev": ["ruff"]}
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[],
        head_requirements=[],
        base_packages=[
            ("cryptography", "50.0.0"),
            ("requests", "2.33.0"),
            ("hatchling", "1.27.0"),
            ("pytest", "9.0.3"),
            ("pydantic", "1.10"),
            ("pydantic", "2"),
            ("ruff", "1"),
        ],
        head_packages=[
            ("cryptography", "50.0.0"),
            ("requests", "2.33.0"),
            ("hatchling", "1.27.0"),
            ("pytest", "9.0.3"),
            ("pydantic", "1.10"),
            ("pydantic", "2"),
            ("ruff", "1"),
        ],
        base_constraints=base_constraints,
        head_constraints=head_constraints,
        base_build_constraints=base_build_constraints,
        head_build_constraints=head_build_constraints,
        base_dependency_groups=base_groups,
        head_dependency_groups=head_groups,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


def test_security_floor_parser_strips_requirement_whitespace() -> None:
    assert "stable_version(matches[0].strip())" in security_dependency_floor_program()


@pytest.mark.parametrize(
    ("sha", "origin"),
    [
        pytest.param("invalid", "https://github.com/openai/openai-python", id="untrusted-base"),
        pytest.param("a" * 40, "https://github.com/attacker/openai-python", id="untrusted-origin"),
    ],
)
def test_security_floor_guard_rejects_untrusted_base(tmp_path: Path, sha: str, origin: str) -> None:
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["danger-pkg>=1.0"],
        head_requirements=["danger-pkg>=1.1"],
        base_packages=[("danger-pkg", "1.0")],
        head_packages=[("danger-pkg", "1.1")],
        sha=sha,
        origin=origin,
    )
    assert result.returncode != 0


def test_routine_dependency_updates_preserve_lock_only_strategy() -> None:
    config = (ROOT / ".github/dependabot.yml").read_text()
    assert "versioning-strategy: increase-if-necessary" in config
    assert re.search(r"python-security:\n\s+applies-to: security-updates", config)
    security_dependency_floor_program()


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
