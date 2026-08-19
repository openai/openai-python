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
    sha: str = "a" * 40,
    origin: str = "https://github.com/openai/openai-python",
) -> subprocess.CompletedProcess[str]:
    def project(requirements: list[str]) -> str:
        if optional:
            return (
                '[project]\nname = "openai"\nversion = "1.0"\ndependencies = []\n'
                + "[project.optional-dependencies]\nfeature = "
                + json.dumps(requirements)
                + "\n"
            )
        return '[project]\nname = "openai"\nversion = "1.0"\ndependencies = ' + json.dumps(requirements) + "\n"

    def lock(packages: list[tuple[str, str]]) -> str:
        return "\n".join(
            f"[[package]]\nname = {json.dumps(name)}\nversion = {json.dumps(version)}\n" for name, version in packages
        )

    (tmp_path / "pyproject.toml").write_text(project(head_requirements))
    (tmp_path / "uv.lock").write_text(lock(head_packages))
    (tmp_path / "base-project.toml").write_text(project(base_requirements))
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
            ["numpy>=1.1", "numpy>=2.0.2"],
            [("numpy", "2.0.2")],
            [("numpy", "2.1.0")],
            True,
            True,
            id="optional-multiple-floors-weakest-raised",
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
