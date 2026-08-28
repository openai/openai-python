from __future__ import annotations

import os
import re
import sys
import json
import shutil
import subprocess
from typing import Any, cast
from pathlib import Path

import pytest
from packaging.markers import Marker
from packaging.version import Version
from packaging.requirements import Requirement

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
        if "python -I -c '" in entry and "Use only the public PyPI registry" in entry
    )
    command = line.split("python -I -c '", 1)[1].rsplit("'", 1)[0]
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
    uv_overrides: dict[str, object] | None = None,
    extra_uv_config: str | None = None,
    project_name: str | None = None,
    trusted_fork: bool = False,
    trusted_base_requires: list[str] | None = None,
    trusted_base_group: list[str] | None = None,
    trusted_base_constraints: list[str] | None = None,
    trusted_base_backend: str = "hatchling.build",
    trusted_base_sha: str = "a" * 40,
    trusted_base_lock: str | None = None,
    trusted_origin: str = "https://github.com/openai/openai-python.git",
    hatch_configuration: str = "",
    trusted_hatch_configuration: str = "",
    hatch_files: dict[str, str] | None = None,
    trusted_hatch_files: dict[str, str] | None = None,
    hatch_symlinks: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    requires = ["hatchling==1.27.0"] if build_requires is None else build_requires
    group = ["hatchling==1.27.0"] if build_group is None else build_group
    constraints = ["hatchling==1.27.0"] if build_constraints is None else build_constraints
    if project_name is None:
        project_name = project["name"]
    configuration = (
        f"[project]\nname = {json.dumps(project_name)}\nversion = {json.dumps(project['version'])}\n"
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
    if uv_overrides is not None:
        for name, value in uv_overrides.items():
            configuration += name + " = " + json.dumps(value) + "\n"
    if uv_sources is not None:
        configuration += "[tool.uv.sources]\n"
        for name, configured_source in uv_sources.items():
            values = ", ".join(key + " = " + json.dumps(value) for key, value in configured_source.items())
            configuration += name + " = { " + values + " }\n"
    configuration += hatch_configuration
    (tmp_path / "pyproject.toml").write_text(configuration)
    for name, contents in (hatch_files or {}).items():
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(contents)
    for name, target in (hatch_symlinks or {}).items():
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.symlink_to(target)
    if extra_uv_config is not None:
        (tmp_path / extra_uv_config).write_text('no-binary-package = ["reviewed-dependency"]\n')

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
        wheels = package.get("wheels")
        if "wheels" not in package and source == {"registry": "https://pypi.org/simple"}:
            wheels = (
                []
                if package.get("sdist_only") or "sdist" in package and package["sdist"] is None
                else [
                    {
                        "url": "https://files.pythonhosted.org/packages/reviewed-1.0.0-py3-none-any.whl",
                        "hash": "sha256:" + "b" * 64,
                    }
                ]
            )
        if wheels is not None:
            assert isinstance(wheels, list)
            typed_wheels = cast(list[dict[str, object]], wheels)
            wheel_values = [
                "{ " + ", ".join(f"{key} = {json.dumps(value)}" for key, value in wheel.items()) + " }"
                for wheel in typed_wheels
            ]
            lines.append("wheels = [" + ", ".join(wheel_values) + "]")
        lines.append("")

    (tmp_path / "uv.lock").write_text("\n".join(lines))
    environment = dict(
        os.environ,
        UNTRUSTED_BUILD_FORK="1" if trusted_fork else "0",
        TRUSTED_BUILD_BASE_SHA=trusted_base_sha,
    )
    if trusted_fork:
        reviewed_requires = ["hatchling==1.27.0"] if trusted_base_requires is None else trusted_base_requires
        reviewed_group = ["hatchling==1.27.0"] if trusted_base_group is None else trusted_base_group
        reviewed_constraints = ["hatchling==1.27.0"] if trusted_base_constraints is None else trusted_base_constraints
        trusted_configuration = (
            "[build-system]\nrequires = "
            + json.dumps(reviewed_requires)
            + "\nbuild-backend = "
            + json.dumps(trusted_base_backend)
            + "\n[dependency-groups]\nbuild = "
            + json.dumps(reviewed_group)
            + "\n[tool.uv]\nbuild-constraint-dependencies = "
            + json.dumps(reviewed_constraints)
            + "\n"
        )
        trusted_configuration += trusted_hatch_configuration
        (tmp_path / "trusted-base.toml").write_text(trusted_configuration)
        for name, contents in (trusted_hatch_files or {}).items():
            destination = tmp_path / ".trusted-hooks" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(contents)
        (tmp_path / "trusted-base.lock").write_text(
            (tmp_path / "uv.lock").read_text() if trusted_base_lock is None else trusted_base_lock
        )
        fake_git = tmp_path / "git"
        fake_git.write_text(
            f"#!{sys.executable}\n"
            "import pathlib, sys\n"
            f"root = pathlib.Path({str(tmp_path)!r})\n"
            f"origin = {trusted_origin!r}\n"
            f"sha = {trusted_base_sha!r}\n"
            "arguments = sys.argv[1:]\n"
            "if arguments == ['remote', 'get-url', 'origin']:\n"
            "    print(origin)\n"
            "elif arguments == ['fetch', '--no-tags', '--depth=1', 'origin', sha]:\n"
            "    pass\n"
            "elif arguments == ['show', sha + ':pyproject.toml']:\n"
            "    print((root / 'trusted-base.toml').read_text(), end='')\n"
            "elif arguments == ['show', sha + ':uv.lock']:\n"
            "    print((root / 'trusted-base.lock').read_text(), end='')\n"
            "elif len(arguments) == 2 and arguments[0] == 'show' and arguments[1].startswith(sha + ':'):\n"
            "    path = root / '.trusted-hooks' / arguments[1].split(':', 1)[1]\n"
            "    sys.stdout.buffer.write(path.read_bytes())\n"
            "else:\n"
            "    raise SystemExit('Unexpected or unsafe git operation')\n"
        )
        fake_git.chmod(0o755)
        environment["PATH"] = str(tmp_path) + os.pathsep + environment["PATH"]
    return subprocess.run(
        [sys.executable, "-c", dependency_lock_source_command()],
        cwd=tmp_path,
        env=environment,
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


@pytest.mark.parametrize(
    ("project_name", "registry_name", "accepted"),
    [
        pytest.param("openai", "reviewed-dependency", True, id="only-reviewed-editable-root"),
        pytest.param("openai", "openai", False, id="public-registry-root-name-collision"),
        pytest.param("openai", "OpenAI", False, id="public-registry-root-case-alias"),
        pytest.param("openai", "OPENAI", False, id="public-registry-root-uppercase-alias"),
        pytest.param("renamed-root", "openai", False, id="renamed-root-exempts-public-openai"),
        pytest.param("open_ai", "openai", False, id="root-normalization-cannot-change-exemption"),
    ],
)
def test_source_build_exemption_only_covers_the_unique_reviewed_editable_root(
    tmp_path: Path, project_name: str, registry_name: str, accepted: bool
) -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    root: dict[str, object] = {
        "name": project_name,
        "version": project["version"],
        "source": {"editable": "."},
    }
    dependency: dict[str, object] = {
        "name": registry_name,
        "version": "1.0.0",
        "source": {"registry": "https://pypi.org/simple"},
    }

    result = run_dependency_lock_source_check(tmp_path, [root, dependency], project_name=project_name)

    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr
    if not accepted:
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


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("reviewed-fork", True, id="fork-keeps-trusted-base-build-pins"),
        pytest.param("fork-hatchling-downgrade", False, id="fork-cannot-downgrade-public-hatchling"),
        pytest.param("fork-hatchling-upgrade", False, id="fork-cannot-swap-public-hatchling-release"),
        pytest.param("fork-build-pin-downgrade", False, id="fork-cannot-change-transitive-backend-pin"),
        pytest.param("fork-extra-build-pin", False, id="fork-cannot-add-unreviewed-backend-package"),
        pytest.param("fork-marker-change", False, id="fork-cannot-change-reviewed-build-marker"),
        pytest.param("fork-marker-literal-case", False, id="fork-cannot-change-case-sensitive-marker"),
        pytest.param("fork-backend-change", False, id="fork-backend-must-match-trusted-base"),
        pytest.param("fork-invalid-base-sha", False, id="fork-rejects-untrusted-base-sha"),
        pytest.param("fork-foreign-origin", False, id="fork-rejects-untrusted-git-origin"),
        pytest.param("fork-credential-origin", False, id="fork-rejects-credential-bearing-origin"),
        pytest.param("fork-canonical-reorder", True, id="fork-allows-canonical-pins-and-reordering"),
        pytest.param("fork-reviewed-base-update", True, id="fork-allows-already-reviewed-base-update"),
        pytest.param("trusted-maintainer-update", True, id="same-repo-maintainer-can-update-build-pins"),
        pytest.param("trusted-dependabot-update", True, id="same-repo-security-bot-can-update-build-pins"),
    ],
)
def test_fork_build_backend_must_match_immutable_reviewed_base(tmp_path: Path, variant: str, accepted: bool) -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    root: dict[str, object] = {
        "name": project["name"],
        "version": project["version"],
        "source": {"editable": "."},
    }
    hatchling: dict[str, object] = {
        "name": "hatchling",
        "version": "1.27.0",
        "source": {"registry": "https://pypi.org/simple"},
    }
    packages: list[dict[str, object]] = [root, hatchling]
    requires = ["hatchling==1.27.0"]
    group = ["hatchling==1.27.0"]
    constraints = ["hatchling==1.27.0"]
    base_requires = ["hatchling==1.27.0"]
    base_group = ["hatchling==1.27.0"]
    base_constraints = ["hatchling==1.27.0"]
    base_backend = "hatchling.build"
    base_sha = "a" * 40
    origin = "https://github.com/openai/openai-python.git"
    fork = not variant.startswith("trusted-")

    if variant in {"fork-hatchling-downgrade", "fork-hatchling-upgrade"}:
        version = "1.26.0" if variant == "fork-hatchling-downgrade" else "1.28.0"
        hatchling["version"] = version
        requires = group = constraints = ["hatchling==" + version]
    elif variant in {"fork-build-pin-downgrade", "fork-extra-build-pin", "fork-canonical-reorder"}:
        version = "25.0" if variant == "fork-build-pin-downgrade" else "26.3"
        packages.append(
            {
                "name": "packaging",
                "version": version,
                "source": {"registry": "https://pypi.org/simple"},
            }
        )
        if variant == "fork-canonical-reorder":
            group = constraints = ["PACKAGING == 26.3", "hatchling==1.27.0"]
        else:
            group = constraints = ["hatchling==1.27.0", "packaging==" + version]
        if variant != "fork-extra-build-pin":
            base_group = base_constraints = ["hatchling==1.27.0", "packaging==26.3"]
    elif variant in {"fork-marker-change", "fork-marker-literal-case"}:
        packages.append(
            {
                "name": "tomli",
                "version": "2.4.1",
                "source": {"registry": "https://pypi.org/simple"},
            }
        )
        if variant == "fork-marker-change":
            head_marker = "python_version < '3.12'"
            base_marker = "python_version < '3.11'"
        else:
            head_marker = "sys_platform == 'linux'"
            base_marker = "sys_platform == 'Linux'"
        group = constraints = ["hatchling==1.27.0", "tomli==2.4.1; " + head_marker]
        base_group = base_constraints = ["hatchling==1.27.0", "tomli==2.4.1; " + base_marker]
    elif variant == "fork-backend-change":
        base_backend = "reviewed.backend"
    elif variant == "fork-invalid-base-sha":
        base_sha = "a" * 39 + "Z"
    elif variant == "fork-foreign-origin":
        origin = "https://github.com/unreviewed/openai-python.git"
    elif variant == "fork-credential-origin":
        origin = "https://token@github.com/openai/openai-python.git"
    elif variant in {"fork-reviewed-base-update", "trusted-maintainer-update", "trusted-dependabot-update"}:
        hatchling["version"] = "1.28.0"
        requires = group = constraints = ["hatchling==1.28.0"]
        if variant == "fork-reviewed-base-update":
            base_requires = base_group = base_constraints = ["hatchling==1.28.0"]

    result = run_dependency_lock_source_check(
        tmp_path,
        packages,
        build_requires=requires,
        build_group=group,
        build_constraints=constraints,
        trusted_fork=fork,
        trusted_base_requires=base_requires,
        trusted_base_group=base_group,
        trusted_base_constraints=base_constraints,
        trusted_base_backend=base_backend,
        trusted_base_sha=base_sha,
        trusted_origin=origin,
    )

    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("fork-added-global", False, id="fork-cannot-add-executable-global-hatch-hook"),
        pytest.param("fork-added-target", False, id="fork-cannot-add-executable-target-hatch-hook"),
        pytest.param("fork-added-metadata", False, id="fork-cannot-add-executable-metadata-hatch-hook"),
        pytest.param("fork-changed-path", False, id="fork-cannot-redirect-reviewed-custom-hook"),
        pytest.param("fork-modified-source", False, id="fork-cannot-modify-reviewed-custom-hook-source"),
        pytest.param("fork-missing-source", False, id="fork-cannot-remove-reviewed-custom-hook-source"),
        pytest.param("fork-symlink-source", False, id="fork-cannot-use-symlinked-custom-hook-source"),
        pytest.param("fork-traversal", False, id="fork-cannot-escape-checkout-through-custom-hook-path"),
        pytest.param("fork-reviewed-metadata", True, id="fork-preserves-immutable-reviewed-metadata-hook"),
        pytest.param("fork-reviewed-default", True, id="fork-preserves-immutable-reviewed-default-hook"),
        pytest.param("fork-packaging-change", True, id="fork-can-change-nonexecutable-hatch-build-metadata"),
        pytest.param("same-repo-maintainer", True, id="trusted-maintainer-can-change-hatch-hooks"),
        pytest.param("same-repo-dependabot", True, id="trusted-dependabot-can-change-hatch-hooks"),
    ],
)
def test_fork_hatch_hooks_and_sources_must_match_immutable_reviewed_base(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    packages: list[dict[str, object]] = [
        {"name": project["name"], "version": project["version"], "source": {"editable": "."}}
    ]
    reviewed = '[tool.hatch.metadata.hooks.custom]\npath = "scripts/hatch_metadata.py"\n'
    head = reviewed
    base = reviewed
    files = {"scripts/hatch_metadata.py": "reviewed = True\n"}
    trusted_files = dict(files)
    symlinks: dict[str, str] = {}

    if variant == "fork-added-global":
        head += '[tool.hatch.build.hooks.custom]\npath = "attacker.py"\n'
        files["attacker.py"] = "raise RuntimeError('unreviewed global hook')\n"
    elif variant == "fork-added-target":
        head += '[tool.hatch.build.targets.wheel.hooks.custom]\npath = "attacker.py"\n'
        files["attacker.py"] = "raise RuntimeError('unreviewed target hook')\n"
    elif variant == "fork-added-metadata":
        base = ""
    elif variant == "fork-changed-path":
        head = '[tool.hatch.metadata.hooks.custom]\npath = "attacker.py"\n'
        files["attacker.py"] = "raise RuntimeError('unreviewed metadata hook')\n"
    elif variant == "fork-modified-source":
        files["scripts/hatch_metadata.py"] = "raise RuntimeError('modified reviewed hook')\n"
    elif variant == "fork-missing-source":
        files.clear()
    elif variant == "fork-symlink-source":
        files = {"reviewed.py": "reviewed = True\n"}
        symlinks = {"scripts/hatch_metadata.py": "../reviewed.py"}
    elif variant == "fork-traversal":
        head = base = '[tool.hatch.metadata.hooks.custom]\npath = "../outside.py"\n'
        files.clear()
        trusted_files.clear()
    elif variant == "fork-reviewed-default":
        head = base = "[tool.hatch.build.hooks.custom]\n"
        files = trusted_files = {"hatch_build.py": "reviewed = True\n"}
    elif variant == "fork-packaging-change":
        head += '[tool.hatch.build]\ninclude = ["different/*"]\n'
        base += '[tool.hatch.build]\ninclude = ["src/*"]\n'
    elif variant.startswith("same-repo-"):
        head += '[tool.hatch.build.hooks.custom]\npath = "new-maintainer-hook.py"\n'
        files["new-maintainer-hook.py"] = "reviewed_maintainer_update = True\n"

    result = run_dependency_lock_source_check(
        tmp_path,
        packages,
        trusted_fork=not variant.startswith("same-repo-"),
        hatch_configuration=head,
        trusted_hatch_configuration=base,
        hatch_files=files,
        trusted_hatch_files=trusted_files,
        hatch_symlinks=symlinks,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("added-default", False, id="fork-cannot-add-unreviewed-default-wheel"),
        pytest.param("added-optional", False, id="fork-cannot-add-unreviewed-optional-wheel"),
        pytest.param("removed-package", False, id="fork-cannot-remove-immutable-reviewed-identity"),
        pytest.param("replaced-name", False, id="fork-cannot-swap-reviewed-package-name"),
        pytest.param("replaced-version", False, id="fork-cannot-swap-reviewed-package-version"),
        pytest.param("replaced-wheel-url", False, id="fork-cannot-swap-reviewed-wheel-url"),
        pytest.param("replaced-wheel-hash", False, id="fork-cannot-swap-reviewed-wheel-hash"),
        pytest.param("replaced-sdist-url", False, id="fork-cannot-swap-reviewed-source-url"),
        pytest.param("replaced-sdist-hash", False, id="fork-cannot-swap-reviewed-source-hash"),
        pytest.param("added-wheel", False, id="fork-cannot-add-an-unreviewed-wheel"),
        pytest.param("removed-wheel", False, id="fork-cannot-drop-an-immutable-reviewed-wheel"),
        pytest.param("duplicate-package", False, id="fork-cannot-hide-an-extra-identity-in-a-set"),
        pytest.param("reordered-wheels", True, id="fork-may-reorder-identical-reviewed-artifacts"),
        pytest.param("canonical-name", True, id="fork-may-canonicalize-identical-reviewed-name"),
        pytest.param("same-repo-maintainer", True, id="same-repo-maintainer-may-update-wheel"),
        pytest.param("same-repo-dependabot", True, id="same-repo-security-bot-may-add-wheel"),
    ],
)
def test_fork_dependency_identities_must_match_immutable_reviewed_lock(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    root: dict[str, object] = {
        "name": project["name"],
        "version": project["version"],
        "source": {"editable": "."},
    }
    reviewed: dict[str, object] = {
        "name": "reviewed_dependency",
        "version": "2.0",
        "source": {"registry": "https://pypi.org/simple"},
        "sdist": {
            "url": "https://files.pythonhosted.org/packages/reviewed-2.0.tar.gz",
            "hash": "sha256:" + "a" * 64,
        },
        "wheels": [
            {
                "url": "https://files.pythonhosted.org/packages/reviewed-2.0-py3-none-any.whl",
                "hash": "sha256:" + "b" * 64,
            },
            {
                "url": "https://files.pythonhosted.org/packages/reviewed-2.0-linux.whl",
                "hash": "sha256:" + "c" * 64,
            },
        ],
    }
    baseline = run_dependency_lock_source_check(tmp_path, [root, reviewed], trusted_fork=True)
    assert baseline.returncode == 0, baseline.stdout + baseline.stderr
    trusted_lock = (tmp_path / "uv.lock").read_text()
    packages = cast(list[dict[str, object]], json.loads(json.dumps([root, reviewed])))
    package = packages[1]
    wheels = cast(list[dict[str, str]], package["wheels"])
    sdist = cast(dict[str, str], package["sdist"])
    fork = not variant.startswith("same-repo-")

    if variant in {"added-default", "added-optional", "same-repo-dependabot"}:
        packages.append(
            {
                "name": "attacker-owned-plugin",
                "version": "1.0",
                "source": {"registry": "https://pypi.org/simple"},
            }
        )
    elif variant == "removed-package":
        packages.pop()
    elif variant == "replaced-name":
        package["name"] = "attacker-owned-plugin"
    elif variant in {"replaced-version", "same-repo-maintainer"}:
        package["version"] = "2.1"
    elif variant == "replaced-wheel-url":
        wheels[0]["url"] = "https://files.pythonhosted.org/packages/attacker-2.0-py3-none-any.whl"
    elif variant == "replaced-wheel-hash":
        wheels[0]["hash"] = "sha256:" + "d" * 64
    elif variant == "replaced-sdist-url":
        sdist["url"] = "https://files.pythonhosted.org/packages/attacker-2.0.tar.gz"
    elif variant == "replaced-sdist-hash":
        sdist["hash"] = "sha256:" + "d" * 64
    elif variant == "added-wheel":
        wheels.append(
            {
                "url": "https://files.pythonhosted.org/packages/attacker-2.0-linux.whl",
                "hash": "sha256:" + "d" * 64,
            }
        )
    elif variant == "removed-wheel":
        wheels.pop()
    elif variant == "duplicate-package":
        packages.append(cast(dict[str, object], json.loads(json.dumps(package))))
    elif variant == "reordered-wheels":
        wheels.reverse()
        packages.reverse()
    elif variant == "canonical-name":
        package["name"] = "Reviewed.Dependency"

    result = run_dependency_lock_source_check(
        tmp_path,
        packages,
        trusted_fork=fork,
        trusted_base_lock=trusted_lock,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


def test_fork_build_provenance_uses_immutable_pull_request_identity() -> None:
    for name in ("ci.yml", "detect-breaking-changes.yml"):
        workflow = (ROOT / ".github/workflows" / name).read_text()
        environment = workflow.split("\njobs:\n", 1)[0].rsplit("\nenv:\n", 1)[1]
        fork = next(line for line in environment.splitlines() if "UNTRUSTED_BUILD_FORK:" in line)
        base = next(line for line in environment.splitlines() if "TRUSTED_BUILD_BASE_SHA:" in line)
        assert "github.event_name == 'pull_request'" in fork
        assert "github.event.pull_request.head.repo.id != github.event.pull_request.base.repo.id" in fork
        assert "github.event_name == 'pull_request'" in base
        assert "github.event.pull_request.base.sha" in base
        assert "github.sha" not in base


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("reviewed-wheel", True, id="reviewed-public-wheel"),
        pytest.param("sdist-only", False, id="unreviewed-source-distribution-backend"),
        pytest.param("empty-wheels", False, id="empty-wheel-list"),
        pytest.param("no-binary", False, id="force-all-source-builds"),
        pytest.param("no-binary-package", False, id="force-package-source-build"),
        pytest.param("no_binary", False, id="force-all-source-builds-alias"),
        pytest.param("no_binary_package", False, id="force-package-source-build-alias"),
        pytest.param("uv.toml", False, id="standalone-uv-config-source-override"),
        pytest.param(".uv.toml", False, id="hidden-uv-config-source-override"),
    ],
)
def test_public_dependencies_require_reviewed_wheels_without_build_overrides(
    tmp_path: Path, variant: str, accepted: bool
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
    }
    overrides: dict[str, object] | None = None
    config: str | None = None
    if variant == "sdist-only":
        dependency["sdist_only"] = True
    elif variant == "empty-wheels":
        dependency["wheels"] = []
    elif variant in {"no-binary", "no_binary"}:
        overrides = {variant: True}
    elif variant in {"no-binary-package", "no_binary_package"}:
        overrides = {variant: ["reviewed-dependency"]}
    elif variant in {"uv.toml", ".uv.toml"}:
        config = variant
    result = run_dependency_lock_source_check(
        tmp_path,
        [root, dependency],
        uv_overrides=overrides,
        extra_uv_config=config,
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
    assert source.strip().startswith("python -I -c '")

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


@pytest.mark.parametrize(
    ("event", "experimental", "allowed"),
    [
        pytest.param("pull_request", False, False, id="fork-pr-supported-python"),
        pytest.param("pull_request", True, False, id="fork-pr-never-gets-prerelease-exception"),
        pytest.param("push", True, False, id="push-never-gets-prerelease-exception"),
        pytest.param("merge_group", True, False, id="merge-queue-never-gets-prerelease-exception"),
        pytest.param("schedule", False, False, id="scheduled-supported-python-wheels-only"),
        pytest.param("schedule", True, True, id="trusted-scheduled-prerelease-preserved"),
        pytest.param("workflow_dispatch", True, True, id="trusted-manual-prerelease-preserved"),
    ],
)
def test_source_builds_only_allowed_in_trusted_experimental_compatibility(
    event: str, experimental: bool, allowed: bool
) -> None:
    for name in ("ci.yml", "detect-breaking-changes.yml"):
        workflow = (ROOT / ".github/workflows" / name).read_text()
        global_environment = workflow.split("\njobs:\n", 1)[0].rsplit("\nenv:\n", 1)[1]
        assert re.search(r"^  UV_NO_BUILD: ['\"]?1['\"]?\s*$", global_environment, re.MULTILINE)
        assert re.search(r"^  UV_NO_BINARY_PACKAGE: ['\"]?openai['\"]?\s*$", global_environment, re.MULTILINE)
    compatibility = dependency_workflow_jobs()["compatibility"]
    assert "matrix.experimental" in compatibility
    assert "(github.event_name == 'schedule' || github.event_name == 'workflow_dispatch')" in compatibility
    assert "&& '0' || '1'" in compatibility
    assert "environment:" not in compatibility
    assert "id-token:" not in compatibility
    assert (experimental and event in {"schedule", "workflow_dispatch"}) is allowed


def test_editable_project_sync_requires_only_the_reviewed_root_build_exemption() -> None:
    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("uv is not installed")

    command = [uv, "--no-config", "sync", "--frozen", "--all-extras", "--offline", "--dry-run"]
    environment = dict(os.environ)
    environment["UV_NO_BUILD"] = "1"
    environment.pop("UV_NO_BINARY_PACKAGE", None)

    rejected = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert rejected.returncode != 0
    assert "openai" in rejected.stderr
    assert "--no-build" in rejected.stderr

    environment["UV_NO_BINARY_PACKAGE"] = "openai"
    accepted = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr


def test_explicit_root_build_keeps_every_public_dependency_source_build_disabled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    build = dependency_workflow_jobs()["build"]
    match = re.search(
        r"      - name: Run build\n        run: \|\n(?P<body>(?:          [^\n]*\n)+)",
        build,
    )
    assert match is not None
    script = "\n".join(line[10:] for line in match.group("body").splitlines())
    assert "env -u UV_NO_BUILD UV_NO_BUILD_PACKAGE=" in script
    assert "UV_NO_BUILD=0" not in script

    log = tmp_path / "calls.jsonl"
    executable = tmp_path / "uv"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json, os, pathlib, sys\n"
        "entry = {'args': sys.argv[1:], 'no_build': os.environ.get('UV_NO_BUILD'), "
        "'no_build_packages': os.environ.get('UV_NO_BUILD_PACKAGE')}\n"
        "with open(os.environ['UV_TEST_LOG'], 'a') as output:\n"
        "    output.write(json.dumps(entry) + '\\n')\n"
        "if sys.argv[1] == 'export':\n"
        "    pathlib.Path(sys.argv[sys.argv.index('--output-file') + 1]).write_text('reviewed\\n')\n"
        "if sys.argv[1] == 'build':\n"
        "    assert '--no-sources' in sys.argv and '--require-hashes' in sys.argv\n"
        "    assert pathlib.Path(sys.argv[sys.argv.index('--build-constraints') + 1]).read_text() == 'reviewed\\n'\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("UV_TEST_LOG", str(log))
    monkeypatch.setenv("UV_NO_BUILD", "1")

    result = subprocess.run(["bash", "-e", "-c", script], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    calls: list[dict[str, Any]] = [json.loads(line) for line in log.read_text().splitlines()]
    assert [call["args"][0] for call in calls] == ["export", "build"]
    lock = tomllib.loads((ROOT / "uv.lock").read_text())
    expected = {
        re.sub(r"[-_.]+", "-", cast(str, package["name"])).lower()
        for package in cast(list[dict[str, object]], lock["package"])
        if package["source"] == {"registry": "https://pypi.org/simple"}
    }
    assert expected
    assert "openai" not in expected
    for call in calls:
        assert call["no_build"] is None
        assert set(cast(str, call["no_build_packages"]).split()) == expected


def test_package_scoped_root_build_policy_rejects_real_external_source_distribution(tmp_path: Path) -> None:
    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("uv is not installed")

    environment = dict(os.environ)
    environment.pop("UV_NO_BUILD", None)
    environment["UV_NO_BUILD_PACKAGE"] = "aiohttp"
    environment["UV_NO_BINARY_PACKAGE"] = "openai aiohttp"
    environment["UV_PROJECT_ENVIRONMENT"] = str(tmp_path / "isolated")
    result = subprocess.run(
        [uv, "--no-config", "sync", "--frozen", "--all-extras", "--offline", "--dry-run"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "aiohttp" in result.stderr
    assert "--no-build" in result.stderr


def test_breaking_change_installer_validates_provenance_first() -> None:
    path = ROOT / ".github/workflows/detect-breaking-changes.yml"
    if not path.exists():
        pytest.skip("GitHub workflows are not included in source distributions")

    match = re.search(
        r"^  detect_breaking_changes:\n(?P<body>.*?)(?=^  [\w-]+:\n|\Z)",
        path.read_text(),
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None
    job = match.group("body")
    steps = re.findall(r"^      - (?:name|uses):\s*(.+)$", job, re.MULTILINE)
    assert re.fullmatch(r"actions/checkout@[0-9a-f]{40}.*", steps[0])
    assert steps[1] == "Verify dependency source provenance before installing tools"
    source = next(line for line in job.splitlines() if "Use only the public PyPI registry" in line)
    command = source.split("python -I -c '", 1)[1].rsplit("'", 1)[0]
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()
    expected = next(line for line in workflow.splitlines() if "Use only the public PyPI registry" in line)
    assert command == expected.split("python -I -c '", 1)[1].rsplit("'", 1)[0]


def test_security_dependency_policy_is_directly_testable_after_the_trusted_gate() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()
    job = dependency_workflow_jobs()["dependency-locks"]
    gate = job.index("Verify dependency source provenance before installing tools")
    policy = job.index('git show "$BASE_SHA:scripts/check-dependency-security.py" | python -I -')
    assert gate < policy
    assert "python - <<'PY'" not in job
    script = ROOT / "scripts/check-dependency-security.py"
    assert script.is_file()
    assert 'import_module("tomllib")' in script.read_text()
    assert workflow.count("Use only the public PyPI registry") == 1


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
    assert "set -euo pipefail" in body
    assert 'git fetch --no-tags --depth=1 origin "$BASE_SHA"' in body
    assert 'git show "$BASE_SHA:scripts/check-dependency-security.py" | python -I -' in body
    program = (ROOT / "scripts/check-dependency-security.py").read_text()
    if sys.version_info < (3, 11):
        program = program.replace(
            "from __future__ import annotations",
            "from __future__ import annotations\nimport sys, tomli; sys.modules['tomllib'] = tomli",
            1,
        )
    return program


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("trusted-base", True, id="security-checker-runs-only-immutable-base-script"),
        pytest.param("tampered-head", True, id="submitted-no-op-cannot-replace-trusted-checker"),
        pytest.param("missing-base-script", False, id="missing-trusted-checker-never-falls-back-to-head"),
        pytest.param("invalid-base", False, id="checker-rejects-noncanonical-event-base-sha"),
        pytest.param("foreign-origin", False, id="checker-rejects-an-attacker-controlled-origin"),
        pytest.param("credential-origin", False, id="checker-rejects-credential-bearing-origin"),
        pytest.param("stdlib-shadow", True, id="isolated-trusted-checker-ignores-checkout-module-shadow"),
    ],
)
def test_security_floor_checker_executes_only_authenticated_base(tmp_path: Path, variant: str, accepted: bool) -> None:
    gate = dependency_workflow_jobs()["dependency-locks"]
    step = gate.split("      - name: Require published minimums for direct security updates\n", 1)[1]
    step = step.split("\n      - name:", 1)[0]
    match = re.search(
        r"        run: (?:(?P<inline>[^|\n][^\n]*)|\|\n(?P<block>(?:          [^\n]*(?:\n|$))+))",
        step,
    )
    assert match is not None
    program = (
        match.group("inline")
        if match.group("inline") is not None
        else "\n".join(line[10:] for line in match.group("block").splitlines())
    )
    sha = "a" * 40 if variant != "invalid-base" else "a" * 39 + "Z"
    origin = "https://github.com/openai/openai-python.git"
    if variant == "foreign-origin":
        origin = "https://github.com/attacker/openai-python.git"
    elif variant == "credential-origin":
        origin = "https://token@github.com/openai/openai-python.git"

    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "check-dependency-security.py").write_text(
        "import pathlib; pathlib.Path('executed-head').write_text('attacker')\n"
    )
    if variant == "stdlib-shadow":
        (tmp_path / "subprocess.py").write_text(
            "import pathlib; pathlib.Path('shadow-imported').write_text('attacker')\n"
        )
    trusted_program = (
        "import subprocess, pathlib\n"
        "assert pathlib.Path(subprocess.__file__).resolve().parent != pathlib.Path.cwd()\n"
        "pathlib.Path('executed-base').write_text('trusted')\n"
    )
    fake_git = tmp_path / "git"
    fake_git.write_text(
        f"#!{sys.executable}\n"
        "import sys\n"
        f"sha = {sha!r}\n"
        f"origin = {origin!r}\n"
        f"missing = {variant == 'missing-base-script'!r}\n"
        f"source = {trusted_program!r}\n"
        "arguments = sys.argv[1:]\n"
        "if arguments == ['remote', 'get-url', 'origin']:\n"
        "    print(origin)\n"
        "elif arguments == ['fetch', '--no-tags', '--depth=1', 'origin', sha]:\n"
        "    pass\n"
        "elif arguments == ['show', sha + ':scripts/check-dependency-security.py'] and not missing:\n"
        "    print(source, end='')\n"
        "else:\n"
        "    raise SystemExit('Unexpected or unsafe git operation')\n"
    )
    fake_git.chmod(0o755)
    environment = dict(os.environ, BASE_SHA=sha, PATH=str(tmp_path) + os.pathsep + os.environ["PATH"])
    result = subprocess.run(
        ["/bin/bash", "-euo", "pipefail", "-c", program],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr
    assert (tmp_path / "executed-base").exists() is accepted
    assert not (tmp_path / "executed-head").exists()
    assert not (tmp_path / "shadow-imported").exists()


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
    base_resolution_markers: dict[tuple[str, str], list[str]] | None = None,
    head_resolution_markers: dict[tuple[str, str], list[str]] | None = None,
    base_lock_dependencies: dict[tuple[str, str], list[dict[str, object]]] | None = None,
    head_lock_dependencies: dict[tuple[str, str], list[dict[str, object]]] | None = None,
    base_lock_optional_dependencies: dict[tuple[str, str], dict[str, list[dict[str, object]]]] | None = None,
    head_lock_optional_dependencies: dict[tuple[str, str], dict[str, list[dict[str, object]]]] | None = None,
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

    def lock(
        packages: list[tuple[str, str]],
        resolutions: dict[tuple[str, str], list[str]] | None,
        dependencies: dict[tuple[str, str], list[dict[str, object]]] | None,
        optional_dependencies: dict[tuple[str, str], dict[str, list[dict[str, object]]]] | None,
    ) -> str:
        def edges(values: list[dict[str, object]]) -> str:
            return (
                "["
                + ", ".join(
                    "{ " + ", ".join(key + " = " + json.dumps(value) for key, value in item.items()) + " }"
                    for item in values
                )
                + "]"
            )

        result: list[str] = []
        for name, version in packages:
            identity = name, version
            entry = f"[[package]]\nname = {json.dumps(name)}\nversion = {json.dumps(version)}\n"
            if resolutions is not None and identity in resolutions:
                entry += "resolution-markers = " + json.dumps(resolutions[identity]) + "\n"
            if dependencies is not None and identity in dependencies:
                entry += "dependencies = " + edges(dependencies[identity]) + "\n"
            if optional_dependencies is not None and identity in optional_dependencies:
                entry += "[package.optional-dependencies]\n"
                for extra, values in optional_dependencies[identity].items():
                    entry += json.dumps(extra) + " = " + edges(values) + "\n"
            result.append(entry)
        return "\n".join(result)

    (tmp_path / "pyproject.toml").write_text(
        project(
            head_requirements, head_optional_groups, head_constraints, head_build_constraints, head_dependency_groups
        )
    )
    (tmp_path / "uv.lock").write_text(
        lock(head_packages, head_resolution_markers, head_lock_dependencies, head_lock_optional_dependencies)
    )
    (tmp_path / "base-project.toml").write_text(
        project(
            base_requirements, base_optional_groups, base_constraints, base_build_constraints, base_dependency_groups
        )
    )
    (tmp_path / "base-lock.toml").write_text(
        lock(base_packages, base_resolution_markers, base_lock_dependencies, base_lock_optional_dependencies)
    )
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
            ["other>=2,<3"],
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
            True,
            id="unchanged-lock-valid-or-marker-remains-supported",
        ),
        pytest.param(
            ["other>=2; (python_version < '3.11')"],
            ["other>=2; (python_version < '3.11')"],
            [("other", "2")],
            [("other", "2")],
            False,
            True,
            id="unchanged-lock-parenthesized-marker-remains-supported",
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
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.0.post1"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.0.post1")],
            False,
            True,
            id="stable-post-release-security-fix",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.0.post0"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.0.post0")],
            False,
            True,
            id="stable-post-zero-above-base-release",
        ),
        pytest.param(
            ["danger-pkg>=1.0.post0"],
            ["danger-pkg>=1.0.post1"],
            [("danger-pkg", "1.0.post0")],
            [("danger-pkg", "1.0.post1")],
            False,
            True,
            id="stable-post-release-increases-monotonically",
        ),
        pytest.param(
            ["danger-pkg>=1.0.post9"],
            ["danger-pkg>=1.1"],
            [("danger-pkg", "1.0.post9")],
            [("danger-pkg", "1.1")],
            False,
            True,
            id="stable-next-release-above-post-release",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.0"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.0.post1")],
            False,
            False,
            id="base-floor-does-not-cover-post-security-fix",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.0.post9"],
            [("danger-pkg", "1.1")],
            [("danger-pkg", "1.0.post9")],
            False,
            False,
            id="post-release-cannot-downgrade-next-release",
        ),
        pytest.param(
            ["danger-pkg>=0!9.0"],
            ["danger-pkg>=1!1.0.post1"],
            [("danger-pkg", "9.0")],
            [("danger-pkg", "1!1.0.post1")],
            False,
            True,
            id="epoch-stable-post-security-fix",
        ),
        pytest.param(
            ["danger-pkg>=1.0"],
            ["danger-pkg>=1.0.0.post1"],
            [("danger-pkg", "1.0")],
            [("danger-pkg", "1.post1")],
            False,
            True,
            id="post-release-normalizes-trailing-zeroes",
        ),
        pytest.param(
            ["safe-direct>=1.0"],
            ["safe-direct>=1.0"],
            [("safe-direct", "1.0"), ("transitive", "1.0")],
            [("safe-direct", "1.0"), ("transitive", "1.1")],
            False,
            False,
            id="unbounded-transitive-security-update-rejected",
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


@pytest.mark.parametrize("scope", ["runtime", "optional", "protected"])
@pytest.mark.parametrize(
    ("previous", "current", "before", "after", "accepted"),
    [
        pytest.param(">=1,>=1.5", ">=1,>=2", "1.5", "2", True, id="strongest-redundant-floor-reaches-patched-release"),
        pytest.param(">=1.5,>=1", ">=2,>=1", "1.5", "2", True, id="strongest-redundant-floor-is-order-independent"),
        pytest.param(">=1,>=2", ">=1,>=1.5", "2", "2", False, id="strongest-redundant-floor-cannot-be-lowered"),
        pytest.param(
            ">=1,>=1.5", ">=1.1,>=1.5", "1.5", "2", False, id="weaker-redundant-floor-cannot-mask-patched-floor"
        ),
        pytest.param(
            ">=1.9,>=1.10", ">=1.9,>=1.11", "1.10", "1.11", True, id="redundant-floors-use-numeric-release-order"
        ),
        pytest.param(">=0!9,>=1!1", ">=0!9,>=1!2", "1!1", "1!2", True, id="redundant-floors-preserve-epoch-order"),
        pytest.param(
            ">=1,>=1.post1",
            ">=1,>=1.post2",
            "1.post1",
            "1.post2",
            True,
            id="redundant-floors-preserve-post-release-order",
        ),
        pytest.param(">1,>=1.5", ">1,>=2", "1.5", "2", True, id="strict-and-inclusive-floors-select-strongest"),
        pytest.param(">=1,>1.5", ">=1,>=2", "1.6", "2", True, id="stronger-inclusive-floor-preserves-strict-floor"),
        pytest.param(">1,>=1.post1", ">1,>=1.2", "1.1", "1.2", True, id="strict-final-floor-still-excludes-base-posts"),
        pytest.param("~=1.4,>=1.5", "~=1.4,>=1.7", "1.5", "1.7", True, id="compatible-floor-retains-implicit-ceiling"),
        pytest.param(
            "~=1.4,>=1.5", ">=1.4,>=1.7", "1.5", "1.7", False, id="redundant-floor-cannot-drop-compatible-ceiling"
        ),
        pytest.param("==1.*,>=1.5", "==1.*,>=1.7", "1.5", "1.7", True, id="wildcard-floor-retains-implicit-ceiling"),
        pytest.param(
            "==1.*,>=1.5", ">=1,>=1.7,<3", "1.5", "1.7", False, id="redundant-floor-cannot-widen-wildcard-ceiling"
        ),
        pytest.param(
            ">=1,>=1.5,!=1.6",
            ">=1,>=1.7,!=1.6",
            "1.5",
            "1.7",
            True,
            id="redundant-floor-preserves-published-exclusion",
        ),
        pytest.param(
            ">=1,>=1.5,!=1.8",
            ">=1,>=1.7",
            "1.5",
            "1.7",
            False,
            id="redundant-floor-cannot-remove-published-exclusion",
        ),
        pytest.param(
            ">=1,>=1.5,<3", ">=1,>=2,<3", "1.5", "2", True, id="redundant-floor-preserves-published-upper-bound"
        ),
        pytest.param(
            ">=1,>=1.5,<3", ">=1,>=2,<4", "1.5", "2", False, id="redundant-floor-cannot-widen-published-upper-bound"
        ),
        pytest.param("==1.5,>=1", "==2,>=1", "1.5", "2", True, id="exact-pin-and-redundant-floor-upgrade"),
        pytest.param(
            "==1.5,>=1", "==1.5,>=2", "1.5", "2", False, id="exact-pin-contradicting-strongest-floor-fails-closed"
        ),
        pytest.param("===1.5,>=1", "===2,>=1", "1.5", "2", True, id="arbitrary-pin-and-redundant-floor-upgrade"),
        pytest.param("===1.5,>=1", "===2.0,>=1", "1.5", "2", False, id="arbitrary-pin-retains-raw-lock-identity"),
        pytest.param(
            ">=1,>=1.5", ">=2rc1,>=2", "1.5", "2", False, id="unsupported-redundant-prerelease-floor-fails-closed"
        ),
        pytest.param(">=1,>=1.5", ">=2,>=", "1.5", "2", False, id="malformed-redundant-floor-fails-closed"),
        pytest.param(
            ">=1,>=1.5", ">=2,>=2.0", "1.5", "2", False, id="ambiguous-equivalent-redundant-floor-fails-closed"
        ),
        pytest.param(">=1,>=1.5,<3", ">=1,>=2,<2", "1.5", "2", False, id="contradictory-floor-and-ceiling-fail-closed"),
    ],
)
def test_security_dependency_minimum_uses_strongest_effective_floor(
    tmp_path: Path, scope: str, previous: str, current: str, before: str, after: str, accepted: bool
) -> None:
    base = "danger-pkg" + previous
    head = "danger-pkg" + current
    protected = scope == "protected"
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["safe-direct>=1"] if protected else [base],
        head_requirements=["safe-direct>=1"] if protected else [head],
        base_packages=[("danger-pkg", before), *([("safe-direct", "1")] if protected else [])],
        head_packages=[("danger-pkg", after), *([("safe-direct", "1")] if protected else [])],
        optional=scope == "optional",
        base_constraints=[base] if protected else None,
        head_constraints=[head] if protected else None,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("removed-exclusion", False, id="grouped-update-cannot-remove-runtime-wildcard-exclusion"),
        pytest.param("narrowed-exclusion", False, id="exact-exclusion-cannot-replace-entire-vulnerable-prefix"),
        pytest.param("removed-upper", False, id="grouped-update-cannot-remove-runtime-upper-bound"),
        pytest.param("widened-upper", False, id="grouped-update-cannot-widen-runtime-upper-bound"),
        pytest.param("inclusive-upper", False, id="inclusive-bound-cannot-weaken-exclusive-upper"),
        pytest.param("strengthened-upper", True, id="narrower-upper-bound-preserves-supported-locks"),
        pytest.param("exclusive-upper", True, id="exclusive-upper-may-strengthen-inclusive-bound"),
        pytest.param("canonical-reordered", True, id="canonical-reordered-security-bounds-remain-equivalent"),
        pytest.param("stronger-wildcard", True, id="broader-exclusion-prefix-may-strengthen-security"),
        pytest.param("wildcard-drops-v2", False, id="stronger-wildcard-cannot-drop-supported-v2-lock"),
        pytest.param("exact-to-wildcard", True, id="wildcard-may-strengthen-exact-release-exclusion"),
        pytest.param("post-removed", False, id="unchanged-lock-must-retain-exact-stable-post-exclusion"),
        pytest.param("post-covered", True, id="release-prefix-may-strengthen-stable-post-exclusion"),
        pytest.param("floor-covers-exact", True, id="stronger-floor-may-imply-prior-exact-exclusion"),
        pytest.param("upper-covers-wildcard", True, id="stronger-upper-may-imply-prior-prefix-exclusion"),
        pytest.param("wrong-epoch", False, id="other-epoch-prefix-does-not-preserve-existing-exclusion"),
        pytest.param("epoch-canonical", True, id="canonical-same-epoch-prefix-preserves-existing-exclusion"),
        pytest.param("marker-preserved", True, id="unchanged-marker-retains-runtime-security-bounds"),
        pytest.param("marker-moved", False, id="security-bounds-cannot-move-to-different-marker-context"),
        pytest.param("optional-removed", False, id="grouped-update-cannot-remove-optional-security-exclusion"),
        pytest.param("optional-preserved", True, id="optional-security-context-and-bounds-remain-supported"),
        pytest.param("unaffected-v1-dropped", False, id="security-bounds-cannot-drop-supported-unchanged-v1"),
        pytest.param("unaffected-v2-dropped", False, id="security-bounds-cannot-drop-supported-unchanged-v2"),
        pytest.param("malformed-exclusion", False, id="ambiguous-unchanged-lock-exclusion-fails-closed"),
        pytest.param("no-old-security-bounds", True, id="unbounded-unchanged-dependency-still-accepts-new-floor"),
    ],
)
def test_grouped_security_updates_preserve_unchanged_published_bounds(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    previous = "pydantic>=1,<3,!=2.12.5.*"
    current = previous
    v1, v2 = "1.10.26", "2.12.6"
    optional = variant.startswith("optional-")

    if variant in {"removed-exclusion", "optional-removed"}:
        current = "pydantic>=1,<3"
    elif variant == "narrowed-exclusion":
        current = "pydantic>=1,<3,!=2.12.5"
    elif variant == "removed-upper":
        current = "pydantic>=1,!=2.12.5.*"
    elif variant == "widened-upper":
        current = "pydantic>=1,<4,!=2.12.5.*"
    elif variant == "inclusive-upper":
        current = "pydantic>=1,<=3,!=2.12.5.*"
    elif variant == "strengthened-upper":
        current = "pydantic>=1,<2.13,!=2.12.5.*"
    elif variant == "exclusive-upper":
        previous = "pydantic>=1,<=3,!=2.12.5.*"
        current = "pydantic>=1,<3,!=2.12.5.*"
    elif variant == "canonical-reordered":
        current = "pydantic!=0!2.12.5.*,<3.0,>=1.0.0"
    elif variant in {"stronger-wildcard", "wildcard-drops-v2"}:
        current = "pydantic>=1,<3,!=2.12.*"
        if variant == "stronger-wildcard":
            v2 = "2.13.0"
    elif variant == "exact-to-wildcard":
        previous = "pydantic>=1,<3,!=2.12.5"
    elif variant in {"post-removed", "post-covered"}:
        previous = "pydantic>=1,<3,!=2.12.5.post1"
        current = "pydantic>=1,<3" if variant == "post-removed" else "pydantic>=1,<3,!=2.12.5.*"
    elif variant == "floor-covers-exact":
        previous = "pydantic>=1,<3,!=1.10.25"
        current = "pydantic>=1.10.26,<3"
    elif variant == "upper-covers-wildcard":
        current = "pydantic>=1,<2.12.5"
        v2 = "2.11.0"
    elif variant in {"wrong-epoch", "epoch-canonical"}:
        previous = "pydantic>=1!1,<1!3,!=1!2.12.5.*"
        current = (
            "pydantic>=1!1,<1!3,!=0!2.12.5.*" if variant == "wrong-epoch" else "pydantic>=1!1,<1!3.0,!=01!02.012.005.*"
        )
        v1, v2 = "1!1.10.26", "1!2.12.6"
    elif variant in {"marker-preserved", "marker-moved"}:
        previous += "; python_version >= '3.11'"
        current += "; python_version >= '3.12'" if variant == "marker-moved" else "; python_version >= '3.11'"
    elif variant == "unaffected-v1-dropped":
        current += ",!=1.10.26.*"
    elif variant == "unaffected-v2-dropped":
        current += ",!=2.12.6.*"
    elif variant == "malformed-exclusion":
        current = "pydantic>=1,<3,!=2.12.5.post1.*"
    elif variant == "no-old-security-bounds":
        previous, current = "pydantic", "pydantic>=1"

    base_requirements = ["danger-pkg>=1"]
    head_requirements = ["danger-pkg>=2"]
    base_optional_groups = {"feature": [previous]} if optional else None
    head_optional_groups = {"feature": [current]} if optional else None
    if not optional:
        base_requirements.append(previous)
        head_requirements.append(current)
    unchanged = [("pydantic", v1), ("pydantic", v2)]
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=[("danger-pkg", "1"), *unchanged],
        head_packages=[("danger-pkg", "2"), *unchanged],
        base_optional_groups=base_optional_groups,
        head_optional_groups=head_optional_groups,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("specifier", "locked"),
    [
        pytest.param(">=1.0a1", "1.0", id="unchanged-alpha-lower-bound"),
        pytest.param(">=1.0b2", "1.0", id="unchanged-beta-lower-bound"),
        pytest.param(">=1.0rc1", "1.0", id="unchanged-release-candidate-lower-bound"),
        pytest.param(">=1.0.dev1", "1.0", id="unchanged-development-lower-bound"),
        pytest.param(">=1.0rc1.post2.dev3", "1.0", id="unchanged-combined-prerelease-post-development-bound"),
        pytest.param("<2.0rc1", "1.0", id="unchanged-prerelease-upper-bound"),
        pytest.param("!=1.0rc1", "1.0", id="unchanged-prerelease-exclusion"),
        pytest.param("~=1.0rc1", "1.0", id="unchanged-compatible-prerelease-bound"),
        pytest.param("==1.0rc1", "1.0rc1", id="unchanged-exact-prerelease-pin"),
        pytest.param("===1.0rc1", "1.0rc1", id="unchanged-arbitrary-prerelease-pin"),
        pytest.param("==1.0+linux", "1.0+linux", id="unchanged-local-version-pin"),
        pytest.param(">=1!1.0rc1", "1!1.0", id="unchanged-epoch-prerelease-bound"),
    ],
)
@pytest.mark.parametrize("scope", ["runtime", "optional", "constraint", "build", "group"])
def test_grouped_security_updates_preserve_unchanged_pep440_prerelease_requirements(
    tmp_path: Path, specifier: str, locked: str, scope: str
) -> None:
    requirement = "beta" + specifier
    assert Requirement(requirement).specifier.contains(locked, prereleases=True)
    base_requirements = ["patch>=1"]
    head_requirements = ["patch>=2"]
    if scope == "runtime":
        base_requirements.append(requirement)
        head_requirements.append(requirement)
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=[("patch", "1"), ("beta", locked)],
        head_packages=[("patch", "2"), ("beta", locked)],
        base_optional_groups={"feature": [requirement]} if scope == "optional" else None,
        head_optional_groups={"feature": [requirement]} if scope == "optional" else None,
        base_constraints=[requirement] if scope == "constraint" else None,
        head_constraints=[requirement] if scope == "constraint" else None,
        base_build_constraints=[requirement] if scope == "build" else None,
        head_build_constraints=[requirement] if scope == "build" else None,
        base_dependency_groups={"development": [requirement]} if scope == "group" else None,
        head_dependency_groups={"development": [requirement]} if scope == "group" else None,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("scope", ["runtime", "optional", "constraint", "build", "group"])
@pytest.mark.parametrize(
    ("previous", "current"),
    [
        pytest.param("beta>=1.0rc1", "beta>=1", id="changed-prerelease-floor-is-not-silently-reinterpreted"),
        pytest.param("beta>=1.0.dev1", "beta>=1", id="changed-development-floor-is-not-silently-reinterpreted"),
        pytest.param("beta<2.0rc1", "beta<3", id="changed-prerelease-ceiling-is-not-silently-reinterpreted"),
        pytest.param("beta!=1.0rc1", "beta", id="removed-prerelease-exclusion-is-not-silently-reinterpreted"),
    ],
)
def test_grouped_security_updates_do_not_bypass_changed_prerelease_requirements(
    tmp_path: Path, previous: str, current: str, scope: str
) -> None:
    Requirement(previous)
    Requirement(current)
    base_requirements = ["patch>=1"]
    head_requirements = ["patch>=2"]
    if scope == "runtime":
        base_requirements.append(previous)
        head_requirements.append(current)
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=[("patch", "1"), ("beta", "1.5")],
        head_packages=[("patch", "2"), ("beta", "1.5")],
        base_optional_groups={"feature": [previous]} if scope == "optional" else None,
        head_optional_groups={"feature": [current]} if scope == "optional" else None,
        base_constraints=[previous] if scope == "constraint" else None,
        head_constraints=[current] if scope == "constraint" else None,
        base_build_constraints=[previous] if scope == "build" else None,
        head_build_constraints=[current] if scope == "build" else None,
        base_dependency_groups={"development": [previous]} if scope == "group" else None,
        head_dependency_groups={"development": [current]} if scope == "group" else None,
    )
    assert result.returncode == 1, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("constraint-exclusion", False, id="unchanged-uv-constraint-cannot-lose-exact-exclusion"),
        pytest.param("constraint-wildcard", False, id="unchanged-uv-constraint-cannot-lose-prefix-exclusion"),
        pytest.param("constraint-upper", False, id="unchanged-uv-constraint-cannot-widen-upper-bound"),
        pytest.param("build-exclusion", False, id="unchanged-build-constraint-cannot-lose-security-exclusion"),
        pytest.param("build-wildcard", False, id="unchanged-build-constraint-cannot-lose-prefix-exclusion"),
        pytest.param("group-exclusion", False, id="unchanged-dependency-group-cannot-lose-security-exclusion"),
        pytest.param("group-wildcard", False, id="unchanged-dependency-group-cannot-lose-prefix-exclusion"),
        pytest.param("group-no-floor", False, id="protected-exclusion-is-checked-before-no-minimum-skip"),
        pytest.param("changed-lock-exclusion", False, id="protected-patch-cannot-erase-other-security-exclusion"),
        pytest.param("post-removed", False, id="protected-stable-post-exclusion-remains-immutable"),
        pytest.param("wrong-epoch", False, id="protected-exclusion-cannot-move-to-different-epoch"),
        pytest.param("marker-exclusion", False, id="protected-marker-context-retains-existing-exclusion"),
        pytest.param("marker-moved", False, id="protected-exclusion-cannot-move-marker-context"),
        pytest.param("drops-supported-lock", False, id="stronger-protected-bound-cannot-drop-current-locked-line"),
        pytest.param("stronger-exclusion", True, id="protected-prefix-may-strengthen-exact-exclusion"),
        pytest.param("stronger-upper", True, id="protected-upper-may-strengthen-without-dropping-lock"),
        pytest.param("canonical-order", True, id="canonical-reordered-protected-bounds-remain-equivalent"),
        pytest.param("build-pin-upgrade", True, id="immutable-exact-build-pins-may-take-reviewed-security-patch"),
        pytest.param("unbounded-group", True, id="unchanged-unbounded-development-group-remains-supported"),
    ],
)
def test_grouped_security_updates_preserve_all_protected_dependency_bounds(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    previous = "danger>=1,<3,!=1.5"
    current = "danger>=1,<3"
    before, after = "2", "2"
    scope = "constraint"

    if variant in {"constraint-wildcard", "build-wildcard", "group-wildcard"}:
        previous = "danger>=1,<3,!=1.5.*"
    elif variant == "constraint-upper":
        current = "danger>=1,<4,!=1.5"
    elif variant == "group-no-floor":
        previous, current = "danger<3,!=1.5", "danger<3"
    elif variant == "changed-lock-exclusion":
        previous = "danger>=1,<3,!=2.5"
        current = "danger>=1.6,<3"
        before, after = "1.4", "1.6"
    elif variant == "post-removed":
        previous = "danger>=1,<3,!=1.5.post2"
    elif variant == "wrong-epoch":
        previous = "danger>=1!1,<1!3,!=1!1.5.*"
        current = "danger>=1!1,<1!3,!=0!1.5.*"
        before = after = "1!2"
    elif variant in {"marker-exclusion", "marker-moved"}:
        previous += "; python_version >= '3.11'"
        current += "; python_version >= '3.12'" if variant == "marker-moved" else "; python_version >= '3.11'"
    elif variant == "drops-supported-lock":
        current = "danger>=1,<2,!=1.5"
    elif variant == "stronger-exclusion":
        current = "danger>=1,<3,!=1.5.*"
    elif variant == "stronger-upper":
        current = "danger>=1,<2.5,!=1.5"
    elif variant == "canonical-order":
        current = "danger!=0!1.5,<3.0,>=1.0"
    elif variant == "build-pin-upgrade":
        previous, current = "danger==1.5", "danger==1.6"
        before, after = "1.5", "1.6"
    elif variant == "unbounded-group":
        previous = current = "danger"

    if variant.startswith("build-"):
        scope = "build"
    elif variant.startswith("group-") or variant == "unbounded-group":
        scope = "group"

    base_constraints = [previous] if scope == "constraint" else None
    head_constraints = [current] if scope == "constraint" else None
    base_build = [previous] if scope == "build" else None
    head_build = [current] if scope == "build" else None
    base_groups = {"reviewed": [previous]} if scope == "group" else None
    head_groups = {"reviewed": [current]} if scope == "group" else None
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1"],
        head_requirements=["patch-me>=1.1"],
        base_packages=[("patch-me", "1"), ("danger", before)],
        head_packages=[("patch-me", "1.1"), ("danger", after)],
        base_constraints=base_constraints,
        head_constraints=head_constraints,
        base_build_constraints=base_build,
        head_build_constraints=head_build,
        base_dependency_groups=base_groups,
        head_dependency_groups=head_groups,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("runtime-wildcard", False, id="patched-runtime-lock-cannot-remove-prior-prefix-exclusion"),
        pytest.param("runtime-exact", False, id="patched-runtime-lock-cannot-remove-prior-exact-exclusion"),
        pytest.param("runtime-post", False, id="patched-runtime-lock-cannot-remove-stable-post-exclusion"),
        pytest.param("runtime-upper", False, id="patched-runtime-lock-cannot-widen-existing-upper-bound"),
        pytest.param("optional-wildcard", False, id="patched-optional-lock-cannot-remove-prior-prefix-exclusion"),
        pytest.param("optional-upper", False, id="patched-optional-lock-cannot-remove-existing-upper-bound"),
        pytest.param("epoch-wrong", False, id="patched-lock-cannot-move-exclusion-into-another-epoch"),
        pytest.param("marker-exclusion", False, id="patched-marker-context-cannot-drop-security-exclusion"),
        pytest.param("marker-moved", False, id="patched-security-exclusion-cannot-move-marker-context"),
        pytest.param("malformed-exclusion", False, id="patched-lock-security-exclusion-must-remain-unambiguous"),
        pytest.param("preserved-wildcard", True, id="patched-lock-preserves-existing-prefix-exclusion"),
        pytest.param("stronger-wildcard", True, id="patched-lock-may-strengthen-exact-into-prefix-exclusion"),
        pytest.param("stronger-upper", True, id="patched-lock-may-strengthen-upper-without-dropping-support"),
        pytest.param("canonical-order", True, id="patched-lock-preserves-canonical-reordered-security-bounds"),
        pytest.param("floor-implies-exclusion", True, id="patched-floor-may-safely-imply-prior-exact-exclusion"),
        pytest.param("optional-preserved", True, id="patched-optional-context-preserves-existing-security-bounds"),
    ],
)
def test_patched_locks_preserve_existing_published_security_bounds(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    previous = "danger>=1,<3,!=2.0.*"
    current = "danger>=1.1,<3"
    before, after = "1", "1.1"
    optional = variant.startswith("optional-")

    if variant in {"runtime-exact", "runtime-post"}:
        previous = "danger>=1,<3,!=2.0.post1" if variant == "runtime-post" else "danger>=1,<3,!=2.0"
    elif variant in {"runtime-upper", "optional-upper"}:
        current = "danger>=1.1,<4,!=2.0.*"
    elif variant == "epoch-wrong":
        previous = "danger>=1!1,<1!3,!=1!2.0.*"
        current = "danger>=1!1.1,<1!3,!=0!2.0.*"
        before, after = "1!1", "1!1.1"
    elif variant in {"marker-exclusion", "marker-moved"}:
        previous += "; python_version >= '3.11'"
        current += "; python_version >= '3.12'" if variant == "marker-moved" else "; python_version >= '3.11'"
    elif variant == "malformed-exclusion":
        current += ",!=2.0.post1.*"
    elif variant in {"preserved-wildcard", "optional-preserved"}:
        current += ",!=2.0.*"
    elif variant == "stronger-wildcard":
        previous = "danger>=1,<3,!=2.0"
        current += ",!=2.0.*"
    elif variant == "stronger-upper":
        current = "danger>=1.1,<2,!=2.0.*"
    elif variant == "canonical-order":
        current = "danger!=0!2.0.*,<3.0,>=1.1.0"
    elif variant == "floor-implies-exclusion":
        previous = "danger>=0,<3,!=0.5"

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[previous],
        head_requirements=[current],
        base_packages=[("danger", before)],
        head_packages=[("danger", after)],
        optional=optional,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("runtime-lower", False, id="unchanged-runtime-exact-pin-cannot-widen-to-floor"),
        pytest.param("runtime-upper", False, id="unchanged-runtime-exact-pin-cannot-widen-to-ceiling"),
        pytest.param("runtime-range", False, id="unchanged-runtime-exact-pin-cannot-widen-to-range"),
        pytest.param("runtime-removed", False, id="unchanged-runtime-exact-pin-cannot-be-removed"),
        pytest.param("runtime-replaced", False, id="unchanged-runtime-lock-cannot-swap-exact-pin"),
        pytest.param("optional-lower", False, id="unchanged-optional-exact-pin-cannot-widen"),
        pytest.param("constraint-lower", False, id="unchanged-uv-exact-pin-cannot-widen"),
        pytest.param("build-lower", False, id="unchanged-build-exact-pin-cannot-widen"),
        pytest.param("group-lower", False, id="unchanged-development-exact-pin-cannot-widen"),
        pytest.param("marker-lower", False, id="unchanged-marker-scoped-exact-pin-cannot-widen"),
        pytest.param("epoch-lower", False, id="unchanged-epoch-exact-pin-cannot-widen"),
        pytest.param("post-lower", False, id="unchanged-stable-post-exact-pin-cannot-widen"),
        pytest.param("upgrade-widen", False, id="patched-release-cannot-replace-exact-pin-with-range"),
        pytest.param("upgrade-wrong-pin", False, id="patched-release-must-match-replacement-exact-pin"),
        pytest.param("upgrade-retained-old", False, id="replacement-pin-cannot-leave-original-release-live"),
        pytest.param("upgrade-ambiguous", False, id="replacement-pin-requires-one-for-one-locked-upgrade"),
        pytest.param("upgrade-downgrade", False, id="replacement-pin-cannot-follow-a-downgraded-release"),
        pytest.param("exact-preserved", True, id="unchanged-original-exact-pin-remains-supported"),
        pytest.param("canonical-preserved", True, id="canonical-equivalent-exact-pin-remains-supported"),
        pytest.param("redundant-preserved", True, id="exact-pin-with-redundant-safe-bounds-remains-supported"),
        pytest.param("runtime-upgrade", True, id="published-exact-pin-may-track-real-security-upgrade"),
        pytest.param("optional-upgrade", True, id="optional-exact-pin-may-track-real-security-upgrade"),
        pytest.param("constraint-upgrade", True, id="uv-exact-pin-may-track-real-security-upgrade"),
        pytest.param("build-upgrade", True, id="reviewed-build-exact-pin-may-track-real-security-upgrade"),
        pytest.param("group-upgrade", True, id="development-exact-pin-may-track-real-security-upgrade"),
        pytest.param("epoch-upgrade", True, id="epoch-exact-pin-may-track-matching-security-upgrade"),
        pytest.param("post-upgrade", True, id="stable-post-exact-pin-may-track-matching-security-upgrade"),
        pytest.param("marker-upgrade", True, id="contextual-exact-pin-may-track-matching-security-upgrade"),
    ],
)
def test_grouped_security_updates_preserve_exact_dependency_pins(tmp_path: Path, variant: str, accepted: bool) -> None:
    previous, current = "danger==1", "danger>=1"
    before, after = ["1"], ["1"]
    optional = variant.startswith("optional-")
    constraints: tuple[list[str], list[str]] | None = None
    build: tuple[list[str], list[str]] | None = None
    groups: tuple[dict[str, list[str]], dict[str, list[str]]] | None = None

    if variant == "runtime-upper":
        current = "danger<=1"
    elif variant == "runtime-range":
        current = "danger>=1,<2"
    elif variant == "runtime-removed":
        current = "danger"
    elif variant == "runtime-replaced":
        current = "danger==2"
    elif variant == "constraint-lower":
        constraints = ([previous], [current])
    elif variant == "build-lower":
        build = ([previous], [current])
    elif variant == "group-lower":
        groups = ({"reviewed": [previous]}, {"reviewed": [current]})
    elif variant in {"marker-lower", "marker-upgrade"}:
        previous += "; python_version >= '3.11'"
        if variant == "marker-upgrade":
            current = "danger==2; python_version >= '3.11'"
            after = ["2"]
        else:
            current += "; python_version >= '3.11'"
    elif variant in {"epoch-lower", "epoch-upgrade"}:
        previous = "danger==1!1"
        before = ["1!1"]
        if variant == "epoch-upgrade":
            current, after = "danger==1!2", ["1!2"]
        else:
            current, after = "danger>=1!1", ["1!1"]
    elif variant in {"post-lower", "post-upgrade"}:
        previous = "danger==1.post1"
        before = ["1.post1"]
        if variant == "post-upgrade":
            current, after = "danger==1.post2", ["1.post2"]
        else:
            current, after = "danger>=1.post1", ["1.post1"]
    elif variant == "upgrade-widen":
        current, after = "danger>=2", ["2"]
    elif variant == "upgrade-wrong-pin":
        current, after = "danger==3", ["2"]
    elif variant == "upgrade-retained-old":
        current, after = "danger==2", ["1", "2"]
    elif variant == "upgrade-ambiguous":
        current, after = "danger==2", ["2", "3"]
    elif variant == "upgrade-downgrade":
        previous, current, before, after = "danger==2", "danger==1", ["2"], ["1"]
    elif variant == "exact-preserved":
        current = previous
    elif variant == "canonical-preserved":
        previous, current = "danger==1.0", "danger==1"
    elif variant == "redundant-preserved":
        current = "danger==1,>=1"
    elif variant.endswith("-upgrade"):
        current, after = "danger==2", ["2"]
        if variant == "constraint-upgrade":
            constraints = ([previous], [current])
        elif variant == "build-upgrade":
            build = ([previous], [current])
        elif variant == "group-upgrade":
            groups = ({"reviewed": [previous]}, {"reviewed": [current]})

    protected = constraints is not None or build is not None or groups is not None
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1"] + ([] if protected else [previous]),
        head_requirements=["patch-me>=1.1"] + ([] if protected else [current]),
        base_packages=[("patch-me", "1"), *[("danger", version) for version in before]],
        head_packages=[("patch-me", "1.1"), *[("danger", version) for version in after]],
        optional=optional,
        base_constraints=None if constraints is None else constraints[0],
        head_constraints=None if constraints is None else constraints[1],
        base_build_constraints=None if build is None else build[0],
        head_build_constraints=None if build is None else build[1],
        base_dependency_groups=None if groups is None else groups[0],
        head_dependency_groups=None if groups is None else groups[1],
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("runtime-inclusive", False, id="strict-published-runtime-floor-cannot-become-inclusive"),
        pytest.param("optional-inclusive", False, id="strict-optional-floor-cannot-become-inclusive"),
        pytest.param("constraint-inclusive", False, id="strict-uv-constraint-cannot-become-inclusive"),
        pytest.param("build-inclusive", False, id="strict-build-constraint-cannot-become-inclusive"),
        pytest.param("group-inclusive", False, id="strict-development-floor-cannot-become-inclusive"),
        pytest.param("strict-lowered", False, id="strict-lower-version-cannot-weaken"),
        pytest.param("strict-dropped", False, id="strict-floor-cannot-disappear"),
        pytest.param("epoch-inclusive", False, id="strict-epoch-floor-cannot-become-inclusive"),
        pytest.param("post-inclusive", False, id="strict-post-release-floor-cannot-become-inclusive"),
        pytest.param("runtime-final-post", False, id="exclusive-final-runtime-floor-cannot-admit-same-release-post"),
        pytest.param("optional-final-post", False, id="exclusive-final-optional-floor-cannot-admit-same-release-post"),
        pytest.param("constraint-final-post", False, id="exclusive-final-constraint-cannot-admit-same-release-post"),
        pytest.param("build-final-post", False, id="exclusive-final-build-floor-cannot-admit-same-release-post"),
        pytest.param("group-final-post", False, id="exclusive-final-group-floor-cannot-admit-same-release-post"),
        pytest.param("final-exclusive-post", False, id="exclusive-final-floor-cannot-admit-later-post-releases"),
        pytest.param("epoch-final-post", False, id="exclusive-epoch-final-floor-cannot-admit-same-release-post"),
        pytest.param("zero-final-post", False, id="exclusive-zero-normalized-final-floor-cannot-admit-post-release"),
        pytest.param("marker-inclusive", False, id="strict-contextual-floor-cannot-become-inclusive"),
        pytest.param("strict-preserved", True, id="unchanged-strict-floor-remains-supported"),
        pytest.param("strict-raised", True, id="strict-floor-may-increase"),
        pytest.param("inclusive-higher", True, id="higher-inclusive-floor-may-replace-strict-floor"),
        pytest.param("inclusive-to-strict", True, id="inclusive-floor-may-strengthen-to-strict"),
        pytest.param("canonical-strict", True, id="canonical-equivalent-strict-floor-remains-supported"),
        pytest.param("post-exclusive-higher", True, id="exclusive-post-floor-may-increase-within-same-release"),
        pytest.param("post-inclusive-higher", True, id="inclusive-later-post-may-strengthen-exclusive-post-floor"),
    ],
)
def test_grouped_security_updates_preserve_strict_dependency_floors(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    previous, current = "danger>1", "danger>=1"
    locked = "2"
    optional = variant in {"optional-inclusive", "optional-final-post"}
    constraints: tuple[list[str], list[str]] | None = None
    build: tuple[list[str], list[str]] | None = None
    groups: tuple[dict[str, list[str]], dict[str, list[str]]] | None = None

    if variant in {
        "runtime-final-post",
        "optional-final-post",
        "constraint-final-post",
        "build-final-post",
        "group-final-post",
    }:
        previous, current = "danger>1.0", "danger>=1.0.post1"
        if variant == "constraint-final-post":
            constraints = ([previous], [current])
        elif variant == "build-final-post":
            build = ([previous], [current])
        elif variant == "group-final-post":
            groups = ({"reviewed": [previous]}, {"reviewed": [current]})
    elif variant == "final-exclusive-post":
        previous, current = "danger>1.0", "danger>1.0.post1"
    elif variant == "epoch-final-post":
        previous, current, locked = "danger>1!1.0", "danger>=1!1.0.post1", "1!2"
    elif variant == "zero-final-post":
        previous, current = "danger>1.0.0", "danger>=1.0.post1"
    elif variant == "post-exclusive-higher":
        previous, current, locked = "danger>1.0.post1", "danger>1.0.post2", "1.0.post3"
    elif variant == "post-inclusive-higher":
        previous, current, locked = "danger>1.0.post1", "danger>=1.0.post2", "1.0.post2"
    elif variant == "constraint-inclusive":
        constraints = ([previous], [current])
    elif variant == "build-inclusive":
        build = ([previous], [current])
    elif variant == "group-inclusive":
        groups = ({"reviewed": [previous]}, {"reviewed": [current]})
    elif variant == "strict-lowered":
        previous, current, locked = "danger>2", "danger>1", "3"
    elif variant == "strict-dropped":
        current = "danger"
    elif variant == "epoch-inclusive":
        previous, current, locked = "danger>1!1", "danger>=1!1", "1!2"
    elif variant == "post-inclusive":
        previous, current, locked = "danger>1.post2", "danger>=1.post2", "1.post3"
    elif variant == "marker-inclusive":
        previous += "; python_version >= '3.11'"
        current += "; python_version >= '3.11'"
    elif variant == "strict-preserved":
        current = previous
    elif variant == "strict-raised":
        current = "danger>1.5"
    elif variant == "inclusive-higher":
        current = "danger>=1.5"
    elif variant == "inclusive-to-strict":
        previous, current = "danger>=1", "danger>1"
    elif variant == "canonical-strict":
        previous, current = "danger>1.0", "danger>1"

    protected = constraints is not None or build is not None or groups is not None
    base_requirements = ["patch-me>=1"] + ([] if protected else [previous])
    head_requirements = ["patch-me>=1.1"] + ([] if protected else [current])
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=[("patch-me", "1"), ("danger", locked)],
        head_packages=[("patch-me", "1.1"), ("danger", locked)],
        optional=optional,
        base_constraints=None if constraints is None else constraints[0],
        head_constraints=None if constraints is None else constraints[1],
        base_build_constraints=None if build is None else build[0],
        head_build_constraints=None if build is None else build[1],
        base_dependency_groups=None if groups is None else groups[0],
        head_dependency_groups=None if groups is None else groups[1],
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("previous", "current", "locked", "accepted"),
    [
        pytest.param(
            "danger>=1,<2",
            "danger>1,<2",
            "1.post1",
            False,
            id="exclusive-final-floor-cannot-drop-retained-post-release",
        ),
        pytest.param(
            "danger>=1.0,<2",
            "danger>1.0.0,<2",
            "1.0.post2",
            False,
            id="canonical-exclusive-final-floor-cannot-drop-retained-post-release",
        ),
        pytest.param(
            "danger>=1!1,<1!2",
            "danger>1!1,<1!2",
            "1!1.post1",
            False,
            id="exclusive-epoch-final-floor-cannot-drop-retained-post-release",
        ),
        pytest.param(
            "danger>=1.post1,<2",
            "danger>1.post1,<2",
            "1.post2",
            True,
            id="exclusive-post-floor-retains-later-same-release-post",
        ),
        pytest.param(
            "danger>=1,<2",
            "danger>1,<2",
            "1.1",
            True,
            id="exclusive-final-floor-retains-later-base-release",
        ),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_exclusive_final_dependency_floors_preserve_retained_post_releases(
    tmp_path: Path, previous: str, current: str, locked: str, accepted: bool, protected: bool
) -> None:
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1"] + ([] if protected else [previous]),
        head_requirements=["patch-me>=1.1"] + ([] if protected else [current]),
        base_packages=[("patch-me", "1"), ("danger", locked)],
        head_packages=[("patch-me", "1.1"), ("danger", locked)],
        base_constraints=[previous] if protected else None,
        head_constraints=[current] if protected else None,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("pydantic-v2", True, id="published-v1-support-survives-protected-v2-patch"),
        pytest.param("pydantic-v1", True, id="published-v2-support-survives-protected-v1-patch"),
        pytest.param("unchanged-published", False, id="private-v2-floor-cannot-leave-published-range-vulnerable"),
        pytest.param("unchanged-published-v1", False, id="private-v1-floor-cannot-leave-published-range-vulnerable"),
        pytest.param("missing-earlier-minor", False, id="published-range-must-exclude-entire-affected-major"),
        pytest.param("missing-earlier-patch", False, id="published-range-must-exclude-earlier-minor-patches"),
        pytest.param("exact-old-only", False, id="excluding-only-old-lock-does-not-protect-whole-branch"),
        pytest.param("removed-still-accepted", False, id="published-range-must-exclude-removed-lock"),
        pytest.param("patched-excluded", False, id="published-range-must-accept-patched-lock"),
        pytest.param("unaffected-excluded", False, id="published-range-must-preserve-unaffected-major"),
        pytest.param("dropped-original-exclusion", False, id="published-original-exclusions-cannot-be-weakened"),
        pytest.param("marked-published", True, id="published-exclusions-preserve-original-marker"),
        pytest.param("moved-published-marker", False, id="published-exclusions-cannot-move-original-marker"),
        pytest.param("epoch-patched", True, id="published-exclusions-match-security-release-epoch"),
        pytest.param("wrong-epoch", False, id="other-epoch-exclusions-do-not-secure-published-branch"),
        pytest.param("post-patched", True, id="published-exclusions-cover-earlier-stable-post-releases"),
        pytest.param("post-missing-intermediate", False, id="published-exclusions-cannot-skip-earlier-post"),
        pytest.param("post-wildcard", False, id="published-post-wildcard-cannot-exclude-patched-release"),
        pytest.param("unsupported-wildcard", False, id="ambiguous-published-exclusions-fail-closed"),
        pytest.param("unbounded-expansion", False, id="published-branch-proof-has-bounded-expansion"),
        pytest.param("unchanged-protected-floor", False, id="unchanged-v2-protected-floor-rejected"),
        pytest.param("below-patched-release", False, id="protected-v2-floor-must-reach-lock-patch"),
        pytest.param("unbounded-branch", False, id="protected-branch-must-retain-upper-bound"),
        pytest.param("weakened-unaffected-floor", False, id="unaffected-v1-security-floor-cannot-drop"),
        pytest.param("removed-unaffected-group", False, id="supported-v1-protected-context-cannot-disappear"),
        pytest.param("removed-unaffected-lock", False, id="supported-v1-locked-branch-cannot-disappear"),
        pytest.param("new-protected-context", False, id="protected-v2-context-must-exist-in-immutable-base"),
    ],
)
def test_security_updates_preserve_independent_supported_major_branches(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    old_exclusions = [f"!=2.{minor}.*" for minor in range(4)]
    published = "pydantic>=1.10.13,<3," + ",".join(old_exclusions)
    v2_exclusions = [f"!=2.{minor}.*" for minor in range(4, 12)] + [f"!=2.12.{patch}.*" for patch in range(6)]
    head_published = published + "," + ",".join(v2_exclusions)
    base_groups = {
        "pydantic-v1": ["pydantic>=1.10.26,<2"],
        "pydantic-v2": ["pydantic>=2,<3"],
    }
    head_groups = {
        "pydantic-v1": ["pydantic>=1.10.26,<2"],
        "pydantic-v2": ["pydantic>=2.12.6,<3"],
    }
    base_packages = [("pydantic", "1.10.26"), ("pydantic", "2.12.5")]
    head_packages = [("pydantic", "1.10.26"), ("pydantic", "2.12.6")]

    if variant in {"pydantic-v1", "unchanged-published-v1"}:
        head_groups["pydantic-v1"] = ["pydantic>=1.10.27,<2"]
        head_groups["pydantic-v2"] = ["pydantic>=2,<3"]
        head_packages = [("pydantic", "1.10.27"), ("pydantic", "2.12.5")]
        head_published = published + "," + ",".join(f"!=1.10.{patch}.*" for patch in range(13, 27))
        if variant == "unchanged-published-v1":
            head_published = published
    elif variant == "unchanged-published":
        head_published = published
    elif variant == "missing-earlier-minor":
        head_published = head_published.replace(",!=2.11.*", "")
    elif variant == "missing-earlier-patch":
        head_published = head_published.replace(",!=2.12.4.*", "")
    elif variant == "exact-old-only":
        head_published = published + ",!=2.12.5"
    elif variant == "removed-still-accepted":
        head_published = head_published.replace(",!=2.12.5.*", "")
    elif variant == "patched-excluded":
        head_published += ",!=2.12.6.*"
    elif variant == "unaffected-excluded":
        head_published += ",!=1.10.26.*"
    elif variant == "dropped-original-exclusion":
        head_published = head_published.replace(",!=2.0.*", "")
    elif variant in {"marked-published", "moved-published-marker"}:
        published += "; python_version >= '3.10'"
        head_published += (
            "; python_version >= '3.11'" if variant == "moved-published-marker" else "; python_version >= '3.10'"
        )
    elif variant in {"epoch-patched", "wrong-epoch"}:
        existing = [f"!=1!2.{minor}.*" for minor in range(4)]
        remaining = [f"!=1!2.{minor}.*" for minor in range(4, 12)] + [f"!=1!2.12.{patch}.*" for patch in range(6)]
        published = "pydantic>=1!1.10.13,<1!3," + ",".join(existing)
        head_published = published + "," + ",".join(remaining)
        if variant == "wrong-epoch":
            head_published = published + "," + ",".join(value.replace("1!", "0!") for value in remaining)
        base_groups = {
            "pydantic-v1": ["pydantic>=1!1.10.26,<1!2"],
            "pydantic-v2": ["pydantic>=1!2,<1!3"],
        }
        head_groups = {
            "pydantic-v1": ["pydantic>=1!1.10.26,<1!2"],
            "pydantic-v2": ["pydantic>=1!2.12.6,<1!3"],
        }
        base_packages = [("pydantic", "1!1.10.26"), ("pydantic", "1!2.12.5")]
        head_packages = [("pydantic", "1!1.10.26"), ("pydantic", "1!2.12.6")]
    elif variant in {"post-patched", "post-missing-intermediate", "post-wildcard"}:
        head_groups["pydantic-v2"] = ["pydantic>=2.12.5.post3,<3"]
        base_packages = [("pydantic", "1.10.26"), ("pydantic", "2.12.5.post1")]
        head_packages = [("pydantic", "1.10.26"), ("pydantic", "2.12.5.post3")]
        lower = [f"!=2.{minor}.*" for minor in range(4, 12)]
        lower += [f"!=2.12.{patch}.*" for patch in range(5)]
        lower += ["!=2.12.5", "!=2.12.5.post0", "!=2.12.5.post1", "!=2.12.5.post2"]
        head_published = published + "," + ",".join(lower)
        if variant == "post-missing-intermediate":
            head_published = head_published.replace(",!=2.12.5.post2", "")
        elif variant == "post-wildcard":
            head_published += ",!=2.12.5.*"
    elif variant == "unsupported-wildcard":
        head_published += ",!=2.12.5.post1.*"
    elif variant == "unbounded-expansion":
        head_groups["pydantic-v2"] = ["pydantic>=2.513.1,<3"]
        base_packages = [("pydantic", "1.10.26"), ("pydantic", "2.513.0")]
        head_packages = [("pydantic", "1.10.26"), ("pydantic", "2.513.1")]
    elif variant == "unchanged-protected-floor":
        head_groups["pydantic-v2"] = ["pydantic>=2,<3"]
    elif variant == "below-patched-release":
        head_groups["pydantic-v2"] = ["pydantic>=2.12.5,<3"]
    elif variant == "unbounded-branch":
        head_groups["pydantic-v2"] = ["pydantic>=2.12.6"]
    elif variant == "weakened-unaffected-floor":
        head_groups["pydantic-v1"] = ["pydantic>=1.10.13,<2"]
    elif variant == "removed-unaffected-group":
        head_groups.pop("pydantic-v1")
    elif variant == "removed-unaffected-lock":
        head_packages = [("pydantic", "2.12.6")]
    elif variant == "new-protected-context":
        base_groups.pop("pydantic-v2")

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[published],
        head_requirements=[head_published],
        base_packages=base_packages,
        head_packages=head_packages,
        base_dependency_groups=base_groups,
        head_dependency_groups=head_groups,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("runtime-removed", False, id="runtime-dependency-and-lock-removed"),
        pytest.param("runtime-unbounded-removed", False, id="unbounded-runtime-dependency-removed"),
        pytest.param("optional-group-removed", False, id="optional-dependency-group-and-lock-removed"),
        pytest.param("optional-unbounded-removed", False, id="unbounded-optional-dependency-removed"),
        pytest.param("marker-context-removed", False, id="unbounded-marker-context-removed"),
        pytest.param("requested-extra-context-removed", False, id="requested-extra-context-removed"),
        pytest.param("declaration-removed", False, id="unbounded-same-context-declaration-removed"),
        pytest.param("unchanged", True, id="runtime-and-optional-dependencies-preserved"),
        pytest.param("transitive-only", True, id="transitive-only-security-update-preserved"),
        pytest.param("canonical-group", True, id="canonical-optional-group-spelling-preserved"),
    ],
)
def test_security_updates_cannot_remove_published_direct_dependencies(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    base_requirements = ["safe-direct>=1", "danger-pkg>=1"]
    head_requirements = ["safe-direct>=1"]
    base_packages = [("safe-direct", "1"), ("danger-pkg", "1")]
    head_packages = [("safe-direct", "1")]
    base_groups: dict[str, list[str]] | None = None
    head_groups: dict[str, list[str]] | None = None
    head_constraints: list[str] | None = None

    if variant == "runtime-unbounded-removed":
        base_requirements = ["safe-direct>=1", "danger-pkg"]
    elif variant in {"optional-group-removed", "optional-unbounded-removed"}:
        base_requirements = head_requirements = ["safe-direct>=1"]
        requirement = "danger-pkg" if variant == "optional-unbounded-removed" else "danger-pkg>=1"
        base_groups = {"feature": [requirement]}
        head_groups = {}
    elif variant == "marker-context-removed":
        base_requirements = [
            "safe-direct>=1",
            "danger-pkg; python_version < '3.11'",
            "danger-pkg; python_version >= '3.11'",
        ]
        head_requirements = ["safe-direct>=1", "danger-pkg; python_version >= '3.11'"]
        head_packages = list(base_packages)
    elif variant == "requested-extra-context-removed":
        base_requirements = ["safe-direct>=1", "danger-pkg[first]", "danger-pkg[second]"]
        head_requirements = ["safe-direct>=1", "danger-pkg[first]"]
        head_packages = list(base_packages)
    elif variant == "declaration-removed":
        base_requirements = ["safe-direct>=1", "danger-pkg", "danger-pkg<3"]
        head_requirements = ["safe-direct>=1", "danger-pkg<3"]
        head_packages = list(base_packages)
    elif variant == "unchanged":
        head_requirements = list(base_requirements)
        head_packages = list(base_packages)
        base_groups = head_groups = {"feature": ["danger-pkg>=1"]}
    elif variant == "transitive-only":
        head_requirements = list(base_requirements)
        base_packages = [*base_packages, ("transitive", "1")]
        head_packages = [("safe-direct", "1"), ("danger-pkg", "1"), ("transitive", "1.1")]
        head_constraints = ["transitive>=1.1"]
    elif variant == "canonical-group":
        base_requirements = head_requirements = ["safe-direct>=1"]
        head_packages = list(base_packages)
        base_groups = {"voice_helpers": ["danger-pkg>=1"]}
        head_groups = {"voice-helpers": ["danger-pkg>=1"]}

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=base_packages,
        head_packages=head_packages,
        base_optional_groups=base_groups,
        head_optional_groups=head_groups,
        head_constraints=head_constraints,
    )

    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr
    if not accepted:
        assert "Do not remove a published direct dependency" in result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("independent-upgrades", True, id="numpy-python-marker-lines-upgrade-independently"),
        pytest.param("reordered-marker", True, id="resolution-marker-conjunction-order-preserved"),
        pytest.param("high-line-only", True, id="unchanged-old-python-floor-does-not-require-new-line"),
        pytest.param("old-line-only", True, id="unchanged-new-python-floor-does-not-require-old-line"),
        pytest.param("swapped-lines", False, id="marker-domains-cannot-swap-locked-versions"),
        pytest.param("dropped-domain", False, id="resolution-marker-domain-cannot-disappear"),
        pytest.param("unmarked-low-floor", False, id="unmarked-floor-must-cover-every-patched-domain"),
        pytest.param("ambiguous-or", False, id="ambiguous-resolution-marker-fails-closed"),
    ],
)
def test_security_patches_follow_their_original_resolution_marker_domains(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    old_requirement = "numpy>=2.2.6; python_version < '3.11'"
    new_requirement = "numpy>=2.4.6; python_version >= '3.11'"
    old_marker = "python_full_version < '3.11'"
    new_markers = [
        "python_full_version >= '3.11' and sys_platform == 'linux'",
        "python_full_version >= '3.11' and sys_platform != 'linux'",
    ]
    base_requirements = [old_requirement, new_requirement]
    head_requirements = [
        "numpy>=2.2.7; python_version < '3.11'",
        "numpy>=2.4.7; python_version >= '3.11'",
    ]
    base_packages = [("numpy", "2.2.6"), ("numpy", "2.4.6")]
    head_packages = [("numpy", "2.2.7"), ("numpy", "2.4.7")]
    base_markers = {
        ("numpy", "2.2.6"): [old_marker],
        ("numpy", "2.4.6"): new_markers,
    }
    head_markers = {
        ("numpy", "2.2.7"): [old_marker],
        ("numpy", "2.4.7"): list(new_markers),
    }
    if variant == "reordered-marker":
        head_markers[("numpy", "2.4.7")] = [
            "sys_platform == 'linux' and python_full_version >= '3.11'",
            "sys_platform != 'linux' and python_full_version >= '3.11'",
        ]
    elif variant == "high-line-only":
        head_requirements[0] = old_requirement
        head_packages[0] = ("numpy", "2.2.6")
        head_markers.pop(("numpy", "2.2.7"))
        head_markers[("numpy", "2.2.6")] = [old_marker]
    elif variant == "old-line-only":
        head_requirements[1] = new_requirement
        head_packages[1] = ("numpy", "2.4.6")
        head_markers.pop(("numpy", "2.4.7"))
        head_markers[("numpy", "2.4.6")] = list(new_markers)
    elif variant == "swapped-lines":
        head_requirements = [
            "numpy>=2.4.7; python_version < '3.11'",
            "numpy>=2.4.7; python_version >= '3.11'",
        ]
        head_markers = {
            ("numpy", "2.2.7"): list(new_markers),
            ("numpy", "2.4.7"): [old_marker],
        }
    elif variant == "dropped-domain":
        head_requirements = [
            "numpy>=2.4.7; python_version < '3.11'",
            "numpy>=2.4.7; python_version >= '3.11'",
        ]
        head_markers[("numpy", "2.4.7")] = []
    elif variant == "unmarked-low-floor":
        base_requirements = ["numpy>=2.2.6"]
        head_requirements = ["numpy>=2.2.7"]
    elif variant == "ambiguous-or":
        head_markers[("numpy", "2.4.7")] = [
            "python_full_version >= '3.11' or sys_platform == 'linux'",
        ]
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=base_packages,
        head_packages=head_packages,
        base_resolution_markers=base_markers,
        head_resolution_markers=head_markers,
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
    ("requirement_marker", "resolution_marker", "direct_accepted", "protected_accepted"),
    [
        pytest.param(
            "python_version in '3.10, 3.11'",
            "python_full_version == '3.10.*'",
            True,
            True,
            id="python-membership-first-release",
        ),
        pytest.param(
            "python_version in '3.10, 3.11'",
            "python_full_version == '3.11.*'",
            True,
            True,
            id="python-membership-second-release",
        ),
        pytest.param(
            "python_version in '3.10, 3.11'",
            "python_full_version >= '3.12'",
            False,
            False,
            id="python-membership-excludes-other-release",
        ),
        pytest.param(
            "python_version not in '3.10, 3.11'",
            "python_full_version == '3.12.*'",
            True,
            True,
            id="python-negative-membership-allows-other-release",
        ),
        pytest.param(
            "python_version not in '3.10, 3.11'",
            "python_full_version == '3.10.*'",
            False,
            False,
            id="python-negative-membership-excludes-listed-release",
        ),
        pytest.param(
            "python_full_version in '3.10.4, 3.11.2'",
            "python_full_version == '3.10.4'",
            True,
            True,
            id="full-python-version-membership",
        ),
        pytest.param(
            "sys_platform in 'linux, darwin'",
            "sys_platform == 'linux'",
            True,
            True,
            id="platform-membership-matches-reviewed-linux",
        ),
        pytest.param(
            "sys_platform not in 'win32, darwin'",
            "sys_platform == 'linux'",
            True,
            True,
            id="negative-platform-membership-matches-reviewed-linux",
        ),
        pytest.param(
            "platform_system in 'Linux, Darwin'",
            "platform_system == 'linux'",
            False,
            False,
            id="platform-membership-preserves-quoted-case",
        ),
        pytest.param(
            "python_version >= '3.1'",
            "python_version in '3.10, 3.11'",
            True,
            True,
            id="resolution-domain-membership-also-supported",
        ),
        pytest.param(
            "python_version in '3.10,,3.11'",
            "python_full_version == '3.10.*'",
            False,
            False,
            id="empty-membership-token-fails-closed",
        ),
        pytest.param(
            "python_version in '3.10, 3.10'",
            "python_full_version == '3.10.*'",
            False,
            False,
            id="duplicate-membership-token-fails-closed",
        ),
        pytest.param(
            "python_version in '3.1, 3.10'",
            "python_full_version == '3.10.*'",
            True,
            True,
            id="overlapping-python-membership-tokens-preserve-pep508-substrings",
        ),
        pytest.param(
            "python_version in '3.10, beta'",
            "python_full_version == '3.10.*'",
            False,
            False,
            id="noncanonical-python-membership-token-fails-closed",
        ),
        pytest.param(
            "sys_platform in 'win, win32'",
            "sys_platform == 'win32'",
            True,
            True,
            id="overlapping-platform-membership-tokens-preserve-pep508-substrings",
        ),
        pytest.param(
            "unsupported_platform in 'linux'",
            "sys_platform == 'linux'",
            False,
            False,
            id="unknown-membership-variable-fails-closed",
        ),
        pytest.param(
            "python_version in '3.10' or sys_platform == 'linux'",
            "python_full_version == '3.10.*'",
            True,
            True,
            id="source-level-or-membership-remains-supported",
        ),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_security_marker_membership_overlaps_are_safe_and_precise(
    tmp_path: Path,
    requirement_marker: str,
    resolution_marker: str,
    direct_accepted: bool,
    protected_accepted: bool,
    protected: bool,
) -> None:
    base = "danger>=1; " + requirement_marker
    head = "danger>=2; " + requirement_marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [base],
        head_requirements=[] if protected else [head],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[base] if protected else None,
        head_constraints=[head] if protected else None,
        base_resolution_markers={("danger", "1"): [resolution_marker]},
        head_resolution_markers={("danger", "2"): [resolution_marker]},
    )
    accepted = protected_accepted if protected else direct_accepted
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("direct-both", True, id="both-actual-numpy-extra-groups-split-by-python-version"),
        pytest.param("direct-high-only", True, id="unchanged-python310-line-does-not-need-artificial-bump"),
        pytest.param("direct-membership-split", True, id="published-split-membership-complements-cover-all-domains"),
        pytest.param("direct-low-insufficient", False, id="python310-split-floor-must-reach-its-own-patch"),
        pytest.param("direct-high-insufficient", False, id="newer-python-split-floor-must-reach-its-own-patch"),
        pytest.param("direct-gap", False, id="split-cannot-drop-python310-resolution-domain"),
        pytest.param("direct-overlap", False, id="split-cannot-overlap-one-resolution-domain"),
        pytest.param("direct-partial-domain", False, id="split-cannot-cover-only-part-of-original-domain"),
        pytest.param("direct-moved-group", False, id="split-cannot-move-published-optional-group"),
        pytest.param("direct-upper-removed", False, id="split-cannot-remove-original-upper-bound"),
        pytest.param("direct-exclusion-removed", False, id="split-cannot-remove-original-excluded-release"),
        pytest.param("direct-original-lowered", False, id="split-cannot-lower-original-unchanged-branch"),
        pytest.param("protected-constraint", True, id="protected-constraint-splits-by-resolution-domain"),
        pytest.param("protected-group", True, id="protected-development-group-splits-by-resolution-domain"),
        pytest.param("protected-membership-split", True, id="protected-split-membership-complements-cover-all-domains"),
        pytest.param("protected-insufficient", False, id="protected-split-floor-must-reach-its-own-patch"),
        pytest.param("protected-gap", False, id="protected-split-cannot-drop-python310-domain"),
        pytest.param("protected-upper-removed", False, id="protected-split-preserves-original-upper-bound"),
    ],
)
def test_security_floors_can_safely_split_original_unmarked_resolution_domains(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    low_marker = "python_version < '3.11'"
    high_marker = "python_version >= '3.11'"
    base_packages = [("numpy", "2.2.6"), ("numpy", "2.4.6")]
    head_packages = [("numpy", "2.2.7"), ("numpy", "2.4.7")]
    base_markers = {
        ("numpy", "2.2.6"): ["python_full_version < '3.11'"],
        ("numpy", "2.4.6"): [
            "python_full_version >= '3.11' and sys_platform == 'linux'",
            "python_full_version >= '3.11' and sys_platform != 'linux'",
        ],
    }
    head_markers = {
        ("numpy", "2.2.7"): ["python_full_version < '3.11'"],
        ("numpy", "2.4.7"): [
            "python_full_version >= '3.11' and sys_platform == 'linux'",
            "python_full_version >= '3.11' and sys_platform != 'linux'",
        ],
    }
    original = "numpy>=1,<3"
    low = "numpy>=2.2.7,<3; " + low_marker
    high = "numpy>=2.4.7,<3; " + high_marker
    base_optional = {
        "datalib": [original],
        "voice_helpers": ["numpy>=2.0.2,<3"],
    }
    head_optional = {
        "datalib": [low, high],
        "voice_helpers": [low, high],
    }
    base_constraints: list[str] | None = None
    head_constraints: list[str] | None = None
    base_groups: dict[str, list[str]] | None = None
    head_groups: dict[str, list[str]] | None = None

    if variant in {"direct-membership-split", "protected-membership-split"}:
        base_markers[("numpy", "2.2.6")] = ["python_full_version == '3.10.*'"]
        head_markers[("numpy", "2.2.7")] = ["python_full_version == '3.10.*'"]
        low = "numpy>=2.2.7,<3; python_version in '3.10'"
        high = "numpy>=2.4.7,<3; python_version not in '3.10'"
        head_optional = {
            "datalib": [low, high],
            "voice_helpers": [low, high],
        }

    if variant == "direct-high-only":
        head_packages[0] = ("numpy", "2.2.6")
        head_markers.pop(("numpy", "2.2.7"))
        head_markers[("numpy", "2.2.6")] = ["python_full_version < '3.11'"]
        head_optional["datalib"][0] = "numpy>=1,<3; " + low_marker
        head_optional["voice_helpers"][0] = "numpy>=2.0.2,<3; " + low_marker
    elif variant == "direct-low-insufficient":
        head_optional["datalib"][0] = "numpy>=2.2.6,<3; " + low_marker
    elif variant == "direct-high-insufficient":
        head_optional["voice_helpers"][1] = "numpy>=2.4.6,<3; " + high_marker
    elif variant == "direct-gap":
        head_optional["datalib"] = [high]
    elif variant == "direct-overlap":
        head_optional["datalib"][0] = "numpy>=2.4.7,<3; python_version < '3.12'"
    elif variant == "direct-partial-domain":
        head_optional["datalib"][0] = "numpy>=2.2.7,<3; python_version < '3.11' and sys_platform == 'linux'"
    elif variant == "direct-moved-group":
        head_optional["moved"] = head_optional.pop("datalib")
    elif variant == "direct-upper-removed":
        head_optional["datalib"][0] = "numpy>=2.2.7; " + low_marker
    elif variant == "direct-exclusion-removed":
        base_optional["datalib"] = ["numpy>=1,<3,!=2.3"]
    elif variant == "direct-original-lowered":
        head_packages[0] = ("numpy", "2.2.6")
        head_markers.pop(("numpy", "2.2.7"))
        head_markers[("numpy", "2.2.6")] = ["python_full_version < '3.11'"]
        head_optional["voice_helpers"][0] = "numpy>=1,<3; " + low_marker
    elif variant.startswith("protected-"):
        base_optional = head_optional = {}
        if variant == "protected-group":
            base_groups, head_groups = {"dev": [original]}, {"dev": [low, high]}
        else:
            base_constraints, head_constraints = [original], [low, high]
            if variant == "protected-insufficient":
                head_constraints[0] = "numpy>=2.2.6,<3; " + low_marker
            elif variant == "protected-gap":
                head_constraints = [high]
            elif variant == "protected-upper-removed":
                head_constraints[0] = "numpy>=2.2.7; " + low_marker

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[],
        head_requirements=[],
        base_packages=base_packages,
        head_packages=head_packages,
        base_optional_groups=base_optional,
        head_optional_groups=head_optional,
        base_constraints=base_constraints,
        head_constraints=head_constraints,
        base_dependency_groups=base_groups,
        head_dependency_groups=head_groups,
        base_resolution_markers=base_markers,
        head_resolution_markers=head_markers,
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


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("constraint-lock-only", False, id="protected-transitive-lock-only-security-update"),
        pytest.param("constraint-insufficient", False, id="protected-transitive-floor-below-patched-release"),
        pytest.param("constraint-patched", True, id="protected-transitive-floor-reaches-patched-release"),
        pytest.param("constraint-higher", True, id="protected-transitive-floor-exceeds-patched-release"),
        pytest.param("constraint-upper-blocks", False, id="protected-transitive-upper-bound-excludes-patch"),
        pytest.param("constraint-unchanged-lock", True, id="protected-transitive-unchanged-lock-preserved"),
        pytest.param("unrelated-transitive", True, id="unrelated-transitive-lock-only-update-preserved"),
        pytest.param("unbounded-group", True, id="unbounded-development-group-lock-update-preserved"),
        pytest.param("group-lock-only", False, id="development-group-floor-must-reach-patched-release"),
        pytest.param("group-patched", True, id="development-group-floor-reaches-patched-release"),
        pytest.param("build-pin-lock-only", False, id="build-constraint-pin-must-reach-patched-release"),
        pytest.param("build-pin-patched", True, id="build-constraint-pin-reaches-patched-release"),
        pytest.param("post-lock-only", False, id="protected-floor-must-reach-stable-post-release"),
        pytest.param("post-patched", True, id="protected-floor-reaches-stable-post-release"),
        pytest.param("epoch-lock-only", False, id="protected-floor-must-reach-new-epoch-release"),
        pytest.param("epoch-patched", True, id="protected-floor-reaches-new-epoch-release"),
        pytest.param("downgrade", False, id="protected-locked-release-cannot-downgrade"),
        pytest.param("added-release", False, id="protected-added-release-without-prior-line-fails-closed"),
        pytest.param("removed-release", False, id="protected-removed-release-without-patch-fails-closed"),
        pytest.param("prerelease", False, id="protected-prerelease-patch-fails-closed"),
        pytest.param("marker-low-unaffected", False, id="unprotected-marker-line-upgrade-requires-security-boundary"),
        pytest.param("marker-high-lock-only", False, id="protected-marker-context-floor-must-reach-patch"),
        pytest.param("marker-high-patched", True, id="protected-marker-context-floor-reaches-patch"),
        pytest.param("pydantic-v1-lock-only", False, id="protected-pydantic-v1-floor-must-reach-patch"),
        pytest.param("pydantic-v1-patched", True, id="protected-pydantic-v1-patch-preserves-v2-line"),
        pytest.param("pydantic-v2-patched", True, id="protected-pydantic-v2-patch-preserves-v1-line"),
    ],
)
def test_protected_security_floors_must_reach_their_patched_release(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    base_constraints: list[str] | None = ["cryptography>=50"]
    head_constraints: list[str] | None = ["cryptography>=50"]
    base_build_constraints: list[str] | None = None
    head_build_constraints: list[str] | None = None
    base_groups: dict[str, list[str]] | None = None
    head_groups: dict[str, list[str]] | None = None
    base_packages = [("cryptography", "50")]
    head_packages = [("cryptography", "51")]
    base_markers: dict[tuple[str, str], list[str]] | None = None
    head_markers: dict[tuple[str, str], list[str]] | None = None

    if variant == "constraint-insufficient":
        head_constraints = ["cryptography>=50.1"]
    elif variant == "constraint-patched":
        head_constraints = ["cryptography>=51"]
    elif variant == "constraint-higher":
        head_constraints = ["cryptography>=52"]
    elif variant == "constraint-upper-blocks":
        base_constraints = ["cryptography>=50,<52"]
        head_constraints = ["cryptography>=51,<51"]
    elif variant == "constraint-unchanged-lock":
        head_packages = list(base_packages)
    elif variant == "unrelated-transitive":
        base_packages.append(("unrelated", "1"))
        head_packages = [("cryptography", "50"), ("unrelated", "2")]
        head_constraints = ["cryptography>=50", "unrelated>=2"]
    elif variant == "unbounded-group":
        base_constraints = head_constraints = None
        base_groups = {"dev": ["ruff"]}
        head_groups = {"dev": ["ruff>=2"]}
        base_packages, head_packages = [("ruff", "1")], [("ruff", "2")]
    elif variant in {"group-lock-only", "group-patched"}:
        base_constraints = head_constraints = None
        base_groups = {"dev": ["pytest>=9"]}
        head_groups = {"dev": ["pytest>=10" if variant == "group-patched" else "pytest>=9"]}
        base_packages, head_packages = [("pytest", "9")], [("pytest", "10")]
    elif variant in {"build-pin-lock-only", "build-pin-patched"}:
        base_constraints = head_constraints = None
        base_build_constraints = ["hatchling==1.27"]
        head_build_constraints = ["hatchling==1.28" if variant == "build-pin-patched" else "hatchling==1.27"]
        base_packages, head_packages = [("hatchling", "1.27")], [("hatchling", "1.28")]
    elif variant in {"post-lock-only", "post-patched"}:
        base_constraints = ["cryptography>=50"]
        head_constraints = ["cryptography>=50.post1" if variant == "post-patched" else "cryptography>=50"]
        base_packages, head_packages = [("cryptography", "50")], [("cryptography", "50.post1")]
    elif variant in {"epoch-lock-only", "epoch-patched"}:
        base_constraints = ["cryptography>=0!50"]
        head_constraints = ["cryptography>=1!1" if variant == "epoch-patched" else "cryptography>=0!50"]
        base_packages, head_packages = [("cryptography", "50")], [("cryptography", "1!1")]
    elif variant == "downgrade":
        base_constraints, head_constraints = ["cryptography>=50"], ["cryptography>=51"]
        base_packages, head_packages = [("cryptography", "52")], [("cryptography", "51")]
    elif variant == "added-release":
        head_constraints = ["cryptography>=51"]
        head_packages = [("cryptography", "50"), ("cryptography", "51")]
    elif variant == "removed-release":
        head_constraints = ["cryptography>=51"]
        base_packages = [("cryptography", "50"), ("cryptography", "51")]
        head_packages = [("cryptography", "51")]
    elif variant == "prerelease":
        head_constraints = ["cryptography>=51"]
        head_packages = [("cryptography", "51rc1")]
    elif variant.startswith("marker-"):
        old_requirement = "cryptography>=50; python_version < '3.11'"
        new_requirement = "cryptography>=60; python_version >= '3.11'"
        base_constraints = [old_requirement]
        head_constraints = [old_requirement]
        if variant != "marker-low-unaffected":
            base_constraints.append(new_requirement)
            head_constraints.append(
                "cryptography>=61; python_version >= '3.11'" if variant == "marker-high-patched" else new_requirement
            )
        base_packages = [("cryptography", "50"), ("cryptography", "60")]
        head_packages = [("cryptography", "50"), ("cryptography", "61")]
        base_markers = {
            ("cryptography", "50"): ["python_full_version < '3.11'"],
            ("cryptography", "60"): ["python_full_version >= '3.11'"],
        }
        head_markers = {
            ("cryptography", "50"): ["python_full_version < '3.11'"],
            ("cryptography", "61"): ["python_full_version >= '3.11'"],
        }
    elif variant.startswith("pydantic-"):
        base_constraints = head_constraints = None
        base_groups = {
            "pydantic-v1": ["pydantic>=1.10,<2"],
            "pydantic-v2": ["pydantic>=2,<3"],
        }
        head_groups = {
            "pydantic-v1": ["pydantic>=1.11,<2" if variant == "pydantic-v1-patched" else "pydantic>=1.10,<2"],
            "pydantic-v2": ["pydantic>=2.13,<3" if variant == "pydantic-v2-patched" else "pydantic>=2,<3"],
        }
        base_packages = [("pydantic", "1.10"), ("pydantic", "2.12")]
        head_packages = (
            [("pydantic", "1.10"), ("pydantic", "2.13")]
            if variant == "pydantic-v2-patched"
            else [("pydantic", "1.11"), ("pydantic", "2.12")]
        )

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[],
        head_requirements=[],
        base_packages=base_packages,
        head_packages=head_packages,
        base_constraints=base_constraints,
        head_constraints=head_constraints,
        base_build_constraints=base_build_constraints,
        head_build_constraints=head_build_constraints,
        base_dependency_groups=base_groups,
        head_dependency_groups=head_groups,
        base_resolution_markers=base_markers,
        head_resolution_markers=head_markers,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("lock-only", False, id="newly-patched-transitive-lock-needs-security-boundary"),
        pytest.param("grouped-lock-only", False, id="grouped-direct-patch-cannot-hide-transitive-lock-only"),
        pytest.param("unbounded-group", False, id="unbounded-development-entry-is-not-a-security-boundary"),
        pytest.param("constraint-missing-floor", False, id="new-uv-constraint-without-floor-does-not-protect"),
        pytest.param("constraint-too-low", False, id="new-uv-constraint-must-reach-patched-release"),
        pytest.param("constraint-old-inclusive", False, id="new-boundary-must-exclude-vulnerable-old-release"),
        pytest.param("constraint-excludes-patch", False, id="new-boundary-must-admit-actual-patched-release"),
        pytest.param("strict-excludes-patch", False, id="strict-boundary-cannot-exclude-patched-release"),
        pytest.param("wrong-marker", False, id="transitive-security-floor-cannot-move-marker-domain"),
        pytest.param("widened-marker", False, id="transitive-security-floor-cannot-widen-over-supported-line"),
        pytest.param("added-without-removal", False, id="shared-transitive-upgrade-cannot-retain-vulnerable-release"),
        pytest.param("ambiguous-upgrade", False, id="shared-transitive-upgrade-must-pair-one-for-one"),
        pytest.param("downgrade", False, id="shared-transitive-security-release-cannot-downgrade"),
        pytest.param("uv-floor", True, id="new-reviewed-uv-security-floor-covers-transitive-patch"),
        pytest.param("uv-exact", True, id="new-reviewed-exact-uv-pin-covers-transitive-patch"),
        pytest.param("build-exact", True, id="new-reviewed-build-pin-covers-transitive-patch"),
        pytest.param("group-floor", True, id="new-reviewed-development-floor-covers-transitive-patch"),
        pytest.param("published-floor", True, id="new-published-floor-covers-former-transitive-patch"),
        pytest.param("unchanged", True, id="unchanged-unprotected-transitive-release-remains-supported"),
        pytest.param("new-package", True, id="genuinely-new-package-introduction-remains-supported"),
        pytest.param("removed-package", True, id="fully-removed-transitive-package-remains-supported"),
        pytest.param("canonical-name", True, id="canonical-equivalent-transitive-name-remains-supported"),
        pytest.param("marker-floor", True, id="matching-marker-security-floor-preserves-unaffected-line"),
        pytest.param("epoch-floor", True, id="matching-epoch-security-floor-covers-transitive-patch"),
        pytest.param("post-floor", True, id="matching-stable-post-floor-covers-transitive-patch"),
        pytest.param("independent-majors", True, id="new-reviewed-v2-floor-preserves-independent-v1-lock"),
    ],
)
def test_newly_patched_transitive_dependencies_require_security_boundaries(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    name, old, patched = "transitive", "1", "2"
    base_requirements, head_requirements = ["patch-me>=1"], ["patch-me>=1.1"]
    before: list[tuple[str, str]] = [(name, old)]
    after: list[tuple[str, str]] = [(name, patched)]
    base_constraints: list[str] | None = None
    head_constraints: list[str] | None = None
    base_build: list[str] | None = None
    head_build: list[str] | None = None
    base_groups: dict[str, list[str]] | None = None
    head_groups: dict[str, list[str]] | None = None
    base_markers: dict[tuple[str, str], list[str]] | None = None
    head_markers: dict[tuple[str, str], list[str]] | None = None

    if variant == "lock-only":
        head_requirements = list(base_requirements)
    elif variant == "unbounded-group":
        base_groups = head_groups = {"dev": [name]}
    elif variant == "constraint-missing-floor":
        head_constraints = [name]
    elif variant == "constraint-too-low":
        head_constraints = [name + ">=1.5"]
    elif variant == "constraint-old-inclusive":
        head_constraints = [name + ">=1"]
    elif variant == "constraint-excludes-patch":
        head_constraints = [name + ">=2,<2"]
    elif variant == "strict-excludes-patch":
        head_constraints = [name + ">2"]
    elif variant in {"wrong-marker", "widened-marker", "marker-floor"}:
        before = [(name, "1"), (name, "2")]
        after = [(name, "1"), (name, "3")]
        base_markers = {
            (name, "1"): ["python_full_version < '3.11'"],
            (name, "2"): ["python_full_version >= '3.11'"],
        }
        head_markers = {
            (name, "1"): ["python_full_version < '3.11'"],
            (name, "3"): ["python_full_version >= '3.11'"],
        }
        if variant == "wrong-marker":
            head_constraints = [name + ">=3; python_version < '3.11'"]
        elif variant == "widened-marker":
            head_constraints = [name + ">=3"]
        else:
            head_constraints = [name + ">=3; python_version >= '3.11'"]
    elif variant == "added-without-removal":
        after = [(name, old), (name, patched)]
        head_constraints = [name + ">=2"]
    elif variant == "ambiguous-upgrade":
        after = [(name, "2"), (name, "3")]
        head_constraints = [name + ">=2"]
    elif variant == "downgrade":
        before, after = [(name, "2")], [(name, "1")]
        head_constraints = [name + ">=1"]
    elif variant == "uv-floor":
        head_constraints = [name + ">=2"]
    elif variant == "uv-exact":
        head_constraints = [name + "==2"]
    elif variant == "build-exact":
        head_build = [name + "==2"]
    elif variant == "group-floor":
        head_groups = {"reviewed": [name + ">=2"]}
    elif variant == "published-floor":
        head_requirements.append(name + ">=2")
    elif variant == "unchanged":
        after = list(before)
    elif variant == "new-package":
        before = []
    elif variant == "removed-package":
        after = []
    elif variant == "canonical-name":
        before = [("Transitive_Pkg", old)]
        after = [("transitive-pkg", patched)]
        head_constraints = ["transitive.pkg>=2"]
    elif variant == "epoch-floor":
        before, after = [(name, "1!1")], [(name, "1!2")]
        head_constraints = [name + ">=1!2"]
    elif variant == "post-floor":
        before, after = [(name, "1.post1")], [(name, "1.post2")]
        head_constraints = [name + ">=1.post2"]
    elif variant == "independent-majors":
        name = "pydantic"
        before, after = [(name, "1.10"), (name, "2.12")], [(name, "1.10"), (name, "2.13")]
        head_groups = {"pydantic-v2": [name + ">=2.13,<3"]}

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=[("patch-me", "1"), *before],
        head_packages=[("patch-me", "1" if variant == "lock-only" else "1.1"), *after],
        base_constraints=base_constraints,
        head_constraints=head_constraints,
        base_build_constraints=base_build,
        head_build_constraints=head_build,
        base_dependency_groups=base_groups,
        head_dependency_groups=head_groups,
        base_resolution_markers=base_markers,
        head_resolution_markers=head_markers,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("disjoint-unreviewed", False, id="protected-high-domain-cannot-hide-unreviewed-low-upgrade"),
        pytest.param("disjoint-reviewed", True, id="new-disjoint-reviewed-floor-protects-low-domain"),
        pytest.param("disjoint-insufficient", False, id="new-disjoint-floor-must-reach-low-domain-patch"),
        pytest.param("disjoint-drops-retained", False, id="new-overlapping-floor-cannot-drop-retained-high-domain"),
        pytest.param("broad-prior-partial", False, id="prior-partial-marker-cannot-cover-broad-resolution-domain"),
        pytest.param("broad-prior-complement", True, id="complementary-prior-markers-cover-broad-resolution-domain"),
        pytest.param("broad-prior-additive-global", True, id="reviewed-global-floor-may-overlap-protected-domain"),
        pytest.param("broad-prior-additive-broad", True, id="reviewed-broader-floor-may-overlap-protected-domain"),
        pytest.param("broad-prior-additive-insufficient", False, id="overlapping-additive-floor-must-reach-patch"),
        pytest.param("broad-prior-old-weakened", False, id="overlapping-addition-cannot-weaken-original-context"),
        pytest.param("broad-prior-old-dropped", False, id="overlapping-addition-cannot-remove-original-context"),
        pytest.param("broad-current-partial", False, id="reviewed-partial-marker-cannot-cover-broad-resolution-domain"),
        pytest.param("broad-current-complement", True, id="complementary-reviewed-markers-cover-resolution-domain"),
        pytest.param("platform-prior-partial", False, id="python-platform-conjunction-cannot-cover-other-platforms"),
        pytest.param("platform-prior-complement", True, id="complementary-platform-markers-cover-every-platform"),
        pytest.param("membership-prior-partial", False, id="membership-protection-cannot-hide-unlisted-python-lines"),
        pytest.param("membership-prior-complement", True, id="membership-complements-cover-all-python-lines"),
        pytest.param("full-version-prior-partial", False, id="full-python-version-protection-cannot-hide-other-lines"),
        pytest.param("independent-major-unreviewed", False, id="protected-v1-cannot-hide-unreviewed-v2-upgrade"),
        pytest.param("independent-major-reviewed", True, id="new-reviewed-v2-group-preserves-existing-v1-group"),
        pytest.param("independent-major-insufficient", False, id="new-v2-group-must-exclude-vulnerable-release"),
        pytest.param(
            "independent-major-global-drops-retained",
            False,
            id="global-additive-floor-cannot-drop-same-domain-protected-v1-release",
        ),
        pytest.param(
            "independent-major-same-group-drops-retained",
            False,
            id="same-group-additive-floor-cannot-drop-same-domain-protected-v1-release",
        ),
        pytest.param("mixed-declarations", False, id="same-context-floor-must-protect-the-actual-removed-release"),
        pytest.param("unchanged-uncovered", True, id="unchanged-unprotected-resolution-domain-remains-supported"),
        pytest.param("extra-platform-uncovered", False, id="selected-extra-platform-cannot-borrow-linux-protection"),
        pytest.param("malformed-membership", False, id="ambiguous-protected-domain-membership-fails-closed"),
        pytest.param("fragment-limit", False, id="overcomplex-security-domain-partition-fails-closed"),
    ],
)
def test_transitive_security_boundaries_cover_every_resolution_fragment(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    name = "transitive"
    before = [(name, "4")]
    after = [(name, "5")]
    base_requirements = ["patch-me>=1"]
    head_requirements = ["patch-me>=1.1"]
    base_constraints: list[str] | None = None
    head_constraints: list[str] | None = None
    base_groups: dict[str, list[str]] | None = None
    head_groups: dict[str, list[str]] | None = None
    base_optional_edges: dict[tuple[str, str], dict[str, list[dict[str, object]]]] | None = None
    head_optional_edges: dict[tuple[str, str], dict[str, list[dict[str, object]]]] | None = None
    broad = "python_full_version >= '3.10'"
    base_markers: dict[tuple[str, str], list[str]] = {(name, "4"): [broad]}
    head_markers: dict[tuple[str, str], list[str]] = {(name, "5"): [broad]}

    if variant.startswith("disjoint-"):
        before = [(name, "1"), (name, "3")]
        after = [(name, "2"), (name, "3")]
        base_markers = {
            (name, "1"): ["python_full_version < '3.11'"],
            (name, "3"): ["python_full_version >= '3.11'"],
        }
        head_markers = {
            (name, "2"): ["python_full_version < '3.11'"],
            (name, "3"): ["python_full_version >= '3.11'"],
        }
        high = name + ">=3; python_version >= '3.11'"
        base_constraints = [high]
        head_constraints = [high]
        if variant == "disjoint-reviewed":
            head_constraints.append(name + ">=2; python_version < '3.11'")
        elif variant == "disjoint-insufficient":
            head_constraints.append(name + ">=1; python_version < '3.11'")
        elif variant == "disjoint-drops-retained":
            head_constraints.append(name + ">=2,<3")
    elif variant.startswith("broad-prior-"):
        high = "; python_version >= '3.11'"
        base_constraints = [name + ">=4" + high]
        head_constraints = [name + ">=5" + high]
        if variant == "broad-prior-complement":
            low = "; python_version < '3.11'"
            base_constraints.append(name + ">=4" + low)
            head_constraints.append(name + ">=5" + low)
        elif variant == "broad-prior-additive-global":
            head_constraints.append(name + ">=5")
        elif variant == "broad-prior-additive-broad":
            head_constraints.append(name + ">=5; python_version >= '3.10'")
        elif variant == "broad-prior-additive-insufficient":
            head_constraints.append(name + ">=4")
        elif variant == "broad-prior-old-weakened":
            head_constraints = [name + ">=3" + high, name + ">=5"]
        elif variant == "broad-prior-old-dropped":
            head_constraints = [name + ">=5"]
    elif variant in {"broad-current-partial", "broad-current-complement"}:
        head_constraints = [name + ">=5; python_version >= '3.11'"]
        if variant == "broad-current-complement":
            head_constraints.append(name + ">=5; python_version < '3.11'")
    elif variant in {"platform-prior-partial", "platform-prior-complement"}:
        marker = "; sys_platform == 'linux'"
        if variant == "platform-prior-partial":
            marker = "; python_version >= '3.11' and sys_platform == 'linux'"
        base_constraints = [name + ">=4" + marker]
        head_constraints = [name + ">=5" + marker]
        if variant == "platform-prior-complement":
            other = "; sys_platform != 'linux'"
            base_constraints.append(name + ">=4" + other)
            head_constraints.append(name + ">=5" + other)
    elif variant in {"membership-prior-partial", "membership-prior-complement"}:
        marker = "; python_version in '3.11, 3.12'"
        base_constraints = [name + ">=4" + marker]
        head_constraints = [name + ">=5" + marker]
        if variant == "membership-prior-complement":
            other = "; python_version not in '3.11, 3.12'"
            base_constraints.append(name + ">=4" + other)
            head_constraints.append(name + ">=5" + other)
    elif variant == "full-version-prior-partial":
        marker = "; python_full_version == '3.11.*'"
        base_constraints = [name + ">=4" + marker]
        head_constraints = [name + ">=5" + marker]
    elif variant.startswith("independent-major-"):
        name = "pydantic"
        before = [(name, "1.5"), (name, "2.4")]
        after = [(name, "1.5"), (name, "2.5")]
        base_markers = {}
        head_markers = {}
        base_groups = {"pydantic-v1": [name + ">=1,<2"]}
        head_groups = {"pydantic-v1": [name + ">=1,<2"]}
        if variant == "independent-major-reviewed":
            head_groups["pydantic-v2"] = [name + ">=2.5,<3"]
        elif variant == "independent-major-insufficient":
            head_groups["pydantic-v2"] = [name + ">=2.4,<3"]
        elif variant == "independent-major-global-drops-retained":
            head_constraints = [name + ">=2.5,<3"]
        elif variant == "independent-major-same-group-drops-retained":
            base_markers = {(name, release): [broad] for _, release in before}
            head_markers = {(name, release): [broad] for _, release in after}
            head_groups["pydantic-v1"].append(name + ">=2.5,<3; python_version >= '3.10'")
    elif variant == "mixed-declarations":
        before = [(name, "5")]
        after = [(name, "6")]
        base_markers = {}
        head_markers = {}
        base_constraints = [name + ">=10", name + "<8"]
        head_constraints = list(base_constraints)
    elif variant == "unchanged-uncovered":
        after = list(before)
        head_markers = dict(base_markers)
        marker = "; python_version >= '3.11'"
        base_constraints = [name + ">=4" + marker]
        head_constraints = list(base_constraints)
    elif variant == "extra-platform-uncovered":
        base_requirements.append("parent[feature]")
        head_requirements.append("parent[feature]")
        before.insert(0, ("parent", "1"))
        after.insert(0, ("parent", "1"))
        edges: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {
            ("parent", "1"): {"feature": [{"name": name, "marker": "extra == 'feature' and sys_platform == 'win32'"}]}
        }
        base_optional_edges = edges
        head_optional_edges = edges
        marker = "; python_version >= '3.11' and sys_platform == 'linux'"
        base_constraints = [name + ">=4" + marker]
        head_constraints = [name + ">=5" + marker]
    elif variant == "malformed-membership":
        marker = "; sys_platform in 'linux, linux'"
        base_constraints = [name + ">=4" + marker]
        head_constraints = [name + ">=5" + marker]
    elif variant == "fragment-limit":
        membership = ", ".join("3." + str(minor) for minor in range(16))
        platforms = "linux, darwin, win32, freebsd, openbsd"
        broad = "python_version in '" + membership + "' and sys_platform in '" + platforms + "'"
        base_markers = {(name, "4"): [broad]}
        head_markers = {(name, "5"): [broad]}
        marker = "; python_version >= '3.11'"
        base_constraints = [name + ">=4" + marker]
        head_constraints = [name + ">=5" + marker]

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=[("patch-me", "1"), *before],
        head_packages=[("patch-me", "1.1"), *after],
        base_constraints=base_constraints,
        head_constraints=head_constraints,
        base_dependency_groups=base_groups,
        head_dependency_groups=head_groups,
        base_resolution_markers=base_markers,
        head_resolution_markers=head_markers,
        base_lock_optional_dependencies=base_optional_edges,
        head_lock_optional_dependencies=head_optional_edges,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("wildcard", True, id="transitive-vulnerable-series-exclusion-preserves-independent-major"),
        pytest.param("canonical-wildcard", True, id="canonical-series-exclusion-preserves-independent-major"),
        pytest.param("no-global-floor", True, id="series-exclusion-does-not-require-destructive-global-floor"),
        pytest.param("group-wildcard", True, id="reviewed-development-series-exclusion-protects-transitive-patch"),
        pytest.param("post-wildcard", True, id="wildcard-excludes-old-stable-post-release-series"),
        pytest.param("extra-exclusion", True, id="independent-reviewed-series-exclusions-remain-supported"),
        pytest.param("exact-only", False, id="single-exact-exclusion-cannot-protect-whole-vulnerable-series"),
        pytest.param("narrow-wildcard", False, id="narrow-wildcard-must-cover-actual-removed-release"),
        pytest.param("narrow-zero-wildcard", False, id="zero-padded-wildcard-must-cover-whole-vulnerable-series"),
        pytest.param("missing-exclusion", False, id="low-global-floor-without-series-exclusion-is-unsafe"),
        pytest.param("wrong-epoch", False, id="series-exclusion-must-match-removed-release-epoch"),
        pytest.param("drops-retained", False, id="series-boundary-must-preserve-independent-supported-major"),
        pytest.param("drops-patched", False, id="series-boundary-must-admit-actual-patched-release"),
        pytest.param("overbroad-wildcard", False, id="series-exclusion-cannot-cover-actual-patched-release"),
    ],
)
def test_transitive_security_boundaries_accept_reviewed_vulnerable_series_exclusions(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    old, patched = "2.5", "2.6"
    requirement = "danger>=1,<3,!=2.5.*"
    groups: dict[str, list[str]] | None = None

    if variant == "canonical-wildcard":
        requirement = "danger>=1,<3,!=02.05.*"
    elif variant == "no-global-floor":
        requirement = "danger<3,!=2.5.*"
    elif variant == "group-wildcard":
        groups = {"pydantic-v2": [requirement]}
    elif variant == "post-wildcard":
        old = "2.5.post1"
    elif variant == "extra-exclusion":
        requirement += ",!=2.4.*"
    elif variant == "exact-only":
        requirement = "danger>=1,<3,!=2.5"
    elif variant == "narrow-wildcard":
        requirement = "danger>=1,<3,!=2.5.1.*"
    elif variant == "narrow-zero-wildcard":
        requirement = "danger>=1,<3,!=2.5.0.*"
    elif variant == "missing-exclusion":
        requirement = "danger>=1,<3"
    elif variant == "wrong-epoch":
        requirement = "danger>=1,<3,!=1!2.5.*"
    elif variant == "drops-retained":
        requirement = "danger>=2,<3,!=2.5.*"
    elif variant == "drops-patched":
        requirement = "danger>=1,<2.6,!=2.5.*"
    elif variant == "overbroad-wildcard":
        requirement = "danger>=1,<3,!=2.*"

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1"],
        head_requirements=["patch-me>=1.1"],
        base_packages=[("patch-me", "1"), ("danger", "1.5"), ("danger", old)],
        head_packages=[("patch-me", "1.1"), ("danger", "1.5"), ("danger", patched)],
        head_constraints=None if groups is not None else [requirement],
        head_dependency_groups=groups,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("runtime-extra", False, id="new-runtime-extra-cannot-introduce-unreviewed-wheel"),
        pytest.param("optional-extra", False, id="new-optional-extra-cannot-introduce-unreviewed-wheel"),
        pytest.param("two-new-packages", False, id="every-new-extra-dependency-identity-must-be-reviewed"),
        pytest.param("unbounded-review", False, id="unbounded-new-extra-dependency-is-not-review-boundary"),
        pytest.param("low-review", False, id="reviewed-new-extra-floor-must-reach-actual-release"),
        pytest.param("wrong-marker", False, id="new-extra-package-review-must-cover-actual-marker-domain"),
        pytest.param("reviewed-floor", True, id="reviewed-floor-can-approve-new-extra-package-identity"),
        pytest.param("reviewed-pin", True, id="reviewed-exact-pin-can-approve-new-extra-package-identity"),
        pytest.param("reviewed-group", True, id="reviewed-development-bound-can-approve-new-extra-package"),
        pytest.param("reviewed-marker", True, id="reviewed-matching-marker-can-approve-new-extra-package"),
        pytest.param("no-new-package", True, id="new-extra-without-new-package-identity-remains-supported"),
        pytest.param("unchanged-extra", True, id="unchanged-existing-extra-does-not-block-unrelated-new-package"),
        pytest.param("widened-extra", False, id="widened-existing-extra-cannot-introduce-unreviewed-package"),
        pytest.param("reviewed-widened-extra", True, id="reviewed-boundary-can-approve-widened-existing-extra"),
        pytest.param("no-extra-change", True, id="ordinary-unrelated-new-package-remains-supported"),
        pytest.param("canonical-extra", True, id="canonical-existing-extra-name-is-not-a-new-context"),
    ],
)
def test_new_requested_extras_cannot_introduce_unreviewed_dependency_identities(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    base_requirements = ["patch-me>=1", "parent"]
    head_requirements = ["patch-me>=1.1", "parent", "parent[new-extra]"]
    base_optional: dict[str, list[str]] | None = None
    head_optional: dict[str, list[str]] | None = None
    constraints: list[str] | None = None
    groups: dict[str, list[str]] | None = None
    new_packages: list[tuple[str, str]] = [("unreviewed-plugin", "1")]
    head_markers: dict[tuple[str, str], list[str]] | None = None

    if variant == "optional-extra":
        base_requirements, head_requirements = ["patch-me>=1"], ["patch-me>=1.1"]
        base_optional = {"feature": ["parent"]}
        head_optional = {"feature": ["parent", "parent[new-extra]"]}
    elif variant == "two-new-packages":
        new_packages.append(("second-unreviewed-plugin", "1"))
        constraints = ["unreviewed-plugin>=1"]
    elif variant == "unbounded-review":
        constraints = ["unreviewed-plugin"]
    elif variant == "low-review":
        constraints = ["unreviewed-plugin>=0"]
    elif variant in {"wrong-marker", "reviewed-marker"}:
        head_requirements[-1] += "; python_version >= '3.11'"
        head_markers = {("unreviewed-plugin", "1"): ["python_full_version >= '3.11'"]}
        suffix = "< '3.11'" if variant == "wrong-marker" else ">= '3.11'"
        constraints = ["unreviewed-plugin>=1; python_version " + suffix]
    elif variant == "reviewed-floor":
        constraints = ["unreviewed-plugin>=1"]
    elif variant == "reviewed-pin":
        constraints = ["unreviewed-plugin==1"]
    elif variant == "reviewed-group":
        groups = {"reviewed": ["unreviewed-plugin>=1"]}
    elif variant == "no-new-package":
        new_packages = []
    elif variant == "unchanged-extra":
        base_requirements[-1] = "parent[new-extra]"
        head_requirements = ["patch-me>=1.1", "parent[new-extra]"]
    elif variant in {"widened-extra", "reviewed-widened-extra"}:
        base_requirements[-1] = "parent[new-extra]; python_version < '3.11'"
        head_requirements = ["patch-me>=1.1", base_requirements[-1], "parent[new-extra]"]
        if variant == "reviewed-widened-extra":
            constraints = ["unreviewed-plugin>=1"]
    elif variant == "no-extra-change":
        head_requirements = ["patch-me>=1.1", "parent"]
    elif variant == "canonical-extra":
        base_requirements[-1] = "parent[New_Extra]"
        head_requirements = ["patch-me>=1.1", "parent[new-extra]"]

    optional_edges: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {
        ("parent", "1"): {"new-extra": [{"name": name} for name, _ in new_packages]}
    }
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=[("patch-me", "1"), ("parent", "1")],
        head_packages=[("patch-me", "1.1"), ("parent", "1"), *new_packages],
        base_optional_groups=base_optional,
        head_optional_groups=head_optional,
        head_constraints=constraints,
        head_dependency_groups=groups,
        head_resolution_markers=head_markers,
        head_lock_optional_dependencies=optional_edges,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("existing-dev", False, id="new-extra-cannot-publish-previously-dev-locked-package"),
        pytest.param("reviewed-existing-dev", True, id="reviewed-floor-allows-previously-dev-locked-package"),
        pytest.param("already-runtime", True, id="already-published-runtime-package-needs-no-extra-review"),
        pytest.param("transitive-existing", False, id="new-extra-cannot-publish-transitive-dev-locked-package"),
        pytest.param("reviewed-transitive", True, id="reviewed-contextual-floors-allow-transitive-existing-packages"),
        pytest.param("selected-nested-extra", False, id="nested-selected-extra-cannot-publish-dev-locked-package"),
        pytest.param("wrong-marker", False, id="reviewed-existing-package-bound-must-cover-extra-domain"),
        pytest.param("matching-marker", True, id="reviewed-existing-package-marker-can-cover-extra-domain"),
        pytest.param("unchanged-extra", True, id="unchanged-requested-extra-keeps-prior-published-reachability"),
        pytest.param("cyclic-extra", False, id="cyclic-extra-cannot-hide-an-unreviewed-dependency"),
        pytest.param("reviewed-cyclic-extra", True, id="reviewed-cyclic-extra-dependency-graph-is-supported"),
        pytest.param("composed-extra", False, id="composed-extra-cannot-hide-an-unreviewed-dependency"),
        pytest.param("reviewed-composed-extra", True, id="reviewed-self-referential-composed-extra-is-supported"),
        pytest.param("mutual-cycle", False, id="mutual-package-cycle-cannot-hide-an-unreviewed-dependency"),
        pytest.param("reviewed-mutual-cycle", True, id="reviewed-mutual-package-dependency-cycle-is-supported"),
        pytest.param("ambiguous-edge", False, id="ambiguous-extra-dependency-edge-fails-closed"),
    ],
)
def test_new_extras_cannot_publish_previously_locked_transitive_packages(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    base_requirements = ["patch-me>=1", "parent"]
    head_requirements = ["patch-me>=1.1", "parent", "parent[new-extra]"]
    packages = [("parent", "1"), ("existing-plugin", "1")]
    base_groups = {"dev": ["existing-plugin"]}
    head_groups = {"dev": ["existing-plugin"]}
    base_edges: dict[tuple[str, str], list[dict[str, object]]] = {}
    head_edges: dict[tuple[str, str], list[dict[str, object]]] = {}
    parent_optional: dict[str, list[dict[str, object]]] = {"new-extra": [{"name": "existing-plugin"}]}
    base_optional = {("parent", "1"): dict(parent_optional)}
    head_optional = {("parent", "1"): dict(parent_optional)}
    constraints: list[str] | None = None
    markers: dict[tuple[str, str], list[str]] | None = None

    if variant == "reviewed-existing-dev":
        constraints = ["existing-plugin>=1"]
    elif variant == "already-runtime":
        base_requirements.append("existing-plugin>=1")
        head_requirements.append("existing-plugin>=1")
    elif variant in {
        "transitive-existing",
        "reviewed-transitive",
        "selected-nested-extra",
        "cyclic-extra",
        "reviewed-cyclic-extra",
        "mutual-cycle",
        "reviewed-mutual-cycle",
    }:
        packages.append(("bridge", "1"))
        parent_optional["new-extra"] = [{"name": "bridge"}]
        if variant == "selected-nested-extra":
            parent_optional["new-extra"] = [{"name": "bridge", "extra": ["nested"]}]
            head_optional[("bridge", "1")] = {"nested": [{"name": "existing-plugin"}]}
            base_optional[("bridge", "1")] = {"nested": [{"name": "existing-plugin"}]}
        elif variant in {"cyclic-extra", "reviewed-cyclic-extra"}:
            head_edges[("bridge", "1")] = [{"name": "parent", "extra": ["new-extra"]}]
            base_edges[("bridge", "1")] = list(head_edges[("bridge", "1")])
        elif variant in {"mutual-cycle", "reviewed-mutual-cycle"}:
            head_edges[("bridge", "1")] = [{"name": "existing-plugin"}]
            head_edges[("existing-plugin", "1")] = [{"name": "bridge"}]
            base_edges.update({identity: list(edges) for identity, edges in head_edges.items()})
        else:
            head_edges[("bridge", "1")] = [{"name": "existing-plugin"}]
            base_edges[("bridge", "1")] = [{"name": "existing-plugin"}]
        base_optional[("parent", "1")]["new-extra"] = list(parent_optional["new-extra"])
        head_optional[("parent", "1")]["new-extra"] = list(parent_optional["new-extra"])
        if variant in {"reviewed-transitive", "reviewed-mutual-cycle"}:
            constraints = ["bridge>=1", "existing-plugin>=1"]
        elif variant in {"transitive-existing", "selected-nested-extra", "reviewed-cyclic-extra", "mutual-cycle"}:
            constraints = ["bridge>=1"]
    elif variant in {"composed-extra", "reviewed-composed-extra"}:
        parent_optional["new-extra"] = [{"name": "parent", "extra": ["nested"]}]
        parent_optional["nested"] = [{"name": "existing-plugin"}]
        base_optional[("parent", "1")] = dict(parent_optional)
        head_optional[("parent", "1")] = dict(parent_optional)
        if variant == "reviewed-composed-extra":
            constraints = ["existing-plugin>=1"]
    elif variant in {"wrong-marker", "matching-marker"}:
        head_requirements[-1] += "; python_version >= '3.11'"
        markers = {("existing-plugin", "1"): ["python_full_version >= '3.11'"]}
        suffix = "< '3.11'" if variant == "wrong-marker" else ">= '3.11'"
        constraints = ["existing-plugin>=1; python_version " + suffix]
    elif variant == "unchanged-extra":
        base_requirements[-1] = "parent[new-extra]"
        head_requirements = ["patch-me>=1.1", "parent[new-extra]"]
    elif variant == "ambiguous-edge":
        parent_optional["new-extra"] = [{"name": "existing-plugin", "extra": "not-a-list"}]

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=[("patch-me", "1"), *packages],
        head_packages=[("patch-me", "1.1"), *packages],
        base_dependency_groups=base_groups,
        head_dependency_groups=head_groups,
        head_constraints=constraints,
        base_resolution_markers=markers,
        head_resolution_markers=markers,
        base_lock_dependencies=base_edges,
        head_lock_dependencies=head_edges,
        base_lock_optional_dependencies=base_optional,
        head_lock_optional_dependencies=head_optional,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("optional-to-runtime", False, id="optional-direct-floor-cannot-review-new-runtime-audience"),
        pytest.param("runtime-reviewed", True, id="reviewed-runtime-floor-covers-new-runtime-audience"),
        pytest.param("protected-reviewed", True, id="protected-floor-can-review-new-runtime-audience"),
        pytest.param("protected-too-low", False, id="protected-review-must-reach-the-actual-locked-release"),
        pytest.param("different-optional", False, id="one-optional-group-cannot-review-another-group-audience"),
        pytest.param("same-optional", True, id="same-optional-group-retains-its-reviewed-direct-audience"),
    ],
)
def test_new_extra_direct_dependency_boundaries_cover_their_actual_audience(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    base_requirements = ["patch-me>=1", "parent"]
    head_requirements = ["patch-me>=1.1", "parent", "parent[feature]"]
    base_optional = {"private": ["plugin>=1"]}
    head_optional = {"private": ["plugin>=1"]}
    constraints: list[str] | None = None

    if variant == "runtime-reviewed":
        base_requirements.append("plugin>=2")
        head_requirements.append("plugin>=2")
    elif variant == "protected-reviewed":
        constraints = ["plugin>=2"]
    elif variant == "protected-too-low":
        constraints = ["plugin>=1"]
    elif variant == "different-optional":
        base_requirements, head_requirements = ["patch-me>=1"], ["patch-me>=1.1"]
        base_optional = {"private": ["plugin>=1"], "public": ["parent"]}
        head_optional = {"private": ["plugin>=1"], "public": ["parent", "parent[feature]"]}
    elif variant == "same-optional":
        base_requirements, head_requirements = ["patch-me>=1"], ["patch-me>=1.1"]
        base_optional = {"public": ["parent", "plugin>=2"]}
        head_optional = {"public": ["parent", "parent[feature]", "plugin>=2"]}

    edges: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {
        ("parent", "1"): {"feature": [{"name": "plugin"}]}
    }
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=[("patch-me", "1"), ("parent", "1"), ("plugin", "2")],
        head_packages=[("patch-me", "1.1"), ("parent", "1"), ("plugin", "2")],
        base_optional_groups=base_optional,
        head_optional_groups=head_optional,
        head_constraints=constraints,
        base_lock_optional_dependencies=edges,
        head_lock_optional_dependencies=edges,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


def test_cyclic_extra_dependency_graph_retains_bounded_pending_states(tmp_path: Path) -> None:
    edges: list[dict[str, object]] = [{"name": "parent", "extra": ["new-extra"]} for _ in range(4097)]
    optional: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {("parent", "1"): {"new-extra": edges}}
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1", "parent"],
        head_requirements=["patch-me>=1.1", "parent", "parent[new-extra]"],
        base_packages=[("patch-me", "1"), ("parent", "1")],
        head_packages=[("patch-me", "1.1"), ("parent", "1")],
        base_lock_optional_dependencies=optional,
        head_lock_optional_dependencies=optional,
    )
    assert result.returncode != 0
    assert "Unbounded published security dependency graph" in result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("published-wildcard", True, id="published-marker-split-preserves-existing-vulnerable-series"),
        pytest.param("protected-wildcard", True, id="protected-marker-split-preserves-existing-vulnerable-series"),
        pytest.param("canonical-wildcard", True, id="split-accepts-canonical-equivalent-wildcard-prefix"),
        pytest.param("reordered-wildcard", True, id="split-accepts-reordered-identical-wildcard-exclusions"),
        pytest.param("published-removed", False, id="published-split-cannot-drop-vulnerable-series-exclusion"),
        pytest.param("protected-removed", False, id="protected-split-cannot-drop-vulnerable-series-exclusion"),
        pytest.param("narrowed-wildcard", False, id="split-cannot-narrow-existing-vulnerable-series-exclusion"),
        pytest.param("wrong-epoch", False, id="split-cannot-move-wildcard-exclusion-to-another-epoch"),
        pytest.param("upper-removed", False, id="wildcard-marker-split-still-preserves-existing-upper-bound"),
        pytest.param("post-wildcard", False, id="split-rejects-ambiguous-post-release-wildcard"),
    ],
)
def test_marker_context_splits_preserve_canonical_wildcard_security_exclusions(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    old = "danger>=1,<3,!=2.0.*"
    low = "danger>=1.6,<3,!=2.0.*; python_version < '3.11'"
    high = "danger>=2.6,<3,!=2.0.*; python_version >= '3.11'"
    protected = variant.startswith("protected-")

    if variant == "canonical-wildcard":
        low = "danger>=1.6,<3,!=02.00.*; python_version < '3.11'"
    elif variant == "reordered-wildcard":
        low = "danger!=2.0.*,<3,>=1.6; python_version < '3.11'"
    elif variant in {"published-removed", "protected-removed"}:
        low = "danger>=1.6,<3; python_version < '3.11'"
    elif variant == "narrowed-wildcard":
        low = "danger>=1.6,<3,!=2.0.1.*; python_version < '3.11'"
    elif variant == "wrong-epoch":
        low = "danger>=1.6,<3,!=1!2.0.*; python_version < '3.11'"
    elif variant == "upper-removed":
        low = "danger>=1.6,!=2.0.*; python_version < '3.11'"
    elif variant == "post-wildcard":
        low = "danger>=1.6,<3,!=2.0.post1.*; python_version < '3.11'"

    base_optional = None if protected else {"feature": [old]}
    head_optional = None if protected else {"feature": [low, high]}
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[],
        head_requirements=[],
        base_packages=[("danger", "1.5"), ("danger", "2.5")],
        head_packages=[("danger", "1.6"), ("danger", "2.6")],
        base_optional_groups=base_optional,
        head_optional_groups=head_optional,
        base_constraints=[old] if protected else None,
        head_constraints=[low, high] if protected else None,
        base_resolution_markers={
            ("danger", "1.5"): ["python_full_version < '3.11'"],
            ("danger", "2.5"): ["python_full_version >= '3.11'"],
        },
        head_resolution_markers={
            ("danger", "1.6"): ["python_full_version < '3.11'"],
            ("danger", "2.6"): ["python_full_version >= '3.11'"],
        },
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("published-lower-dropped", False, id="published-compatible-release-cannot-drop-lower-floor"),
        pytest.param("published-upper-dropped", False, id="published-compatible-release-cannot-drop-series-ceiling"),
        pytest.param("protected-upper-dropped", False, id="protected-compatible-release-cannot-drop-series-ceiling"),
        pytest.param("equivalent-expanded", True, id="compatible-release-can-expand-to-equivalent-explicit-bounds"),
        pytest.param("tighter-series", True, id="compatible-release-can-tighten-without-dropping-locked-release"),
        pytest.param("zero-precision", False, id="compatible-release-trailing-zero-preserves-precision-ceiling"),
        pytest.param("epoch-ceiling", False, id="compatible-release-preserves-epoch-aware-series-ceiling"),
        pytest.param("post-floor", False, id="compatible-release-preserves-post-release-lower-floor"),
        pytest.param("single-component", False, id="single-component-compatible-release-fails-closed"),
        pytest.param("wildcard", False, id="wildcard-compatible-release-fails-closed"),
    ],
)
def test_compatible_release_requirements_preserve_reviewed_security_bounds(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    original = "safe~=1.4"
    replacement = "safe>=1.4,<2"
    locked = "1.5"
    protected = variant.startswith("protected-")

    if variant == "published-lower-dropped":
        replacement = "safe>=1,<2"
    elif variant in {"published-upper-dropped", "protected-upper-dropped"}:
        replacement = "safe>=1.4"
    elif variant == "tighter-series":
        replacement = "safe~=1.5"
    elif variant == "zero-precision":
        original = "safe~=1.4.0"
        replacement = "safe>=1.4,<2"
        locked = "1.4.5"
    elif variant == "epoch-ceiling":
        original = "safe~=1!1.4"
        replacement = "safe>=1!1.4"
        locked = "1!1.5"
    elif variant == "post-floor":
        original = "safe~=1.4.post1"
        replacement = "safe>=1.4,<2"
    elif variant == "single-component":
        original = "safe~=1"
    elif variant == "wildcard":
        original = "safe~=1.4.*"

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1"] + ([] if protected else [original]),
        head_requirements=["patch-me>=1.1"] + ([] if protected else [replacement]),
        base_packages=[("patch-me", "1"), ("safe", locked)],
        head_packages=[("patch-me", "1.1"), ("safe", locked)],
        base_constraints=[original] if protected else None,
        head_constraints=[replacement] if protected else None,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("previous", "updated"),
    [
        pytest.param("danger >= 1.0 ", "danger >= 2.0 ", id="whitespace-padded-security-floor"),
        pytest.param(
            "danger >= 1.0 , >= 1.5 ",
            "danger >= 1.0 , >= 2.0 ",
            id="whitespace-padded-redundant-security-floors",
        ),
    ],
)
def test_security_floor_parser_strips_requirement_whitespace(tmp_path: Path, previous: str, updated: str) -> None:
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[previous],
        head_requirements=[updated],
        base_packages=[("danger", "1.5")],
        head_packages=[("danger", "2.0")],
    )
    assert result.returncode == 0, result.stdout + result.stderr


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


def test_reviewed_root_build_still_runs_with_source_distribution_builds_disabled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    log = fake_uv(tmp_path, monkeypatch)
    monkeypatch.setenv("UV_NO_BUILD", "1")
    result = subprocess.run([str(ROOT / "scripts/build"), "--out-dir", str(tmp_path / "dist")], check=False)
    calls = [json.loads(line)["args"] for line in log.read_text().splitlines()]
    assert result.returncode == 0
    assert calls[0][0] == "export"
    assert calls[1][0] == "build"
    assert "--no-sources" in calls[1]


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("runtime", True, id="published-runtime-or-marker-receives-security-patch"),
        pytest.param("optional", True, id="published-optional-or-marker-receives-security-patch"),
        pytest.param("constraint", True, id="reviewed-uv-constraint-or-marker-receives-security-patch"),
        pytest.param("build", True, id="reviewed-build-constraint-or-marker-receives-security-patch"),
        pytest.param("group", True, id="reviewed-development-group-or-marker-receives-security-patch"),
        pytest.param("grouped", True, id="grouped-marker-disjunction-preserves-safe-precedence"),
        pytest.param("precedence", True, id="ungrouped-marker-disjunction-preserves-and-precedence"),
        pytest.param("reordered", True, id="reordered-marker-disjunction-preserves-original-source-scope"),
        pytest.param("duplicate", True, id="duplicate-marker-disjunction-arm-is-idempotent"),
        pytest.param("subsumed", True, id="subsumed-marker-disjunction-arm-preserves-source-scope"),
        pytest.param("membership", True, id="membership-marker-disjunction-remains-bounded"),
        pytest.param("widen-single", False, id="single-marker-source-cannot-gain-unreviewed-or-arm"),
        pytest.param("widen-existing", False, id="existing-disjunction-cannot-gain-unreviewed-or-arm"),
        pytest.param("dropped-arm", False, id="existing-disjunction-cannot-drop-supported-source-arm"),
        pytest.param("lowered-arm", False, id="split-disjunction-arm-cannot-lower-original-security-floor"),
        pytest.param("unsafe-call", False, id="disjunction-cannot-hide-executable-marker-expression"),
        pytest.param("unsafe-constant", False, id="disjunction-cannot-hide-constant-marker-expression"),
        pytest.param("unsafe-unary", False, id="disjunction-cannot-hide-unary-marker-expression"),
        pytest.param("unsafe-chained", False, id="disjunction-cannot-hide-chained-marker-comparison"),
        pytest.param("malformed-membership", False, id="disjunction-cannot-hide-ambiguous-membership"),
        pytest.param("unbounded", False, id="unbounded-marker-disjunction-fails-closed"),
    ],
)
def test_security_updates_preserve_bounded_disjunctive_requirement_markers(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    low = "python_version < '3.11'"
    windows = "sys_platform == 'win32'"
    marker = low + " or " + windows
    head_marker = marker
    base_floor, head_floor = "1", "2"
    before, after = "1", "2"
    head_entries: list[str] | None = None
    scope = variant if variant in {"optional", "constraint", "build", "group"} else "runtime"

    if variant == "grouped":
        marker = "(" + low + " or " + windows + ") and python_version >= '3.10'"
        head_marker = marker
    elif variant == "precedence":
        marker = low + " or " + windows + " and python_version >= '3.10'"
        head_marker = marker
    elif variant == "reordered":
        head_marker = windows + " or " + low
    elif variant == "duplicate":
        marker = low + " or " + low
        head_marker = marker
    elif variant == "subsumed":
        marker = low + " or (" + low + " and " + windows + ")"
        head_marker = marker
    elif variant == "membership":
        marker = "python_version in '3.10, 3.11' or " + windows
        head_marker = marker
    elif variant in {"widen-single", "widen-existing", "dropped-arm", "lowered-arm"}:
        base_floor = head_floor = before = after = "2"
        if variant == "widen-single":
            marker, head_marker = low, marker
        elif variant == "widen-existing":
            head_marker = marker + " or sys_platform == 'darwin'"
        elif variant == "dropped-arm":
            head_marker = low
        else:
            head_entries = ["danger>=1; " + low, "danger>=2; " + windows]
    elif variant == "unsafe-call":
        head_marker = low + " or __import__('os').system('true')"
    elif variant == "unsafe-constant":
        head_marker = low + " or True"
    elif variant == "unsafe-unary":
        head_marker = low + " or not " + windows
    elif variant == "unsafe-chained":
        head_marker = low + " or python_version < '3.11' < '3.12'"
    elif variant == "malformed-membership":
        head_marker = low + " or python_version in '3.10,,3.11'"
    elif variant == "unbounded":
        head_marker = " or ".join("sys_platform == 'platform" + str(index) + "'" for index in range(129))

    previous = "danger>=" + base_floor + "; " + marker
    current = "danger>=" + head_floor + "; " + head_marker
    head_entries = [current] if head_entries is None else head_entries
    base_requirements = [previous] if scope == "runtime" else []
    head_requirements = head_entries if scope == "runtime" else []
    base_optional = {"feature": [previous]} if scope == "optional" else None
    head_optional = {"feature": head_entries} if scope == "optional" else None
    base_constraints = [previous] if scope == "constraint" else None
    head_constraints = head_entries if scope == "constraint" else None
    base_build = [previous] if scope == "build" else None
    head_build = head_entries if scope == "build" else None
    base_groups = {"reviewed": [previous]} if scope == "group" else None
    head_groups = {"reviewed": head_entries} if scope == "group" else None
    resolution = "python_full_version == '3.10.*'"
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=[("danger", before)],
        head_packages=[("danger", after)],
        base_optional_groups=base_optional,
        head_optional_groups=head_optional,
        base_constraints=base_constraints,
        head_constraints=head_constraints,
        base_build_constraints=base_build,
        head_build_constraints=head_build,
        base_dependency_groups=base_groups,
        head_dependency_groups=head_groups,
        base_resolution_markers={("danger", before): [resolution]},
        head_resolution_markers={("danger", after): [resolution]},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("runtime", True, id="existing-published-marker-can-split-into-supported-domains"),
        pytest.param("optional", True, id="existing-optional-marker-can-split-within-original-group"),
        pytest.param("constraint", True, id="existing-uv-constraint-marker-can-split-within-original-scope"),
        pytest.param("group", True, id="existing-development-marker-can-split-within-original-group"),
        pytest.param("implicit-lower", True, id="marked-split-can-use-implicit-supported-python-lower-bound"),
        pytest.param("gap", False, id="marked-split-cannot-drop-supported-original-resolution-domain"),
        pytest.param("widened", False, id="marked-split-cannot-widen-outside-original-marker"),
        pytest.param("overlap", False, id="marked-split-cannot-overlap-supported-resolution-subdomains"),
        pytest.param("partial", False, id="marked-split-cannot-cover-only-one-supported-platform"),
        pytest.param("weakened", False, id="marked-split-cannot-lower-original-security-floor"),
        pytest.param("upper-removed", False, id="marked-split-cannot-remove-existing-upper-bound"),
        pytest.param("exclusion-removed", False, id="marked-split-cannot-remove-existing-wildcard-exclusion"),
        pytest.param("moved-group", False, id="marked-split-cannot-move-existing-optional-group"),
        pytest.param("moved-extra", False, id="marked-split-cannot-replace-original-requested-extra"),
    ],
)
def test_security_floors_can_safely_split_existing_marked_resolution_domains(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    original = "danger>=1,<3,!=2.0.*; python_version < '3.14'"
    low = "danger>=1.6,<3,!=2.0.*; python_version >= '3.10' and python_version < '3.11'"
    high = "danger>=2.6,<3,!=2.0.*; python_version >= '3.11' and python_version < '3.14'"
    scope = variant if variant in {"optional", "constraint", "group"} else "runtime"

    if variant == "implicit-lower":
        low = "danger>=1.6,<3,!=2.0.*; python_version < '3.11'"
    elif variant == "gap":
        low = ""
    elif variant == "widened":
        high = "danger>=2.6,<3,!=2.0.*; python_version >= '3.11'"
    elif variant == "overlap":
        low = "danger>=1.6,<3,!=2.0.*; python_version >= '3.10' and python_version < '3.12'"
    elif variant == "partial":
        low += " and sys_platform == 'linux'"
    elif variant == "weakened":
        low = "danger>=0.9,<3,!=2.0.*; python_version >= '3.10' and python_version < '3.11'"
    elif variant == "upper-removed":
        low = low.replace(",<3", "")
    elif variant == "exclusion-removed":
        low = low.replace(",!=2.0.*", "")
    elif variant == "moved-extra":
        original = original.replace("danger>=", "danger[secure]>=")
        low = low.replace("danger>=", "danger[other]>=")
        high = high.replace("danger>=", "danger[other]>=")

    replacements = [value for value in (low, high) if value]
    base_requirements = [original] if scope == "runtime" else []
    head_requirements = replacements if scope == "runtime" else []
    base_optional = {"feature": [original]} if scope == "optional" or variant == "moved-group" else None
    head_optional = (
        {"different": replacements}
        if variant == "moved-group"
        else {"feature": replacements}
        if scope == "optional"
        else None
    )
    if variant == "moved-group":
        base_requirements = head_requirements = []
    base_constraints = [original] if scope == "constraint" else None
    head_constraints = replacements if scope == "constraint" else None
    base_groups = {"reviewed": [original]} if scope == "group" else None
    head_groups = {"reviewed": replacements} if scope == "group" else None
    low_domain = "python_full_version >= '3.10' and python_full_version < '3.11'"
    high_domain = "python_full_version >= '3.11'"
    if scope in {"constraint", "group"}:
        high_domain += " and python_full_version < '3.14'"
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=[("danger", "1.5"), ("danger", "2.5")],
        head_packages=[("danger", "1.6"), ("danger", "2.6")],
        base_optional_groups=base_optional,
        head_optional_groups=head_optional,
        base_constraints=base_constraints,
        head_constraints=head_constraints,
        base_dependency_groups=base_groups,
        head_dependency_groups=head_groups,
        base_resolution_markers={("danger", "1.5"): [low_domain], ("danger", "2.5"): [high_domain]},
        head_resolution_markers={("danger", "1.6"): [low_domain], ("danger", "2.6"): [high_domain]},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("both", True, id="every-supported-major-can-receive-security-patch-together"),
        pytest.param("missing-v1-exclusion", False, id="joint-patch-must-exclude-entire-vulnerable-v1-series"),
        pytest.param("missing-v2-exclusion", False, id="joint-patch-must-exclude-entire-vulnerable-v2-series"),
        pytest.param("drops-patched-v1", False, id="joint-patch-cannot-exclude-other-patched-supported-major"),
        pytest.param("unchanged-v1-floor", False, id="joint-patch-must-raise-preexisting-v1-security-floor"),
        pytest.param("unchanged-v2-floor", False, id="joint-patch-must-raise-preexisting-v2-security-floor"),
        pytest.param("missing-old-group", False, id="joint-patch-cannot-trust-newly-added-protected-context"),
        pytest.param("removed-group", False, id="joint-patch-cannot-remove-existing-supported-major-context"),
        pytest.param("missing-upper", False, id="joint-patch-must-preserve-independent-branch-upper-bound"),
        pytest.param("downgrade", False, id="joint-patch-cannot-downgrade-one-supported-major"),
        pytest.param("removed-branch", False, id="joint-patch-cannot-remove-one-supported-locked-major"),
        pytest.param("single-branch", False, id="published-exclusion-path-requires-distinct-supported-peer"),
    ],
)
def test_security_updates_can_patch_all_independent_supported_major_branches(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    published = "danger>=1.5,<3"
    exclusions = ["!=1.5.*", *("!=2." + str(minor) + ".*" for minor in range(6))]
    updated_published = published + "," + ",".join(exclusions)
    base_groups = {
        "danger-v1": ["danger>=1.5,<2"],
        "danger-v2": ["danger>=2.5,<3"],
    }
    head_groups = {
        "danger-v1": ["danger>=1.6,<2"],
        "danger-v2": ["danger>=2.6,<3"],
    }
    previous = [("danger", "1.5"), ("danger", "2.5")]
    current = [("danger", "1.6"), ("danger", "2.6")]

    if variant == "missing-v1-exclusion":
        updated_published = updated_published.replace(",!=1.5.*", "")
    elif variant == "missing-v2-exclusion":
        updated_published = updated_published.replace(",!=2.4.*", "")
    elif variant == "drops-patched-v1":
        updated_published += ",!=1.6.*"
    elif variant == "unchanged-v1-floor":
        head_groups["danger-v1"] = ["danger>=1.5,<2"]
    elif variant == "unchanged-v2-floor":
        head_groups["danger-v2"] = ["danger>=2.5,<3"]
    elif variant == "missing-old-group":
        base_groups.pop("danger-v2")
    elif variant == "removed-group":
        head_groups.pop("danger-v2")
    elif variant == "missing-upper":
        head_groups["danger-v2"] = ["danger>=2.6"]
    elif variant == "downgrade":
        current[1] = ("danger", "2.4")
    elif variant == "removed-branch":
        current = [("danger", "2.6")]
    elif variant == "single-branch":
        base_groups.pop("danger-v2")
        head_groups.pop("danger-v2")
        previous = [("danger", "1.5")]
        current = [("danger", "1.6")]

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[published],
        head_requirements=[updated_published],
        base_packages=previous,
        head_packages=current,
        base_dependency_groups=base_groups,
        head_dependency_groups=head_groups,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("unchanged", True, id="independent-overlapping-or-sources-can-remain-unchanged"),
        pytest.param("raised", True, id="independent-overlapping-or-sources-can-both-raise-their-floor"),
        pytest.param("widened", False, id="overlapping-source-cannot-borrow-another-source-to-widen"),
        pytest.param("dropped", False, id="overlapping-source-cannot-drop-its-own-original-marker-arm"),
        pytest.param("swapped-floor", False, id="overlapping-sources-cannot-swap-a-lower-security-floor"),
        pytest.param("removed-source", False, id="overlapping-sources-cannot-remove-independent-source"),
    ],
)
def test_security_marker_source_lineage_preserves_independent_overlapping_declarations(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    shared = "sys_platform == 'linux'"
    low = "python_version < '3.11'"
    high = "python_version >= '3.11'"
    base = ["danger>=1; " + shared + " or " + low, "danger>=2; " + shared + " or " + high]
    head = ["danger>=3; " + shared + " or " + low, "danger>=3; " + shared + " or " + high]
    before, after = "2", "3"
    if variant == "unchanged":
        head = list(base)
        after = before
    elif variant == "widened":
        head[0] += " or os_name == 'nt'"
    elif variant == "dropped":
        head[0] = "danger>=3; " + shared
    elif variant == "swapped-floor":
        base = ["danger>=2; " + shared + " or " + low, "danger>=3; " + shared + " or " + high]
        head = ["danger>=3; " + shared + " or " + low, "danger>=2; " + shared + " or " + high]
        before = after = "3"
    elif variant == "removed-source":
        head.pop()
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base,
        head_requirements=head,
        base_packages=[("danger", before)],
        head_packages=[("danger", after)],
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    "variant",
    [
        pytest.param("disjoint", id="unbounded-protected-source-cannot-move-to-disjoint-domain"),
        pytest.param("removed", id="unbounded-protected-source-cannot-disappear-entirely"),
        pytest.param("widened", id="unbounded-protected-source-cannot-gain-unreviewed-domain"),
        pytest.param("add-protected", id="retained-protected-source-cannot-add-unbounded-disjoint-source"),
        pytest.param("add-runtime", id="retained-runtime-source-cannot-add-unbounded-disjoint-source"),
    ],
)
def test_unbounded_protected_marker_sources_preserve_their_reviewed_domain(tmp_path: Path, variant: str) -> None:
    original = "danger; python_version < '3.11' or sys_platform == 'linux'"
    if variant == "disjoint":
        updated = ["danger; python_version >= '3.11' and sys_platform != 'linux'"]
    elif variant == "removed":
        updated = []
    elif variant in {"add-protected", "add-runtime"}:
        updated = [original, "danger; os_name == 'nt'"]
    else:
        updated = [original + " or os_name == 'nt'"]
    runtime = variant == "add-runtime"
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[original] if runtime else [],
        head_requirements=updated if runtime else [],
        base_packages=[("danger", "2")],
        head_packages=[("danger", "2")],
        base_dependency_groups=None if runtime else {"reviewed": [original]},
        head_dependency_groups=None if runtime else {"reviewed": updated},
    )
    assert result.returncode == 1, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("runtime", True, id="published-or-source-can-split-into-independently-raised-arms"),
        pytest.param("group", True, id="protected-or-source-can-split-into-independently-raised-arms"),
        pytest.param("drop", False, id="or-source-partition-cannot-drop-original-supported-arm"),
        pytest.param("widen", False, id="or-source-partition-cannot-widen-beyond-original-union"),
        pytest.param("lower", False, id="or-source-partition-cannot-lower-any-original-floor"),
        pytest.param("overlap", False, id="or-source-partition-cannot-overlap-independent-replacements"),
    ],
)
def test_security_marker_disjunction_can_split_into_reviewed_source_declarations(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    low = "python_version < '3.11'"
    high = "python_version >= '3.11' and python_version < '3.14'"
    original = "danger>=1,<3; " + low + " or " + high
    first = "danger>=1.6,<3; " + low
    second = "danger>=2.6,<3; " + high
    if variant == "drop":
        second = ""
    elif variant == "widen":
        second = "danger>=2.6,<3; python_version >= '3.11'"
    elif variant == "lower":
        second = "danger>=0.5,<3; " + high
    elif variant == "overlap":
        first = "danger>=1.6,<3; python_version < '3.12'"
    updated = [value for value in (first, second) if value]
    protected = variant == "group"
    low_domain = "python_full_version < '3.11'"
    high_domain = "python_full_version >= '3.11' and python_full_version < '3.14'"
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [original],
        head_requirements=[] if protected else updated,
        base_packages=[("danger", "1.5"), ("danger", "2.5")],
        head_packages=[("danger", "1.6"), ("danger", "2.6")],
        base_dependency_groups={"reviewed": [original]} if protected else None,
        head_dependency_groups={"reviewed": updated} if protected else None,
        base_resolution_markers={("danger", "1.5"): [low_domain], ("danger", "2.5"): [high_domain]},
        head_resolution_markers={("danger", "1.6"): [low_domain], ("danger", "2.6"): [high_domain]},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


def test_direct_disjunction_preserves_symbolic_extra_markers(tmp_path: Path) -> None:
    marker = "extra == 'feature' or sys_platform == 'win32'"
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["danger[secure]>=1; " + marker],
        head_requirements=["danger[secure]>=2; " + marker],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("reviewed", True, id="new-extra-can-review-exact-newly-exposed-locked-package"),
        pytest.param("fake-extra", False, id="unrelated-new-extra-cannot-approve-different-protected-source"),
        pytest.param("wrong-marker", False, id="new-extra-review-boundary-must-cover-actual-exposed-marker"),
        pytest.param("low-floor", False, id="new-extra-review-boundary-must-reach-actual-locked-release"),
        pytest.param("floorless", False, id="new-extra-cannot-approve-unbounded-protected-source"),
    ],
)
def test_requested_extra_source_exceptions_validate_the_exact_exposed_package(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    marker = "python_version >= '3.11'"
    requirement = "danger>=2; " + marker
    target = "danger"
    packages = [("parent", "1"), ("danger", "2")]
    groups = {"reviewed": ["danger"]}
    constraints: list[str]

    if variant == "wrong-marker":
        requirement = "danger>=2; python_version < '3.11'"
    elif variant == "low-floor":
        requirement = "danger>=1; " + marker
    elif variant == "floorless":
        requirement = "danger; " + marker
    elif variant == "fake-extra":
        target = "safe-plugin"
        packages.append(("safe-plugin", "1"))
        groups["reviewed"].append("safe-plugin")

    constraints = [requirement]
    if variant == "fake-extra":
        constraints.append("safe-plugin>=1")
    optional: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {
        ("parent", "1"): {"feature": [{"name": target}]}
    }
    domains = {("danger", "2"): ["python_full_version >= '3.11'"]}
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["parent"],
        head_requirements=["parent", "parent[feature]; " + marker],
        base_packages=packages,
        head_packages=packages,
        base_dependency_groups=groups,
        head_dependency_groups=groups,
        head_constraints=constraints,
        base_resolution_markers=domains,
        head_resolution_markers=domains,
        base_lock_optional_dependencies=optional,
        head_lock_optional_dependencies=optional,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("transitive-refined", True, id="unchanged-transitive-broad-domain-can-refine-semantically"),
        pytest.param("transitive-coalesced", True, id="unchanged-transitive-split-domains-can-coalesce-semantically"),
        pytest.param("direct-refined", True, id="unchanged-direct-release-can-refine-its-lock-domain"),
        pytest.param("protected-refined", True, id="unchanged-protected-release-can-refine-its-lock-domain"),
        pytest.param("protected-coalesced", True, id="unchanged-protected-release-can-coalesce-lock-domains"),
        pytest.param("platform-refined", True, id="equivalent-platform-complements-preserve-original-domain"),
        pytest.param("membership-refined", True, id="equivalent-membership-alternatives-preserve-domain"),
        pytest.param("independent-majors", True, id="domain-refinement-preserves-coexisting-supported-majors"),
        pytest.param("reviewed-upgrade", True, id="refined-upgrade-remains-covered-by-reviewed-security-floor"),
        pytest.param("complementary-upgrade", True, id="refined-upgrade-accepts-complementary-reviewed-floors"),
        pytest.param("unreviewed-upgrade", False, id="domain-refinement-cannot-hide-unreviewed-upgraded-release"),
        pytest.param("partial-upgrade", False, id="reviewed-floor-cannot-cover-only-one-refined-domain"),
        pytest.param("gap", False, id="semantic-refinement-cannot-drop-an-original-resolution-region"),
        pytest.param("widened", False, id="semantic-refinement-cannot-add-an-unreviewed-resolution-region"),
        pytest.param("swapped", False, id="semantic-refinement-cannot-swap-releases-across-domains"),
        pytest.param("unbounded", False, id="unbounded-common-resolution-refinement-fails-closed"),
    ],
)
def test_security_resolution_domains_compare_semantic_release_coverage(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    broad = "python_full_version < '3.12'"
    low = "python_full_version < '3.11'"
    high = "python_full_version >= '3.11' and python_full_version < '3.12'"
    previous = [("danger", "2")]
    current = [("danger", "2")]
    base_markers: dict[tuple[str, str], list[str]] = {("danger", "2"): [broad]}
    head_markers: dict[tuple[str, str], list[str]] = {("danger", "2"): [low, high]}
    base_requirements = ["patch-me>=1"]
    head_requirements = ["patch-me>=1.1"]
    base_constraints: list[str] | None = None
    head_constraints: list[str] | None = None

    if variant in {"transitive-coalesced", "protected-coalesced"}:
        base_markers, head_markers = head_markers, base_markers
    if variant == "direct-refined":
        base_requirements.append("danger>=2")
        head_requirements.append("danger>=2")
    elif variant in {"protected-refined", "protected-coalesced"}:
        base_constraints = ["danger>=2"]
        head_constraints = ["danger>=2"]
    elif variant == "platform-refined":
        head_markers = {
            ("danger", "2"): [broad + " and sys_platform == 'linux'", broad + " and sys_platform != 'linux'"]
        }
    elif variant == "membership-refined":
        base_markers = {("danger", "2"): ["python_version in '3.10, 3.11'"]}
        head_markers = {
            ("danger", "2"): ["python_version == '3.1'", "python_version == '3.10'", "python_version == '3.11'"]
        }
    elif variant == "independent-majors":
        previous = current = [("danger", "1.5"), ("danger", "2.5")]
        base_markers = {(name, release): [broad] for name, release in previous}
        head_markers = {(name, release): [low, high] for name, release in current}
    elif variant in {"reviewed-upgrade", "complementary-upgrade", "unreviewed-upgrade", "partial-upgrade"}:
        current = [("danger", "3")]
        head_markers = {("danger", "3"): [low, high]}
        if variant == "reviewed-upgrade":
            head_constraints = ["danger>=3"]
        elif variant == "complementary-upgrade":
            head_constraints = ["danger>=3; python_version < '3.11'", "danger>=3; python_version >= '3.11'"]
        elif variant == "partial-upgrade":
            head_constraints = ["danger>=3; python_version < '3.11'"]
    elif variant == "gap":
        head_markers = {("danger", "2"): [low]}
    elif variant == "widened":
        head_markers = {("danger", "2"): [low, high, "python_full_version >= '3.12'"]}
    elif variant == "swapped":
        previous = [("danger", "1"), ("danger", "2")]
        current = [("danger", "1"), ("danger", "2")]
        base_markers = {("danger", "1"): [low], ("danger", "2"): [high]}
        head_markers = {("danger", "1"): [high], ("danger", "2"): [low]}
    elif variant == "unbounded":
        head_markers = {
            ("danger", "2"): [broad + " and sys_platform == 'platform" + str(index) + "'" for index in range(129)]
        }

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=[("patch-me", "1"), *previous],
        head_packages=[("patch-me", "1.1"), *current],
        base_constraints=base_constraints,
        head_constraints=head_constraints,
        base_resolution_markers=base_markers,
        head_resolution_markers=head_markers,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("unrelated-root", True, id="new-extra-does-not-review-unrelated-runtime-root-transitive"),
        pytest.param("same-parent-normal", True, id="new-extra-does-not-review-parent-normal-dependency"),
        pytest.param("related-unreviewed", False, id="package-actually-reachable-from-new-extra-needs-review"),
        pytest.param("related-reviewed", True, id="reviewed-extra-package-does-not-impose-unrelated-bound"),
        pytest.param("wrong-audience", False, id="extra-review-must-intersect-actual-requested-audience"),
        pytest.param("partial-platform", False, id="extra-review-cannot-cover-only-one-exposed-platform"),
        pytest.param("complementary-platform", True, id="complementary-extra-reviews-cover-all-exposed-platforms"),
        pytest.param("wrong-root", False, id="review-on-unrelated-root-cannot-secure-actual-extra-package"),
        pytest.param("low-floor", False, id="actual-extra-review-floor-must-reach-selected-release"),
    ],
)
def test_requested_extra_review_only_covers_packages_reachable_through_that_extra(
    tmp_path: Path, variant: str, accepted: bool
) -> None:
    base_requirements = ["patch-me>=1", "parent"]
    head_requirements = ["patch-me>=1.1", "parent", "parent[feature]"]
    previous = [("patch-me", "1"), ("parent", "1")]
    current = [("patch-me", "1.1"), ("parent", "1"), ("unrelated", "1")]
    head_edges: dict[tuple[str, str], list[dict[str, object]]] = {("patch-me", "1.1"): [{"name": "unrelated"}]}
    optional: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {("parent", "1"): {"feature": []}}
    constraints: list[str] | None = None
    markers: dict[tuple[str, str], list[str]] | None = None

    if variant == "same-parent-normal":
        head_edges = {("parent", "1"): [{"name": "unrelated"}]}
    elif variant not in {"unrelated-root", "same-parent-normal"}:
        current.append(("extra-package", "2"))
        optional[("parent", "1")]["feature"].append({"name": "extra-package"})
        markers = {("extra-package", "2"): ["python_full_version >= '3.10'"]}
        if variant == "related-reviewed":
            constraints = ["extra-package>=2"]
        elif variant == "wrong-audience":
            head_requirements[-1] += "; python_version >= '3.11'"
            constraints = ["extra-package>=2; python_version < '3.11'"]
        elif variant == "partial-platform":
            constraints = ["extra-package>=2; sys_platform == 'linux'"]
        elif variant == "complementary-platform":
            constraints = [
                "extra-package>=2; sys_platform == 'linux'",
                "extra-package>=2; sys_platform != 'linux'",
            ]
        elif variant == "wrong-root":
            constraints = ["unrelated>=1"]
        elif variant == "low-floor":
            constraints = ["extra-package>=1"]

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=base_requirements,
        head_requirements=head_requirements,
        base_packages=previous,
        head_packages=current,
        head_constraints=constraints,
        head_resolution_markers=markers,
        head_lock_dependencies=head_edges,
        base_lock_optional_dependencies=optional,
        head_lock_optional_dependencies=optional,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("substring", True, id="platform-membership-covers-actual-arm-substring"),
        pytest.param("complete-token", True, id="platform-membership-still-covers-complete-token"),
        pytest.param("overlapping-prefix", True, id="overlapping-platform-membership-covers-shorter-token"),
        pytest.param("overlapping-long", True, id="overlapping-platform-membership-covers-longer-token"),
        pytest.param("overlapping-short", True, id="overlapping-platform-membership-covers-hidden-short-substring"),
        pytest.param("overlapping-negative", False, id="negative-overlapping-membership-excludes-shared-prefix"),
        pytest.param("overlapping-negative-outside", True, id="negative-overlapping-membership-retains-outside-value"),
        pytest.param("overlapping-case-sensitive", False, id="overlapping-platform-membership-preserves-quoted-case"),
        pytest.param("overlapping-resolution", True, id="overlapping-platform-resolution-membership-remains-supported"),
        pytest.param("overlapping-complement", True, id="overlapping-membership-and-complement-cover-every-substring"),
        pytest.param(
            "overlapping-dropped-complement", False, id="overlapping-membership-cannot-drop-complement-substrings"
        ),
        pytest.param(
            "overlapping-dropped-substrings", False, id="overlapping-token-split-cannot-drop-hidden-substrings"
        ),
        pytest.param("duplicate-token", False, id="platform-membership-still-rejects-duplicate-tokens"),
        pytest.param("empty-token", False, id="platform-membership-still-rejects-empty-tokens"),
        pytest.param("unbounded-tokens", False, id="platform-membership-still-rejects-too-many-tokens"),
        pytest.param("case-sensitive", False, id="platform-membership-keeps-quoted-case"),
        pytest.param("negative-substring", False, id="negative-membership-rejects-an-actual-substring"),
        pytest.param("negative-outside", True, id="negative-membership-keeps-values-outside-the-string"),
        pytest.param("mixed-complement", True, id="membership-and-negative-complement-intersect-exactly"),
        pytest.param("mixed-complement-rejected", False, id="negative-membership-removes-an-actual-substring"),
        pytest.param("complement-partition", True, id="membership-and-complement-fully-partition-original-domain"),
        pytest.param("dropped-complement", False, id="missing-membership-complement-cannot-drop-original-contexts"),
        pytest.param("dropped-substrings", False, id="equality-split-cannot-drop-original-membership-substrings"),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_platform_membership_markers_preserve_pep508_substring_domains(
    tmp_path: Path, variant: str, accepted: bool, protected: bool
) -> None:
    expression = "platform_machine in 'arm64, x86_64'"
    original = "danger>=1; " + expression
    updated = ["danger>=2; " + expression]
    old_domains = ["platform_machine == 'arm'"]
    new_domains = list(old_domains)

    if variant == "complete-token":
        old_domains = new_domains = ["platform_machine == 'arm64'"]
    elif variant in {
        "overlapping-prefix",
        "overlapping-long",
        "overlapping-short",
        "overlapping-negative",
        "overlapping-negative-outside",
        "overlapping-case-sensitive",
    }:
        negative = variant in {"overlapping-negative", "overlapping-negative-outside"}
        expression = "platform_machine " + ("not in" if negative else "in") + " 'arm, arm64'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; " + expression]
        if variant == "overlapping-long":
            old_domains = new_domains = ["platform_machine == 'arm64'"]
        elif variant == "overlapping-short":
            old_domains = new_domains = ["platform_machine == 'a'"]
        elif variant == "overlapping-negative-outside":
            old_domains = new_domains = ["platform_machine == 'aarch64'"]
        elif variant == "overlapping-case-sensitive":
            old_domains = new_domains = ["platform_machine == 'ARM'"]
    elif variant == "overlapping-resolution":
        expression = "platform_machine != 'aarch64'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; " + expression]
        old_domains = new_domains = ["platform_machine in 'arm, arm64'"]
    elif variant in {"overlapping-complement", "overlapping-dropped-complement"}:
        expression = "platform_machine in 'arm, arm64'"
        original = "danger>=1; " + expression
        included = expression + " and platform_machine in 'arm64'"
        excluded = expression + " and platform_machine not in 'arm64'"
        updated = ["danger>=2; " + excluded]
        old_domains = [expression]
        new_domains = [excluded]
        if variant == "overlapping-complement":
            updated.append("danger>=2; " + included)
            new_domains.append(included)
    elif variant == "overlapping-dropped-substrings":
        expression = "platform_machine in 'arm, arm64'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; platform_machine == 'arm'", "danger>=2; platform_machine == 'arm64'"]
        old_domains = [expression]
        new_domains = ["platform_machine == 'arm'", "platform_machine == 'arm64'"]
    elif variant in {"duplicate-token", "empty-token", "unbounded-tokens"}:
        values = "arm, arm" if variant == "duplicate-token" else "arm,,arm64"
        if variant == "unbounded-tokens":
            values = ", ".join("arm" + str(index) for index in range(17))
        expression = "platform_machine in '" + values + "'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; " + expression]
    elif variant == "case-sensitive":
        old_domains = new_domains = ["platform_machine == 'ARM'"]
    elif variant in {"negative-substring", "negative-outside"}:
        expression = "platform_machine not in 'arm64, x86_64'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; " + expression]
        if variant == "negative-outside":
            old_domains = new_domains = ["platform_machine == 'aarch64'"]
    elif variant in {"mixed-complement", "mixed-complement-rejected"}:
        expression = "platform_machine in 'arm64, x86_64' and platform_machine not in 'x86_64'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; " + expression]
        if variant == "mixed-complement-rejected":
            old_domains = new_domains = ["platform_machine == 'x86'"]
    elif variant in {"complement-partition", "dropped-complement"}:
        included = expression + " and platform_machine in 'x86_64'"
        excluded = expression + " and platform_machine not in 'x86_64'"
        updated = ["danger>=2; " + excluded]
        old_domains = [expression]
        new_domains = [excluded]
        if variant == "complement-partition":
            updated.append("danger>=2; " + included)
            new_domains.append(included)
    elif variant == "dropped-substrings":
        updated = [
            "danger>=2; platform_machine == 'arm64'",
            "danger>=2; platform_machine == 'x86_64'",
        ]
        old_domains = [expression]
        new_domains = ["platform_machine == 'arm64'", "platform_machine == 'x86_64'"]

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [original],
        head_requirements=[] if protected else updated,
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[original] if protected else None,
        head_constraints=updated if protected else None,
        base_resolution_markers={("danger", "1"): old_domains},
        head_resolution_markers={("danger", "2"): new_domains},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("requirement_marker", "release", "membership"),
    [
        pytest.param("platform_release in 'arm64'", "6", "arm64", id="string-membership-keeps-numeric-substring"),
        pytest.param(
            "platform_release not in 'arm64'", "6", "arm64", id="negative-membership-rejects-numeric-substring"
        ),
        pytest.param("platform_release in 'arm64, x86_64'", "6", "arm64", id="membership-preserves-entire-raw-string"),
        pytest.param(
            "platform_release == '6.0' and platform_release in 'arm64'",
            "6",
            "arm64",
            id="normalized-equality-keeps-raw-substring-witness",
        ),
        pytest.param(
            "platform_release == '6' and platform_release in 'v6' and platform_release not in '6'",
            "v6",
            "v6",
            id="v-prefixed-raw-alias-survives-negative-membership",
        ),
        pytest.param(
            "platform_release == '6a0' and platform_release in '6a'",
            "6a",
            "6a",
            id="missing-prerelease-serial-normalizes-without-losing-raw-spelling",
        ),
        pytest.param(
            "platform_release == '6a1' and platform_release in '6alpha1'",
            "6alpha1",
            "6alpha1",
            id="prerelease-stage-alias-normalizes-without-losing-raw-spelling",
        ),
        pytest.param(
            "platform_release == '6.post0' and platform_release in '6.post'",
            "6.post",
            "6.post",
            id="missing-postrelease-serial-normalizes-without-losing-raw-spelling",
        ),
        pytest.param(
            "platform_release == '6.post1' and platform_release in '6-1'",
            "6-1",
            "6-1",
            id="implicit-postrelease-normalizes-without-losing-raw-spelling",
        ),
        pytest.param(
            "platform_release == '6.dev0' and platform_release in '6.dev'",
            "6.dev",
            "6.dev",
            id="missing-development-serial-normalizes-without-losing-raw-spelling",
        ),
        pytest.param(
            "platform_release != '6.0' and platform_release in 'arm64'",
            "6",
            "arm64",
            id="normalized-inequality-removes-raw-substring-witness",
        ),
        pytest.param(
            "platform_release != 'linux' and platform_release in 'arm64'",
            "6",
            "arm64",
            id="string-exclusion-does-not-reject-numeric-membership-domain",
        ),
        pytest.param(
            "platform_release < '7' and platform_release in 'arm64'",
            "6",
            "arm64",
            id="exclusive-upper-bound-keeps-numeric-substring",
        ),
        pytest.param(
            "platform_release <= '6' and platform_release in 'arm64'",
            "6",
            "arm64",
            id="inclusive-upper-bound-keeps-numeric-substring",
        ),
        pytest.param(
            "platform_release > '5' and platform_release in 'arm64'",
            "6",
            "arm64",
            id="exclusive-lower-bound-keeps-numeric-substring",
        ),
        pytest.param(
            "platform_release >= '6' and platform_release in 'arm64'",
            "6",
            "arm64",
            id="inclusive-lower-bound-keeps-numeric-substring",
        ),
        pytest.param(
            "platform_release > '6' and platform_release in 'arm64'",
            "6",
            "arm64",
            id="exclusive-lower-bound-rejects-equal-substring",
        ),
        pytest.param(
            "platform_release >= '5' and platform_release not in 'arm64'",
            "6",
            "arm64",
            id="negative-membership-still-limits-numeric-witness",
        ),
        pytest.param(
            "platform_release == '6.*' and platform_release in 'arm64'",
            "6",
            "arm64",
            id="wildcard-equality-keeps-numeric-substring",
        ),
        pytest.param(
            "platform_release >= '6.8.0.1a1' and platform_release in 'kernel-6.8.0.1a2'",
            "6.8.0.1a2",
            "kernel-6.8.0.1a2",
            id="prerelease-membership-preserves-numeric-ordering",
        ),
        pytest.param(
            "platform_release > '6.8.0.1a1' and platform_release in 'kernel-6.8.0.1a1.post1'",
            "6.8.0.1a1.post1",
            "kernel-6.8.0.1a1.post1",
            id="strict-prerelease-floor-excludes-its-post-release",
        ),
        pytest.param(
            "platform_release > '6.8.0.1.post1' and platform_release in 'kernel-6.8.0.1.post2'",
            "6.8.0.1.post2",
            "kernel-6.8.0.1.post2",
            id="post-release-membership-preserves-numeric-ordering",
        ),
        pytest.param(
            "platform_release >= '6.8.0.1.dev1' and platform_release in 'kernel-6.8.0.1.dev2'",
            "6.8.0.1.dev2",
            "kernel-6.8.0.1.dev2",
            id="development-membership-preserves-numeric-ordering",
        ),
        pytest.param(
            "platform_release ~= '6.8.0.1' and platform_release in 'kernel-6.8.0.2'",
            "6.8.0.2",
            "kernel-6.8.0.2",
            id="wide-compatible-range-preserves-raw-membership",
        ),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_platform_release_membership_matches_packaging_version_domains(
    tmp_path: Path, requirement_marker: str, release: str, membership: str, protected: bool
) -> None:
    expected = Marker(requirement_marker).evaluate(environment={"platform_release": release})
    resolution_marker = f"platform_release == '{Version(release)}' and platform_release in '{membership}'"
    if release == "v6":
        resolution_marker += " and platform_release not in '6'"
    previous = "danger>=1; " + requirement_marker
    updated = "danger>=2; " + requirement_marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [updated],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=[updated] if protected else None,
        base_resolution_markers={("danger", "1"): [resolution_marker]},
        head_resolution_markers={("danger", "2"): [resolution_marker]},
    )
    assert result.returncode == (0 if expected else 1), result.stdout + result.stderr


@pytest.mark.parametrize("missing", [None, "included", "excluded"], ids=["complete", "missing-in", "missing-not-in"])
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_platform_release_membership_complements_preserve_every_numeric_alias(
    tmp_path: Path, missing: str | None, protected: bool
) -> None:
    domain = "platform_release == '6'"
    partitions = {
        "included": domain + " and platform_release in 'arm64'",
        "excluded": domain + " and platform_release not in 'arm64'",
    }
    current = [marker for name, marker in partitions.items() if name != missing]
    previous = "danger>=1; " + domain
    updated = ["danger>=2; " + marker for marker in current]
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else updated,
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=updated if protected else None,
        base_resolution_markers={("danger", "1"): [domain]},
        head_resolution_markers={("danger", "2"): current},
    )
    assert result.returncode == (0 if missing is None else 1), result.stdout + result.stderr


@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_platform_release_negative_membership_retains_equivalent_numeric_aliases(
    tmp_path: Path, protected: bool
) -> None:
    marker = "platform_release == '6' and platform_release not in '6, 6.0, 06, 6.00'"
    assert Marker(marker).evaluate(environment={"platform_release": "6.0.0"})
    previous, updated = "danger>=1; " + marker, "danger>=2; " + marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [updated],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=[updated] if protected else None,
        base_resolution_markers={("danger", "1"): [marker]},
        head_resolution_markers={("danger", "2"): [marker]},
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("requirement_marker", "release"),
    [
        pytest.param("platform_release not in '6'", "6", id="standalone-negative-excludes-exact-release"),
        pytest.param("platform_release not in '7'", "6", id="standalone-negative-preserves-other-release"),
        pytest.param("platform_release not in 'kernel-6'", "6", id="negative-preserves-raw-substring-semantics"),
        pytest.param("platform_release not in 'linux'", "6", id="negative-preserves-nonnumeric-operand"),
        pytest.param("platform_release not in '6'", "6.0", id="negative-preserves-dotted-raw-alias"),
        pytest.param("platform_release not in '6.0'", "6.0", id="negative-excludes-dotted-raw-release"),
        pytest.param("platform_release not in '06'", "6", id="negative-excludes-leading-zero-containing-string"),
        pytest.param("platform_release not in '6'", "06", id="negative-preserves-leading-zero-raw-alias"),
        pytest.param(
            "platform_release not in '7' and platform_release not in 'kernel-6'",
            "6",
            id="every-negative-clause-is-preserved",
        ),
        pytest.param(
            "platform_release not in '7' and platform_release not in 'linux'",
            "6",
            id="multiple-negative-clauses-can-share-a-witness",
        ),
        pytest.param(
            "platform_release >= '5' and platform_release not in '6'",
            "6",
            id="numeric-lower-bound-cannot-drop-negative-membership",
        ),
        pytest.param(
            "platform_release == '6' and platform_release not in '6'",
            "6",
            id="numeric-equality-cannot-manufacture-an-alias-to-evade-negative-membership",
        ),
        pytest.param(
            "platform_release == '6' and platform_release not in '6'",
            "6.0",
            id="numeric-equality-retains-a-real-dotted-raw-alias",
        ),
        pytest.param(
            "platform_release == '6' and platform_release in '6'",
            "6.0",
            id="numeric-equality-cannot-manufacture-a-positive-membership-alias",
        ),
        pytest.param(
            "platform_release == '6' or platform_release in 'arm64'",
            "6.0",
            id="numeric-equality-disjunction-preserves-its-dotted-alias-alternative",
        ),
        pytest.param(
            "platform_release < '7' and platform_release not in '5'",
            "6",
            id="numeric-upper-bound-retains-valid-negative-membership",
        ),
        pytest.param(
            "platform_release != 'linux' and platform_release not in '6'",
            "6",
            id="mixed-raw-and-numeric-domains-retain-negative-membership",
        ),
        pytest.param(
            "platform_release in 'kernel-6' and platform_release not in '6'",
            "6",
            id="positive-and-negative-memberships-share-the-same-witness",
        ),
        pytest.param(
            "platform_release not in 'kernel-6.8.0.1'",
            "6.8.0.1",
            id="negative-membership-preserves-arbitrary-release-width",
        ),
        pytest.param(
            "platform_release not in 'kernel-6.8.0.1a1'",
            "6.8.0.1a1",
            id="negative-membership-preserves-prerelease-spelling",
        ),
        pytest.param(
            "platform_release not in 'kernel-6.8.0.1.post2'",
            "6.8.0.1.post2",
            id="negative-membership-preserves-postrelease-spelling",
        ),
        pytest.param(
            "platform_release not in 'kernel-6.8.0.1.dev3'",
            "6.8.0.1.dev3",
            id="negative-membership-preserves-development-spelling",
        ),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_platform_release_negative_membership_matches_packaging_without_positive_membership(
    tmp_path: Path, requirement_marker: str, release: str, protected: bool
) -> None:
    expected = Marker(requirement_marker).evaluate(environment={"platform_release": release})
    domain = f"platform_release == '{release}'"
    previous, updated = "danger>=1; " + requirement_marker, "danger>=2; " + requirement_marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [updated],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=[updated] if protected else None,
        base_resolution_markers={("danger", "1"): [domain]},
        head_resolution_markers={("danger", "2"): [domain]},
    )
    assert result.returncode == (0 if expected else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("requirement_marker", "resolution_marker", "release"),
    [
        pytest.param(
            "platform_release === '6.8.0'",
            "platform_release == '6.8.0'",
            "6.8.0",
            id="arbitrary-equality-preserves-exact-raw-platform-release",
        ),
        pytest.param(
            "platform_release === '6.8.0'",
            "platform_release == '6.8'",
            "6.8",
            id="arbitrary-equality-rejects-shorter-normalized-alias",
        ),
        pytest.param(
            "platform_release === '6.8'",
            "platform_release == '6.8.0'",
            "6.8.0",
            id="arbitrary-equality-rejects-longer-normalized-alias",
        ),
        pytest.param(
            "platform_release === '06.008.000'",
            "platform_release == '06.008.000'",
            "06.008.000",
            id="arbitrary-equality-retains-leading-zero-spelling",
        ),
        pytest.param(
            "platform_release === '6.0' and platform_release == '6'",
            "platform_release == '6.0'",
            "6.0",
            id="arbitrary-equality-can-intersect-an-equivalent-numeric-alias",
        ),
        pytest.param(
            "platform_release === '06' and platform_release == '6'",
            "platform_release == '06'",
            "06",
            id="arbitrary-equality-can-intersect-a-leading-zero-numeric-alias",
        ),
        pytest.param(
            "platform_release === '6.8.0.1.2'",
            "platform_release == '6.8.0.1.2'",
            "6.8.0.1.2",
            id="arbitrary-equality-supports-arbitrary-release-width",
        ),
        pytest.param(
            "platform_release === '6.8.0.1a1'",
            "platform_release == '6.8.0.1a1'",
            "6.8.0.1a1",
            id="arbitrary-equality-retains-prerelease-spelling",
        ),
        pytest.param(
            "platform_release === '6.8.0.1.post2'",
            "platform_release == '6.8.0.1.post2'",
            "6.8.0.1.post2",
            id="arbitrary-equality-retains-postrelease-spelling",
        ),
        pytest.param(
            "platform_release === '6.8.0.1.dev3'",
            "platform_release == '6.8.0.1.dev3'",
            "6.8.0.1.dev3",
            id="arbitrary-equality-retains-development-spelling",
        ),
        pytest.param(
            "platform_release === 'Linux'",
            "platform_release == 'linux'",
            "linux",
            id="arbitrary-equality-matches-packaging-case-insensitivity",
        ),
        pytest.param(
            "platform_release === 'v6.8'",
            "platform_release === 'v6.8'",
            "v6.8",
            id="arbitrary-equality-retains-v-prefixed-raw-domains",
        ),
        pytest.param(
            "platform_release === '6+LOCAL'",
            "platform_release === '6+local'",
            "6+local",
            id="arbitrary-equality-retains-case-insensitive-local-domains",
        ),
        pytest.param(
            "platform_release === '6' and platform_release not in '6'",
            "platform_release == '6'",
            "6",
            id="raw-equality-cannot-evade-negative-membership",
        ),
        pytest.param(
            "platform_release === '6' and platform_release in 'kernel-6'",
            "platform_release == '6'",
            "6",
            id="raw-equality-can-intersect-positive-membership",
        ),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_platform_release_arbitrary_equality_matches_packaging_raw_domains(
    tmp_path: Path, requirement_marker: str, resolution_marker: str, release: str, protected: bool
) -> None:
    expected = Marker(requirement_marker).evaluate(environment={"platform_release": release})
    assert Marker(resolution_marker).evaluate(environment={"platform_release": release})
    previous, updated = "danger>=1; " + requirement_marker, "danger>=2; " + requirement_marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [updated],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=[updated] if protected else None,
        base_resolution_markers={("danger", "1"): [resolution_marker]},
        head_resolution_markers={("danger", "2"): [resolution_marker]},
    )
    assert result.returncode == (0 if expected else 1), result.stdout + result.stderr


@pytest.mark.parametrize("scope", ["runtime", "optional", "constraint", "build", "group"])
@pytest.mark.parametrize(
    ("marker", "release"),
    [
        pytest.param("platform_release not in '6'", "6", id="inactive-negative-membership"),
        pytest.param("platform_release not in '7'", "6", id="active-negative-membership"),
        pytest.param("platform_release === '6.0'", "6", id="inactive-normalized-raw-equality-alias"),
        pytest.param("platform_release === '6'", "6", id="active-exact-raw-equality"),
    ],
)
def test_platform_release_raw_security_boundaries_are_consistent_across_dependency_groups(
    tmp_path: Path, scope: str, marker: str, release: str
) -> None:
    expected = Marker(marker).evaluate(environment={"platform_release": release})
    previous, updated = "danger>=1; " + marker, "danger>=2; " + marker
    runtime = scope in {"runtime", "optional"}
    domain = f"platform_release == '{release}'"
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[previous] if runtime else [],
        head_requirements=[updated] if runtime else [],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        optional=scope == "optional",
        base_constraints=[previous] if scope == "constraint" else None,
        head_constraints=[updated] if scope == "constraint" else None,
        base_build_constraints=[previous] if scope == "build" else None,
        head_build_constraints=[updated] if scope == "build" else None,
        base_dependency_groups={"development": [previous]} if scope == "group" else None,
        head_dependency_groups={"development": [updated]} if scope == "group" else None,
        base_resolution_markers={("danger", "1"): [domain]},
        head_resolution_markers={("danger", "2"): [domain]},
    )
    assert result.returncode == (0 if expected else 1), result.stdout + result.stderr


@pytest.mark.parametrize("scope", ["constraint", "build", "group"])
@pytest.mark.parametrize("exposure", ["transitive-upgrade", "new-extra"])
@pytest.mark.parametrize(
    ("marker", "release"),
    [
        pytest.param("platform_release not in '6'", "6", id="inactive-negative-boundary"),
        pytest.param("platform_release not in '7'", "6", id="active-negative-boundary"),
        pytest.param("platform_release not in '6'", "6.0", id="active-normalized-numeric-alias"),
        pytest.param("platform_release === '6'", "6", id="active-exact-raw-boundary"),
        pytest.param("platform_release === '6.0'", "6", id="inactive-normalized-raw-boundary"),
    ],
)
def test_new_platform_release_security_boundaries_cover_actual_exposure_domains(
    tmp_path: Path, scope: str, exposure: str, marker: str, release: str
) -> None:
    expected = Marker(marker).evaluate(environment={"platform_release": release})
    requirement = "danger>=2; " + marker
    domain = f"platform_release == '{release}'"
    extra = exposure == "new-extra"
    optional: dict[tuple[str, str], dict[str, list[dict[str, object]]]] | None = (
        {("parent", "1"): {"feature": [{"name": "danger"}]}} if extra else None
    )
    base_packages = [("patch", "1"), ("parent", "1") if extra else ("danger", "1")]
    head_packages = [("patch", "2"), *([("parent", "1")] if extra else []), ("danger", "2")]
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch>=1", *(["parent"] if extra else [])],
        head_requirements=["patch>=2", *(["parent", "parent[feature]"] if extra else [])],
        base_packages=base_packages,
        head_packages=head_packages,
        head_constraints=[requirement] if scope == "constraint" else None,
        head_build_constraints=[requirement] if scope == "build" else None,
        head_dependency_groups={"reviewed": [requirement]} if scope == "group" else None,
        base_lock_optional_dependencies=optional,
        head_lock_optional_dependencies=optional,
        base_resolution_markers=None if extra else {("danger", "1"): [domain]},
        head_resolution_markers={("danger", "2"): [domain]},
    )
    assert result.returncode == (0 if expected else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("requirement_marker", "resolution_marker", "accepted"),
    [
        pytest.param("'lin' in sys_platform", "sys_platform == 'linux'", True, id="reversed-platform-substring"),
        pytest.param(
            "'linux' in sys_platform", "sys_platform == 'lin'", False, id="reversed-membership-keeps-direction"
        ),
        pytest.param("'lin' in sys_platform", "sys_platform == 'win32'", False, id="reversed-platform-missing-needle"),
        pytest.param("'win' not in sys_platform", "sys_platform == 'linux'", True, id="reversed-negative-outside"),
        pytest.param("'lin' not in sys_platform", "sys_platform == 'linux'", False, id="reversed-negative-substring"),
        pytest.param(
            "sys_platform == 'linux'",
            "'lin' in sys_platform and sys_platform == 'linux'",
            True,
            id="reversed-resolution-substring",
        ),
        pytest.param("sys_platform == 'linux'", "'lin' not in sys_platform", False, id="reversed-resolution-negative"),
        pytest.param(
            "'lin' in sys_platform and 'ux' in sys_platform",
            "sys_platform == 'linux'",
            True,
            id="reversed-platform-keeps-every-required-needle",
        ),
        pytest.param(
            "'lin' in sys_platform and 'in' not in sys_platform",
            "sys_platform == 'linux'",
            False,
            id="required-needle-cannot-contain-a-forbidden-needle",
        ),
        pytest.param(
            "'lin' in sys_platform and sys_platform in 'linux,win32'",
            "sys_platform == 'linux'",
            True,
            id="forward-and-reversed-membership-share-one-platform-witness",
        ),
        pytest.param(
            "'inu' in sys_platform and sys_platform in 'linux,win32'",
            "sys_platform == 'win32'",
            False,
            id="forward-and-reversed-membership-reject-distinct-witnesses",
        ),
        pytest.param("'' in sys_platform", "sys_platform == 'linux'", True, id="empty-reversed-needle-is-universal"),
        pytest.param("'' not in sys_platform", "sys_platform == 'linux'", False, id="empty-reversed-negative-is-empty"),
        pytest.param("'LIN' in sys_platform", "sys_platform == 'linux'", False, id="reversed-platform-keeps-case"),
        pytest.param(
            "'3.1' in platform_version",
            "platform_version == '3.10'",
            True,
            id="reversed-platform-version-remains-string-containment",
        ),
        pytest.param(
            "'6.1' in platform_release",
            "platform_release == '6.10'",
            False,
            id="reversed-numeric-platform-release-fails-closed",
        ),
        pytest.param(
            "'3.1' in python_version",
            "python_full_version == '3.10.4'",
            False,
            id="unbounded-reversed-python-version-space-fails-closed",
        ),
        pytest.param(
            "'" + "a" * 257 + "' in sys_platform",
            "sys_platform == 'linux'",
            False,
            id="unbounded-reversed-platform-needle-fails-closed",
        ),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_reversed_platform_membership_preserves_operand_orientation(
    tmp_path: Path, requirement_marker: str, resolution_marker: str, accepted: bool, protected: bool
) -> None:
    previous = "danger>=1; " + requirement_marker
    updated = "danger>=2; " + requirement_marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [updated],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=[updated] if protected else None,
        base_resolution_markers={("danger", "1"): [resolution_marker]},
        head_resolution_markers={("danger", "2"): [resolution_marker]},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize("complete", [False, True], ids=["missing-complement", "complete-complement"])
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_reversed_platform_membership_complements_preserve_every_security_domain(
    tmp_path: Path, complete: bool, protected: bool
) -> None:
    domain = "sys_platform != 'darwin'"
    included = domain + " and 'lin' in sys_platform"
    excluded = domain + " and 'lin' not in sys_platform"
    updated = ["danger>=2; " + included]
    new_domains = [included]
    if complete:
        updated.append("danger>=2; " + excluded)
        new_domains.append(excluded)
    previous = "danger>=1; " + domain
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else updated,
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=updated if protected else None,
        base_resolution_markers={("danger", "1"): [domain]},
        head_resolution_markers={("danger", "2"): new_domains},
    )
    assert result.returncode == (0 if complete else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("requirement_marker", "resolution_marker", "accepted"),
    [
        pytest.param(
            "sys_platform >= 'linux'",
            "sys_platform == 'linux'",
            True,
            id="inclusive-lower-includes-only-the-equal-platform",
        ),
        pytest.param(
            "sys_platform > 'linux'",
            "sys_platform == 'linux'",
            False,
            id="exclusive-lower-rejects-equal-platform",
        ),
        pytest.param(
            "sys_platform > 'linux'",
            "sys_platform == 'win32'",
            False,
            id="exclusive-lower-does-not-use-lexical-platform-ordering",
        ),
        pytest.param(
            "sys_platform >= 'linux'",
            "sys_platform == 'win32'",
            False,
            id="inclusive-lower-does-not-cover-a-lexically-greater-platform",
        ),
        pytest.param(
            "sys_platform <= 'linux'",
            "sys_platform == 'linux'",
            True,
            id="inclusive-upper-includes-only-the-equal-platform",
        ),
        pytest.param(
            "sys_platform <= 'linux'",
            "sys_platform == 'darwin'",
            False,
            id="inclusive-upper-does-not-cover-a-lexically-smaller-platform",
        ),
        pytest.param(
            "sys_platform < 'linux'",
            "sys_platform == 'linux'",
            False,
            id="exclusive-upper-rejects-equal-platform",
        ),
        pytest.param(
            "sys_platform < 'ab'",
            "sys_platform == 'a'",
            False,
            id="exclusive-upper-does-not-use-lexical-platform-ordering",
        ),
        pytest.param(
            "'ab' > sys_platform",
            "sys_platform == 'a'",
            False,
            id="reversed-exclusive-comparison-does-not-use-lexical-ordering",
        ),
        pytest.param(
            "'a' <= sys_platform",
            "sys_platform == 'a'",
            True,
            id="reversed-inclusive-comparison-preserves-equal-platform",
        ),
        pytest.param(
            "'a' <= sys_platform",
            "sys_platform == 'b'",
            False,
            id="reversed-inclusive-comparison-rejects-unequal-platform",
        ),
        pytest.param(
            "sys_platform >= 'linux' and sys_platform < 'win32'",
            "sys_platform == 'linux'",
            False,
            id="exclusive-upper-makes-a-platform-window-unsatisfiable",
        ),
        pytest.param(
            "sys_platform >= 'linux' and sys_platform < 'win32'",
            "sys_platform == 'win32'",
            False,
            id="exclusive-platform-window-rejects-every-platform",
        ),
        pytest.param(
            "sys_platform >= 'linux'",
            "sys_platform >= 'linux' and sys_platform < 'win32'",
            False,
            id="exclusive-resolution-marker-has-no-installer-domain",
        ),
        pytest.param(
            "sys_platform > 'linux'",
            "sys_platform <= 'linux'",
            False,
            id="strict-platform-comparison-cannot-cover-an-inclusive-domain",
        ),
        pytest.param(
            "sys_platform >= 'linux' and sys_platform != 'linux'",
            "sys_platform == 'linux'",
            False,
            id="inclusive-platform-exclusion-cannot-be-lost",
        ),
        pytest.param(
            "sys_platform >= 'linux' and sys_platform != 'linux'",
            "sys_platform > 'linux'",
            False,
            id="inclusive-platform-exclusion-leaves-no-other-witness",
        ),
        pytest.param(
            "platform_machine > 'ar' and platform_machine in 'arm64, x86_64'",
            "platform_machine == 'arm'",
            False,
            id="strict-platform-comparison-cannot-gain-a-substring-witness",
        ),
        pytest.param(
            "platform_machine >= 'arm' and platform_machine in 'arm64, x86_64'",
            "platform_machine == 'arm'",
            True,
            id="inclusive-platform-comparison-retains-an-equal-substring-witness",
        ),
        pytest.param(
            "platform_version > '3.9'",
            "platform_version == '3.10'",
            False,
            id="platform-version-does-not-enable-version-ordering",
        ),
        pytest.param(
            "platform_version >= '3.9'",
            "platform_version == '3.10'",
            False,
            id="inclusive-platform-version-comparison-still-requires-equality",
        ),
        pytest.param(
            "platform_release < 'build-42'",
            "platform_release == 'build-4'",
            False,
            id="nonnumeric-platform-release-does-not-use-lexical-ordering",
        ),
        pytest.param(
            "platform_release >= 'build-42'",
            "platform_release == 'build-42'",
            True,
            id="nonnumeric-platform-release-inclusive-comparison-preserves-equality",
        ),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_ordered_platform_markers_preserve_installer_security_domains(
    tmp_path: Path,
    requirement_marker: str,
    resolution_marker: str,
    accepted: bool,
    protected: bool,
) -> None:
    before = "danger>=1; " + requirement_marker
    after = "danger>=2; " + requirement_marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [before],
        head_requirements=[] if protected else [after],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[before] if protected else None,
        head_constraints=[after] if protected else None,
        base_resolution_markers={("danger", "1"): [resolution_marker]},
        head_resolution_markers={("danger", "2"): [resolution_marker]},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("requirement_marker", "resolution_marker", "accepted"),
    [
        pytest.param(
            "sys_platform < 'ab'",
            "sys_platform == 'a'",
            False,
            id="strict-less-than-never-protects-a-transitive-platform",
        ),
        pytest.param(
            "sys_platform > 'a'",
            "sys_platform == 'ab'",
            False,
            id="strict-greater-than-never-protects-a-transitive-platform",
        ),
        pytest.param(
            "sys_platform >= 'a'",
            "sys_platform in 'a,b'",
            False,
            id="inclusive-lower-cannot-hide-an-unprotected-platform-fragment",
        ),
        pytest.param(
            "sys_platform <= 'a'",
            "sys_platform in 'a,b'",
            False,
            id="inclusive-upper-cannot-hide-an-unprotected-platform-fragment",
        ),
        pytest.param(
            "sys_platform >= 'a'",
            "sys_platform == 'a'",
            True,
            id="inclusive-lower-protects-its-equal-platform",
        ),
        pytest.param(
            "sys_platform <= 'a'",
            "sys_platform == 'a'",
            True,
            id="inclusive-upper-protects-its-equal-platform",
        ),
    ],
)
def test_ordered_platform_markers_cannot_fake_transitive_security_coverage(
    tmp_path: Path, requirement_marker: str, resolution_marker: str, accepted: bool
) -> None:
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1"],
        head_requirements=["patch-me>=1.1"],
        base_packages=[("patch-me", "1"), ("danger", "1")],
        head_packages=[("patch-me", "1.1"), ("danger", "2")],
        base_constraints=["danger>=1; " + (requirement_marker if accepted else resolution_marker)],
        head_constraints=["danger>=2; " + requirement_marker],
        base_resolution_markers={("danger", "1"): [resolution_marker]},
        head_resolution_markers={("danger", "2"): [resolution_marker]},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("patched-range", True, id="wildcard-equality-normalizes-to-inclusive-series-range"),
        pytest.param("subsumed-exclusion", True, id="patched-floor-subsumes-the-original-wildcard-exclusion"),
        pytest.param("preserved-exclusion", True, id="wildcard-equality-retains-an-independent-prefix-exclusion"),
        pytest.param("removed-exclusion", False, id="wildcard-equality-cannot-drop-an-uncovered-exclusion"),
        pytest.param("widened-series", False, id="wildcard-equality-cannot-widen-its-original-major-series"),
        pytest.param("removed-upper", False, id="wildcard-equality-cannot-drop-its-implicit-upper-bound"),
        pytest.param("nested-prefix", True, id="minor-wildcard-equality-keeps-the-correct-next-prefix-ceiling"),
        pytest.param("minor-zero-prefix", True, id="one-zero-wildcard-equality-has-one-one-exclusive-ceiling"),
        pytest.param("patch-zero-prefix", True, id="one-zero-zero-wildcard-equality-has-one-zero-one-ceiling"),
        pytest.param("canonical-zeroes", True, id="wildcard-equality-normalizes-release-prefix-zeroes"),
        pytest.param("epoch-zeroes", True, id="wildcard-equality-normalizes-epoch-and-release-zeroes"),
        pytest.param("epoch", True, id="wildcard-equality-preserves-its-explicit-epoch"),
        pytest.param("wrong-epoch", False, id="wildcard-equality-cannot-move-its-epoch"),
        pytest.param("malformed-post", False, id="post-release-wildcard-equality-remains-invalid"),
        pytest.param("retained-release", False, id="wildcard-equality-cannot-drop-an-unchanged-supported-lock"),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_wildcard_equality_series_preserve_reviewed_security_bounds(
    tmp_path: Path, variant: str, accepted: bool, protected: bool
) -> None:
    previous, current = "danger==1.*", "danger>=1.3,<2"
    before, after = ["1.2"], ["1.3"]

    if variant in {"preserved-exclusion", "removed-exclusion"}:
        previous = "danger==1.*,!=1.8.*"
        current = "danger>=1.3,<2" + (",!=1.8.*" if variant == "preserved-exclusion" else "")
    elif variant == "subsumed-exclusion":
        previous = "danger==1.*,!=1.2.*"
        before = ["1.1"]
    elif variant == "widened-series":
        current = "danger>=1.3,<3"
    elif variant == "removed-upper":
        current = "danger>=1.3"
    elif variant == "nested-prefix":
        previous, current = "danger==1.2.*", "danger>=1.2.4,<1.3"
        before, after = ["1.2.3"], ["1.2.4"]
    elif variant == "minor-zero-prefix":
        previous, current = "danger==1.0.*", "danger>=1.0.3,<1.1"
        before, after = ["1.0.2"], ["1.0.3"]
    elif variant == "patch-zero-prefix":
        previous, current = "danger==1.0.0.*", "danger>=1.0.0.4,<1.0.1"
        before, after = ["1.0.0.3"], ["1.0.0.4"]
    elif variant == "canonical-zeroes":
        previous, current = "danger==01.00.*", "danger>=1.0.3,<1.1"
        before, after = ["1.0.2"], ["1.0.3"]
    elif variant == "epoch-zeroes":
        previous, current = "danger==01!01.00.*", "danger>=1!1.0.3,<1!1.1"
        before, after = ["1!1.0.2"], ["1!1.0.3"]
    elif variant in {"epoch", "wrong-epoch"}:
        previous = "danger==1!1.*"
        current = "danger>=1!1.3,<1!2" if variant == "epoch" else "danger>=0!1.3,<0!2"
        before = ["1!1.2"]
        after = ["1!1.3"] if variant == "epoch" else ["1.3"]
    elif variant == "malformed-post":
        previous = "danger==1.post1.*"
        before, after = ["1.post1"], ["1.3"]
    elif variant == "retained-release":
        current = "danger>=1.3,<1.5"
        before, after = ["1.2", "1.8"], ["1.3", "1.8"]

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [current],
        base_packages=[("danger", version) for version in before],
        head_packages=[("danger", version) for version in after],
        base_constraints=[previous] if protected else None,
        head_constraints=[current] if protected else None,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("full-substring", True, id="full-python-membership-covers-partial-final-digits"),
        pytest.param("full-token", True, id="full-python-membership-keeps-complete-token"),
        pytest.param("full-outside", False, id="full-python-membership-rejects-values-outside-literal"),
        pytest.param("full-negative-substring", False, id="full-python-negative-membership-rejects-real-substring"),
        pytest.param("full-negative-outside", True, id="full-python-negative-membership-keeps-outside-release"),
        pytest.param("minor-substring", True, id="python-minor-membership-covers-partial-minor-digits"),
        pytest.param(
            "minor-containing-full-version", True, id="python-minor-membership-allows-containing-full-version"
        ),
        pytest.param(
            "minor-containing-full-versions", True, id="python-minor-membership-allows-containing-full-version-list"
        ),
        pytest.param("minor-overlapping-prefix", True, id="python-minor-membership-allows-overlapping-prefix"),
        pytest.param("minor-overlapping-short", True, id="python-minor-membership-preserves-short-overlapping-prefix"),
        pytest.param(
            "minor-overlapping-negative", False, id="negative-python-minor-membership-excludes-overlapping-prefix"
        ),
        pytest.param(
            "minor-overlapping-negative-outside", True, id="negative-python-minor-membership-keeps-outside-release"
        ),
        pytest.param("full-overlapping-prefix", True, id="full-python-membership-allows-overlapping-prefix"),
        pytest.param("full-overlapping-short", True, id="full-python-membership-preserves-short-overlapping-prefix"),
        pytest.param(
            "full-overlapping-prerelease", True, id="full-python-membership-allows-overlapping-prerelease-serials"
        ),
        pytest.param("minor-negative-substring", False, id="python-minor-negative-membership-excludes-partial-minor"),
        pytest.param("minor-dropped-substrings", False, id="python-minor-equalities-cannot-drop-hidden-three-one"),
        pytest.param(
            "minor-overlapping-dropped-substrings", False, id="overlapping-python-membership-cannot-drop-short-prefix"
        ),
        pytest.param("resolution-projection", True, id="full-python-membership-resolution-projects-into-minor"),
        pytest.param("complete-partition", True, id="python-membership-and-complement-cover-entire-domain"),
        pytest.param("missing-partition", False, id="missing-python-membership-complement-cannot-drop-domain"),
        pytest.param("dropped-substrings", False, id="python-token-equalities-cannot-drop-original-substrings"),
        pytest.param("unbounded-substrings", False, id="unbounded-python-membership-substrings-fail-closed"),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_python_membership_markers_preserve_exact_pep508_substrings(
    tmp_path: Path, variant: str, accepted: bool, protected: bool
) -> None:
    expression = "python_full_version in '3.10.10, 3.10.11'"
    original = "danger>=1; " + expression
    updated = ["danger>=2; " + expression]
    old_domains = ["python_full_version == '3.10.1'"]
    new_domains = list(old_domains)

    if variant == "full-token":
        old_domains = new_domains = ["python_full_version == '3.10.10'"]
    elif variant == "full-outside":
        old_domains = new_domains = ["python_full_version == '3.10.12'"]
    elif variant in {"full-negative-substring", "full-negative-outside"}:
        expression = "python_full_version not in '3.10.10, 3.10.11'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; " + expression]
        if variant == "full-negative-outside":
            old_domains = new_domains = ["python_full_version == '3.10.12'"]
    elif variant in {"minor-substring", "minor-negative-substring"}:
        operator = "not in" if variant == "minor-negative-substring" else "in"
        expression = "python_version " + operator + " '3.10, 3.11'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; " + expression]
        old_domains = new_domains = ["python_full_version == '3.1.7'"]
    elif variant in {"minor-containing-full-version", "minor-containing-full-versions"}:
        versions = "3.10.1" if variant == "minor-containing-full-version" else "3.10.1, 3.11.2"
        release = "3.10.7" if variant == "minor-containing-full-version" else "3.11.7"
        expression = "python_version in '" + versions + "'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; " + expression]
        old_domains = new_domains = ["python_full_version == '" + release + "'"]
    elif variant in {
        "minor-overlapping-prefix",
        "minor-overlapping-short",
        "minor-overlapping-negative",
        "minor-overlapping-negative-outside",
    }:
        negative = variant in {"minor-overlapping-negative", "minor-overlapping-negative-outside"}
        operator = "not in" if negative else "in"
        expression = "python_version " + operator + " '3.1, 3.10'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; " + expression]
        if variant == "minor-overlapping-short":
            release = "3.1.7"
        elif variant == "minor-overlapping-negative-outside":
            release = "3.11.7"
        else:
            release = "3.10.7"
        old_domains = new_domains = ["python_full_version == '" + release + "'"]
    elif variant in {"full-overlapping-prefix", "full-overlapping-short", "full-overlapping-prerelease"}:
        versions = "3.15.0a1, 3.15.0a10" if variant == "full-overlapping-prerelease" else "3.10.1, 3.10.10"
        if variant == "full-overlapping-short":
            release = "3.10.1"
        elif variant == "full-overlapping-prerelease":
            release = "3.15.0a10"
        else:
            release = "3.10.10"
        expression = "python_full_version in '" + versions + "'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; " + expression]
        old_domains = new_domains = ["python_full_version == '" + release + "'"]
    elif variant == "minor-dropped-substrings":
        expression = "python_version in '3.10, 3.11'"
        original = "danger>=1; " + expression
        updated = [
            "danger>=2; python_version == '3.10'",
            "danger>=2; python_version == '3.11'",
        ]
        old_domains = [expression]
        new_domains = ["python_version == '3.10'", "python_version == '3.11'"]
    elif variant == "minor-overlapping-dropped-substrings":
        expression = "python_version in '3.1, 3.10'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; python_version == '3.10'"]
        old_domains = [expression]
        new_domains = ["python_version == '3.10'"]
    elif variant == "resolution-projection":
        expression = "python_version == '3.10'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; " + expression]
        old_domains = new_domains = ["python_full_version in '3.10.10, 3.10.11'"]
    elif variant in {"complete-partition", "missing-partition"}:
        included = expression + " and python_full_version in '3.10.11'"
        excluded = expression + " and python_full_version not in '3.10.11'"
        updated = ["danger>=2; " + excluded]
        old_domains = new_domains = [
            "python_full_version == '3.10.1'",
            "python_full_version == '3.10.10'",
            "python_full_version == '3.10.11'",
        ]
        if variant == "complete-partition":
            updated.append("danger>=2; " + included)
    elif variant == "dropped-substrings":
        updated = [
            "danger>=2; python_full_version == '3.10.10'",
            "danger>=2; python_full_version == '3.10.11'",
        ]
        old_domains = [expression]
        new_domains = ["python_full_version == '3.10.10'", "python_full_version == '3.10.11'"]
    elif variant == "unbounded-substrings":
        members = ", ".join("3.10." + str(1000 + index) for index in range(16))
        expression = "python_full_version in '" + members + "'"
        original = "danger>=1; " + expression
        updated = ["danger>=2; " + expression]
        old_domains = new_domains = ["python_full_version == '3.10.1000'"]

    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [original],
        head_requirements=[] if protected else updated,
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[original] if protected else None,
        head_constraints=updated if protected else None,
        base_resolution_markers={("danger", "1"): old_domains},
        head_resolution_markers={("danger", "2"): new_domains},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("requirement_marker", "resolution_marker", "accepted"),
    [
        pytest.param("'3.10' == python_version", "python_full_version == '3.10.4'", True, id="reversed-equality"),
        pytest.param("'3.10' != python_version", "python_full_version == '3.11.4'", True, id="reversed-inequality"),
        pytest.param("'3.10' != python_version", "python_full_version == '3.10.4'", False, id="reversed-excluded"),
        pytest.param("'3.10' < python_version", "python_full_version == '3.11.0'", True, id="reversed-exclusive-lower"),
        pytest.param("'3.10' < python_version", "python_full_version == '3.10.4'", False, id="reversed-lower-equal"),
        pytest.param(
            "'3.10' <= python_version", "python_full_version == '3.10.4'", True, id="reversed-inclusive-lower"
        ),
        pytest.param("'3.10' <= python_version", "python_full_version == '3.9.4'", False, id="reversed-lower-outside"),
        pytest.param("'3.10' > python_version", "python_full_version == '3.9.4'", True, id="reversed-exclusive-upper"),
        pytest.param("'3.10' > python_version", "python_full_version == '3.10.4'", False, id="reversed-upper-equal"),
        pytest.param(
            "'3.10' >= python_version", "python_full_version == '3.10.4'", True, id="reversed-inclusive-upper"
        ),
        pytest.param("'3.10' >= python_version", "python_full_version == '3.11.4'", False, id="reversed-upper-outside"),
        pytest.param("'3.1' == python_version", "python_full_version == '3.1.7'", True, id="reversed-minor-projection"),
        pytest.param("'3.10.1' <= python_full_version", "python_full_version == '3.10.1'", True, id="reversed-full"),
        pytest.param("'linux' <= sys_platform", "sys_platform == 'win32'", False, id="reversed-platform-unequal"),
        pytest.param("'linux' <= sys_platform", "sys_platform == 'darwin'", False, id="reversed-platform-outside"),
        pytest.param(
            "python_version >= '3.10'",
            "'3.10.4' <= python_full_version",
            True,
            id="reversed-resolution-comparison",
        ),
        pytest.param(
            "sys_platform >= 'linux'",
            "'linux' <= sys_platform",
            True,
            id="reversed-platform-resolution",
        ),
        pytest.param("'3.10' in python_version", "python_full_version == '3.10.4'", False, id="reversed-in-rejected"),
        pytest.param(
            "'3.10' not in python_version",
            "python_full_version == '3.11.4'",
            False,
            id="reversed-not-in-rejected",
        ),
        pytest.param(
            "'3.10' <= python_version <= '3.11'",
            "python_full_version == '3.10.4'",
            False,
            id="reversed-chained-comparison-rejected",
        ),
        pytest.param(
            "3.10 <= python_version", "python_full_version == '3.10.4'", False, id="nonstring-literal-rejected"
        ),
        pytest.param(
            "python_full_version <= python_version",
            "python_full_version == '3.10.4'",
            False,
            id="two-marker-variables-rejected",
        ),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_reversed_literal_marker_comparisons_preserve_semantic_security_domains(
    tmp_path: Path, requirement_marker: str, resolution_marker: str, accepted: bool, protected: bool
) -> None:
    previous = "danger>=1; " + requirement_marker
    updated = "danger>=2; " + requirement_marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [updated],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=[updated] if protected else None,
        base_resolution_markers={("danger", "1"): [resolution_marker]},
        head_resolution_markers={("danger", "2"): [resolution_marker]},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("requested", "marker", "reviewed", "accepted"),
    [
        pytest.param("foo", "extra in 'foobar'", False, False, id="substring-extra-cannot-hide-unreviewed-package"),
        pytest.param("foo", "extra in 'foobar'", True, True, id="substring-extra-can-use-reviewed-package"),
        pytest.param(
            "foo", "extra not in 'foobar'", False, True, id="negative-substring-extra-does-not-expose-package"
        ),
        pytest.param(
            "foo-bar", "extra in 'FOO_BAR-baz'", False, False, id="extra-substring-normalizes-both-pep508-operands"
        ),
        pytest.param(
            "foo-bar", "'FOO_BAR' in extra", False, False, id="reversed-extra-containment-normalizes-the-needle"
        ),
        pytest.param("foo-bar", "'foo' in extra", False, False, id="reversed-extra-containment-keeps-direction"),
        pytest.param("foo", "'foobar' in extra", False, True, id="reversed-extra-longer-needle-cannot-match"),
        pytest.param("foo", "'foo' not in extra", False, True, id="reversed-extra-negative-excludes-a-real-needle"),
        pytest.param("bar", "'foo' not in extra", False, False, id="reversed-extra-negative-keeps-an-outside-needle"),
    ],
)
def test_locked_extra_membership_uses_pep508_substring_containment(
    tmp_path: Path, requested: str, marker: str, reviewed: bool, accepted: bool
) -> None:
    optional: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {
        ("parent", "1"): {requested: [{"name": "plugin", "marker": marker}]}
    }
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1", "parent"],
        head_requirements=["patch-me>=1.1", "parent", "parent[" + requested + "]"],
        base_packages=[("patch-me", "1"), ("parent", "1")],
        head_packages=[("patch-me", "1.1"), ("parent", "1"), ("plugin", "1")],
        head_constraints=["plugin>=1"] if reviewed else None,
        base_lock_optional_dependencies=optional,
        head_lock_optional_dependencies=optional,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("requested", "marker"),
    [
        pytest.param("new-extra", "extra >= 'new-extra'", id="inclusive-lower-order-matches-selected-extra"),
        pytest.param("new-extra", "extra <= 'new-extra'", id="inclusive-upper-order-matches-selected-extra"),
        pytest.param("new-extra", "extra > 'new-extra'", id="strict-lower-order-does-not-match-selected-extra"),
        pytest.param("new-extra", "extra < 'new-extra'", id="strict-upper-order-does-not-match-selected-extra"),
        pytest.param("new-extra", "extra >= 'other-extra'", id="inclusive-lower-order-rejects-different-extra"),
        pytest.param("new-extra", "extra <= 'other-extra'", id="inclusive-upper-order-rejects-different-extra"),
        pytest.param("new-extra", "extra > 'aaa'", id="strict-lower-order-does-not-fall-back-to-lexical-order"),
        pytest.param("new-extra", "extra < 'zzz'", id="strict-upper-order-does-not-fall-back-to-lexical-order"),
        pytest.param("new-extra", "extra >= 'NEW_EXTRA'", id="inclusive-order-normalizes-pep508-extra-alias"),
        pytest.param("new-extra", "'NEW_EXTRA' <= extra", id="reversed-inclusive-order-normalizes-extra-alias"),
        pytest.param("new-extra", "'new-extra' >= extra", id="reversed-inclusive-upper-order-matches-equality"),
        pytest.param("new-extra", "'new-extra' < extra", id="reversed-strict-order-remains-unsatisfied"),
        pytest.param(
            "new-extra",
            "extra >= 'new-extra' and extra <= 'NEW_EXTRA'",
            id="inclusive-extra-conjunction-shares-one-normalized-witness",
        ),
        pytest.param(
            "new-extra",
            "extra >= 'new-extra' and extra < 'new-extra'",
            id="strict-and-inclusive-extra-conjunction-remains-unsatisfied",
        ),
        pytest.param(
            "new-extra",
            "extra > 'new-extra' or extra <= 'NEW_EXTRA'",
            id="inclusive-extra-disjunction-retains-its-active-alternative",
        ),
    ],
)
@pytest.mark.parametrize("reviewed", [False, True], ids=["unreviewed-package", "reviewed-package"])
def test_selected_extra_ordered_markers_match_packaging_without_hiding_dependencies(
    tmp_path: Path, requested: str, marker: str, reviewed: bool
) -> None:
    active = Marker(marker).evaluate(environment={"extra": requested})
    optional: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {
        ("parent", "1"): {requested: [{"name": "plugin", "marker": marker}]}
    }
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1", "parent"],
        head_requirements=["patch-me>=1.1", "parent", "parent[" + requested + "]"],
        base_packages=[("patch-me", "1"), ("parent", "1")],
        head_packages=[("patch-me", "1.1"), ("parent", "1"), ("plugin", "1")],
        head_constraints=["plugin>=1"] if reviewed else None,
        base_lock_optional_dependencies=optional,
        head_lock_optional_dependencies=optional,
    )
    assert result.returncode == (0 if not active or reviewed else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("marker", "reviewed", "accepted"),
    [
        pytest.param(
            "extra != 'foo' and extra != 'bar'",
            None,
            True,
            id="different-selected-extras-cannot-witness-separate-negative-clauses",
        ),
        pytest.param(
            "extra == 'foo' and extra == 'bar'",
            None,
            True,
            id="different-selected-extras-cannot-witness-separate-equality-clauses",
        ),
        pytest.param(
            "extra == 'foo' and extra != 'bar'",
            None,
            False,
            id="one-selected-extra-satisfying-both-clauses-exposes-the-package",
        ),
        pytest.param(
            "extra == 'foo' and extra != 'bar'",
            ["plugin>=1"],
            True,
            id="one-selected-extra-satisfying-both-clauses-can-use-a-reviewed-package",
        ),
        pytest.param(
            "extra in 'foobar' and extra not in 'foobar'",
            None,
            True,
            id="membership-and-its-complement-cannot-use-different-selected-extras",
        ),
        pytest.param(
            "extra in 'foo' and extra not in 'bar'",
            None,
            False,
            id="membership-conjunction-retains-a-single-valid-selected-extra",
        ),
        pytest.param(
            "(extra == 'foo' and sys_platform == 'linux') or (extra == 'bar' and sys_platform == 'win32')",
            ["plugin>=1; sys_platform == 'linux'"],
            False,
            id="distinct-selected-extras-retain-both-platform-security-domains",
        ),
        pytest.param(
            "(extra == 'foo' and sys_platform == 'linux') or (extra == 'bar' and sys_platform == 'win32')",
            ["plugin>=1; sys_platform == 'linux'", "plugin>=1; sys_platform == 'win32'"],
            True,
            id="distinct-selected-extras-can-each-use-their-reviewed-platform-domain",
        ),
        pytest.param(
            "(extra != 'foo' and extra != 'bar') or (extra == 'foo' and sys_platform == 'linux')",
            ["plugin>=1; sys_platform == 'linux'"],
            True,
            id="nested-boolean-marker-discards-cross-extra-witnesses-and-keeps-platform-context",
        ),
    ],
)
def test_locked_extra_conjunctions_share_one_selected_extra_witness(
    tmp_path: Path, marker: str, reviewed: list[str] | None, accepted: bool
) -> None:
    optional: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {
        ("parent", "1"): {"foo": [{"name": "plugin", "marker": marker}], "bar": []}
    }
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1", "parent"],
        head_requirements=["patch-me>=1.1", "parent", "parent[foo,bar]"],
        base_packages=[("patch-me", "1"), ("parent", "1")],
        head_packages=[("patch-me", "1.1"), ("parent", "1"), ("plugin", "1")],
        head_constraints=reviewed,
        base_lock_optional_dependencies=optional,
        head_lock_optional_dependencies=optional,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("marker", "reviewed", "accepted"),
    [
        pytest.param("extra == ''", False, False, id="missing-extra-uses-its-empty-selected-value"),
        pytest.param("extra == ''", True, True, id="matching-empty-extra-can-use-a-reviewed-package"),
        pytest.param("extra != ''", False, True, id="missing-extra-rejects-a-nonempty-only-edge"),
        pytest.param("extra in ''", False, False, id="empty-selected-extra-preserves-substring-containment"),
        pytest.param("extra in 'foobar'", False, False, id="empty-selected-extra-is-a-substring-of-other-values"),
        pytest.param("extra not in ''", False, True, id="empty-selected-extra-preserves-negative-containment"),
    ],
)
def test_locked_extra_marker_defaults_to_one_empty_selected_extra(
    tmp_path: Path, marker: str, reviewed: bool, accepted: bool
) -> None:
    optional: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {
        ("parent", "1"): {"feature": [{"name": "nested"}]}
    }
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1", "parent"],
        head_requirements=["patch-me>=1.1", "parent", "parent[feature]"],
        base_packages=[("patch-me", "1"), ("parent", "1"), ("nested", "1")],
        head_packages=[("patch-me", "1.1"), ("parent", "1"), ("nested", "1"), *([("plugin", "1")] if reviewed else [])],
        head_constraints=["nested>=1", *(["plugin>=1"] if reviewed else [])],
        head_lock_dependencies={("nested", "1"): [{"name": "plugin", "marker": marker}]},
        base_lock_optional_dependencies=optional,
        head_lock_optional_dependencies=optional,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("requirement_marker", "resolution_marker", "accepted"),
    [
        pytest.param(
            "implementation_version >= '3.10'",
            "implementation_version == '3.11.0'",
            True,
            id="implementation-version-uses-pep440-ordering",
        ),
        pytest.param(
            "implementation_version >= '3.10'",
            "implementation_version == '3.9.9'",
            False,
            id="implementation-version-rejects-lower-numeric-release",
        ),
        pytest.param(
            "implementation_version < '3.10'",
            "implementation_version == '3.9.9'",
            True,
            id="implementation-version-does-not-use-lexical-ordering",
        ),
        pytest.param(
            "platform_release == '6.8.0'",
            "platform_release == '6.8.0'",
            True,
            id="platform-release-marker-is-supported",
        ),
        pytest.param(
            "platform_release >= '6.10'",
            "platform_release == '6.11.0'",
            True,
            id="platform-release-uses-pep440-ordering",
        ),
        pytest.param(
            "platform_release < '6.10'",
            "platform_release == '6.9.0'",
            True,
            id="platform-release-does-not-use-lexical-ordering",
        ),
        pytest.param(
            "platform_release >= '6.10'",
            "platform_release == '6.9.0'",
            False,
            id="platform-release-rejects-lower-numeric-release",
        ),
        pytest.param(
            "platform_release >= '6.8.0.1'",
            "platform_release == '6.8.0.2'",
            True,
            id="platform-release-preserves-four-component-numeric-ordering",
        ),
        pytest.param(
            "platform_release >= '6.8.0.2'",
            "platform_release == '6.8.0.1'",
            False,
            id="platform-release-rejects-lower-four-component-release",
        ),
        pytest.param(
            "platform_release < '6.8.0.10'",
            "platform_release == '6.8.0.2'",
            True,
            id="platform-release-orders-fourth-component-numerically",
        ),
        pytest.param(
            "platform_release >= '6.8'",
            "platform_release == '6.8.0.1'",
            True,
            id="platform-release-compares-short-and-long-release-segments",
        ),
        pytest.param(
            "platform_release >= '6.8.0.1'",
            "platform_release == '6.8'",
            False,
            id="platform-release-rejects-shorter-lower-release-segments",
        ),
        pytest.param(
            "platform_release == '6.8.0.1'",
            "platform_release == '6.8.0.1.0'",
            True,
            id="platform-release-normalizes-trailing-zero-components",
        ),
        pytest.param(
            "platform_release > '6.8.0'",
            "platform_release == '6.8.0.1'",
            True,
            id="platform-release-preserves-strict-longer-release-ordering",
        ),
        pytest.param(
            "platform_release == '6.8.0.*'",
            "platform_release == '6.8.0.2'",
            True,
            id="platform-release-wildcard-covers-longer-release-segments",
        ),
        pytest.param(
            "platform_release == '6.8.0.*'",
            "platform_release == '6.8.1.0'",
            False,
            id="platform-release-wildcard-does-not-cover-another-prefix",
        ),
        pytest.param(
            "platform_release >= '6.8.0.1.2'",
            "platform_release == '6.8.0.1.3'",
            True,
            id="platform-release-preserves-five-component-numeric-ordering",
        ),
        pytest.param(
            "platform_release >= '6'",
            "platform_release == '6.0.0.1'",
            True,
            id="platform-release-supports-single-component-numeric-floor",
        ),
        pytest.param(
            "platform_release >= ' 6.8.0.1 '",
            "platform_release == '6.8.0.2'",
            True,
            id="platform-release-normalizes-surrounding-version-whitespace",
        ),
        pytest.param(
            "platform_release >= '06.008.000.001'",
            "platform_release == '6.8.0.2'",
            True,
            id="platform-release-normalizes-component-leading-zeroes",
        ),
        pytest.param(
            "platform_release >= '6.8.1234567890.1'",
            "platform_release == '6.8.1234567890.2'",
            False,
            id="platform-release-rejects-unbounded-numeric-components",
        ),
        pytest.param(
            "platform_release >= '" + ".".join(["6"] * 33) + "'",
            "platform_release == '" + ".".join(["6"] * 33) + "'",
            False,
            id="platform-release-rejects-unbounded-release-component-count",
        ),
        pytest.param(
            "platform_release >= 'v6.8.0.1'",
            "platform_release == 'v6.8.0.2'",
            False,
            id="platform-release-unsupported-v-prefix-fails-closed",
        ),
        pytest.param(
            "platform_release >= '1!6.8.0.1'",
            "platform_release == '1!6.8.0.2'",
            False,
            id="platform-release-unsupported-epoch-fails-closed",
        ),
        pytest.param(
            "platform_release == '6.8.0.1+linux'",
            "platform_release == '6.8.0.1+linux'",
            False,
            id="platform-release-unsupported-local-label-fails-closed",
        ),
        pytest.param(
            "platform_release >= '6.10'",
            "platform_release == 'build-42'",
            False,
            id="platform-release-rejects-mixed-numeric-and-nonversion-domains",
        ),
        pytest.param(
            "platform_release != '6.8.0.1'",
            "platform_release == 'linux'",
            False,
            id="platform-release-rejects-four-component-version-against-nonversion-domain",
        ),
        pytest.param(
            "platform_release != ' 6.8.0.1 '",
            "platform_release == 'linux'",
            False,
            id="platform-release-rejects-whitespace-padded-version-against-nonversion-domain",
        ),
        pytest.param(
            "platform_release != '6'",
            "platform_release == 'linux'",
            False,
            id="platform-release-rejects-single-component-version-against-nonversion-domain",
        ),
        pytest.param(
            "platform_release != '1!6.8.0'",
            "platform_release == 'linux'",
            False,
            id="platform-release-rejects-epoch-version-against-nonversion-domain",
        ),
        pytest.param(
            "platform_release != '6.8.0.1rc1'",
            "platform_release == 'linux'",
            False,
            id="platform-release-rejects-prerelease-version-against-nonversion-domain",
        ),
        pytest.param(
            "platform_release != '6.8.0.1.post1'",
            "platform_release == 'linux'",
            False,
            id="platform-release-rejects-post-release-version-against-nonversion-domain",
        ),
        pytest.param(
            "platform_release != '6.8.0.1.dev1'",
            "platform_release == 'linux'",
            False,
            id="platform-release-rejects-development-version-against-nonversion-domain",
        ),
        pytest.param(
            "platform_release != '6.8.0.1+local'",
            "platform_release == 'linux'",
            False,
            id="platform-release-rejects-local-version-against-nonversion-domain",
        ),
        pytest.param(
            "platform_release != 'v6.8alpha1'",
            "platform_release == 'linux'",
            False,
            id="platform-release-rejects-normalized-version-against-nonversion-domain",
        ),
        pytest.param(
            "platform_release >= '6.8.0a1'",
            "platform_release == '6.8.0a2'",
            True,
            id="platform-release-preserves-numeric-prerelease-ordering",
        ),
        pytest.param(
            "platform_release >= '6.8.0.1a1'",
            "platform_release == '6.8.0.1a2'",
            True,
            id="platform-release-preserves-four-component-prerelease-ordering",
        ),
        pytest.param(
            "platform_release >= '6.8.0.post1'",
            "platform_release == '6.8.0.post2'",
            True,
            id="platform-release-preserves-numeric-post-release-ordering",
        ),
        pytest.param(
            "platform_release >= '6.8.0.1.post1'",
            "platform_release == '6.8.0.1.post2'",
            True,
            id="platform-release-preserves-four-component-post-release-ordering",
        ),
        pytest.param(
            "platform_release >= '6.8.0.dev1'",
            "platform_release == '6.8.0.dev2'",
            True,
            id="platform-release-preserves-numeric-development-ordering",
        ),
        pytest.param(
            "platform_release >= '6.8.0.1.dev1'",
            "platform_release == '6.8.0.1.dev2'",
            True,
            id="platform-release-preserves-four-component-development-ordering",
        ),
        pytest.param(
            "platform_release != 'build-42'",
            "platform_release == '6.9.0'",
            True,
            id="platform-release-string-exclusions-preserve-numeric-domains",
        ),
        pytest.param(
            "platform_release === '6.10.0'",
            "platform_release == '6.10'",
            False,
            id="platform-release-arbitrary-equality-cannot-cover-normalized-domain",
        ),
        pytest.param(
            "platform_version == 'build-42'",
            "platform_version == 'build-42'",
            True,
            id="platform-version-marker-is-supported",
        ),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_additional_pep508_marker_variables_preserve_security_domains(
    tmp_path: Path, requirement_marker: str, resolution_marker: str, accepted: bool, protected: bool
) -> None:
    previous = "danger>=1; " + requirement_marker
    updated = "danger>=2; " + requirement_marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [updated],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=[updated] if protected else None,
        base_resolution_markers={("danger", "1"): [resolution_marker]},
        head_resolution_markers={("danger", "2"): [resolution_marker]},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("original", "addition", "accepted"),
    [
        pytest.param("sniffio", "sniffio[feature]", True, id="new-unbounded-extra-retains-unbounded-parent"),
        pytest.param("sniffio", "sniffio[feature]<2", False, id="new-extra-cannot-add-unreviewed-upper-bound"),
        pytest.param("sniffio", "sniffio[feature]>=1", False, id="new-extra-cannot-add-unreviewed-lower-bound"),
        pytest.param(
            "sniffio>=1,<3", "sniffio[feature]>=1,<3", True, id="new-extra-may-repeat-existing-reviewed-bounds"
        ),
        pytest.param(
            "sniffio>=1,<3", "sniffio[feature]>=1,<2", False, id="new-extra-cannot-narrow-existing-reviewed-bounds"
        ),
    ],
)
def test_new_requested_extras_cannot_narrow_existing_published_bounds(
    tmp_path: Path, original: str, addition: str, accepted: bool
) -> None:
    optional: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {("sniffio", "1.5"): {"feature": []}}
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1", original],
        head_requirements=["patch-me>=1.1", original, addition],
        base_packages=[("patch-me", "1"), ("sniffio", "1.5")],
        head_packages=[("patch-me", "1.1"), ("sniffio", "1.5")],
        base_lock_optional_dependencies=optional,
        head_lock_optional_dependencies=optional,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("addition", "accepted"),
    [
        pytest.param("sniffio[feature]>=1,<3", True, id="optional-extra-may-repeat-reviewed-runtime-bounds"),
        pytest.param("sniffio[feature]>=1,<2", False, id="optional-extra-cannot-narrow-reviewed-runtime-bounds"),
    ],
)
def test_optional_requested_extras_preserve_existing_runtime_bounds(
    tmp_path: Path, addition: str, accepted: bool
) -> None:
    optional: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {("sniffio", "1.5"): {"feature": []}}
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1", "sniffio>=1,<3"],
        head_requirements=["patch-me>=1.1", "sniffio>=1,<3"],
        base_packages=[("patch-me", "1"), ("sniffio", "1.5")],
        head_packages=[("patch-me", "1.1"), ("sniffio", "1.5")],
        head_optional_groups={"feature": [addition]},
        base_lock_optional_dependencies=optional,
        head_lock_optional_dependencies=optional,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("previous_marker", "requested_marker", "accepted"),
    [
        pytest.param(
            "python_version ~= '3.10'",
            "python_version ~= '3.10'",
            True,
            id="compatible-marker-preserves-previously-published-extra-audience",
        ),
        pytest.param(
            "python_version === '3.10'",
            "python_version === '3.10'",
            True,
            id="arbitrary-equality-preserves-previously-published-extra-audience",
        ),
        pytest.param(
            "python_version ~= '3.10'",
            "python_version ~= '4.0'",
            False,
            id="compatible-extra-marker-cannot-expose-unreviewed-major",
        ),
        pytest.param(
            "python_version === '3.10'",
            "python_version === '3.11'",
            False,
            id="arbitrary-equality-extra-marker-cannot-expose-unreviewed-minor",
        ),
    ],
)
def test_new_extra_reachability_compares_pep508_version_marker_audiences(
    tmp_path: Path, previous_marker: str, requested_marker: str, accepted: bool
) -> None:
    previous = [("existing-parent", "1"), ("parent", "1"), ("plugin", "1")]
    edges: dict[tuple[str, str], list[dict[str, object]]] = {
        ("existing-parent", "1"): [{"name": "plugin", "marker": previous_marker}]
    }
    optional: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {
        ("parent", "1"): {"feature": [{"name": "plugin"}]}
    }
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1", "existing-parent", "parent"],
        head_requirements=[
            "patch-me>=1.1",
            "existing-parent",
            "parent",
            "parent[feature]; " + requested_marker,
        ],
        base_packages=[("patch-me", "1"), *previous],
        head_packages=[("patch-me", "1.1"), *previous],
        base_lock_dependencies=edges,
        head_lock_dependencies=edges,
        base_lock_optional_dependencies=optional,
        head_lock_optional_dependencies=optional,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variable", "compatible", "release"),
    [
        pytest.param("platform_release", "6.8", "6.9", id="two-component-compatible-range-keeps-next-minor"),
        pytest.param("platform_release", "6.8", "7.0", id="two-component-compatible-range-rejects-next-major"),
        pytest.param("platform_release", "6.8.0", "6.8.9", id="three-component-compatible-range-keeps-next-patch"),
        pytest.param("platform_release", "6.8.0", "6.9", id="three-component-compatible-range-rejects-next-minor"),
        pytest.param("platform_release", "6.8.0.1", "6.8.0.1", id="four-component-compatible-range-keeps-lower-bound"),
        pytest.param("platform_release", "6.8.0.1", "6.8.0.2", id="four-component-compatible-range-keeps-next-build"),
        pytest.param("platform_release", "6.8.0.1", "6.8.1", id="four-component-compatible-range-rejects-next-patch"),
        pytest.param(
            "platform_release", "6.8.0.1", "6.8.1a1", id="four-component-compatible-range-rejects-next-patch-alpha"
        ),
        pytest.param(
            "platform_release", "6.8.0.1", "6.8.1.dev1", id="four-component-compatible-range-rejects-next-patch-dev"
        ),
        pytest.param(
            "platform_release", "6.8.0.1.2", "6.8.0.1.3", id="five-component-compatible-range-keeps-next-build"
        ),
        pytest.param(
            "platform_release", "6.8.0.1.2", "6.8.0.2", id="five-component-compatible-range-rejects-next-build-series"
        ),
        pytest.param(
            "platform_release", "6.8.0.1.0", "6.8.0.1.9", id="trailing-zero-compatible-range-preserves-precision"
        ),
        pytest.param(
            "platform_release", "6.8.0.1.0", "6.8.0.2", id="trailing-zero-compatible-range-rejects-next-series"
        ),
        pytest.param(
            "platform_release", "06.008.000.001", "6.8.0.2", id="compatible-range-normalizes-release-leading-zeroes"
        ),
        pytest.param("platform_release", "6.8.0.1a1", "6.8.0.1a2", id="compatible-alpha-range-keeps-later-alpha"),
        pytest.param("platform_release", "6.8.0.1a1", "6.8.0.1b1", id="compatible-alpha-range-keeps-later-beta"),
        pytest.param("platform_release", "6.8.0.1a1", "6.8.0.2", id="compatible-alpha-range-keeps-next-build"),
        pytest.param("platform_release", "6.8.0.1a1", "6.8.1a1", id="compatible-alpha-range-rejects-next-series"),
        pytest.param("platform_release", "6.8.0.1.post2", "6.8.0.1.post1", id="compatible-post-range-rejects-old-post"),
        pytest.param("platform_release", "6.8.0.1.post2", "6.8.0.1.post3", id="compatible-post-range-keeps-later-post"),
        pytest.param("platform_release", "6.8.0.1.post2", "6.8.0.2", id="compatible-post-range-keeps-next-build"),
        pytest.param("platform_release", "6.8.0.1.dev2", "6.8.0.1.dev1", id="compatible-dev-range-rejects-earlier-dev"),
        pytest.param("platform_release", "6.8.0.1.dev2", "6.8.0.1a1", id="compatible-dev-range-keeps-alpha"),
        pytest.param("platform_release", "6.8.0.1.dev2", "6.8.0.1", id="compatible-dev-range-keeps-final"),
        pytest.param(
            "platform_release", "6.8.0.1a1.post2.dev1", "6.8.0.1a1.post2", id="compatible-combined-suffix-range"
        ),
        pytest.param(
            "python_full_version", "3.10.0.1", "3.10.0.2", id="full-python-version-supports-four-component-range"
        ),
        pytest.param(
            "python_full_version", "3.10.0.1", "3.10.1", id="full-python-version-preserves-four-component-ceiling"
        ),
        pytest.param(
            "python_full_version", "3.10.0.1.2", "3.10.0.1.3", id="full-python-version-supports-five-component-range"
        ),
        pytest.param(
            "implementation_version", "3.10.0.1", "3.10.0.2", id="implementation-version-supports-four-component-range"
        ),
        pytest.param(
            "implementation_version", "3.10.0.1", "3.10.1", id="implementation-version-preserves-four-component-ceiling"
        ),
        pytest.param("python_version", "3.10.0", "3.10", id="python-minor-compatible-range-projects-zero-micro"),
        pytest.param("python_version", "3.10.0", "3.11", id="python-minor-compatible-range-preserves-micro-ceiling"),
        pytest.param("python_version", "3.10.0.0", "3.10", id="python-minor-compatible-range-projects-zero-build"),
        pytest.param("python_version", "3.10.0.1", "3.10", id="python-minor-compatible-range-rejects-nonzero-build"),
        pytest.param("python_version", "3.10.1", "3.10", id="python-minor-compatible-range-rejects-nonzero-micro"),
        pytest.param("python_version", "3.10.0a1", "3.10", id="python-minor-compatible-range-keeps-prerelease-floor"),
        pytest.param("python_version", "3.10.0.post1", "3.10", id="python-minor-compatible-range-rejects-post-floor"),
        pytest.param("python_version", "3.10.post1", "3.11", id="two-component-python-post-floor-keeps-next-minor"),
        pytest.param("python_version", "3.10.post1", "3.10", id="two-component-python-post-floor-rejects-same-minor"),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_arbitrary_width_compatible_markers_match_packaging(
    tmp_path: Path, variable: str, compatible: str, release: str, protected: bool
) -> None:
    marker = f"{variable} ~= '{compatible}'"
    expected = Marker(marker).evaluate(environment={variable: release})
    resolution = f"{variable} == '{release}'"
    previous, updated = "danger>=1; " + marker, "danger>=2; " + marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [updated],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=[updated] if protected else None,
        base_resolution_markers={("danger", "1"): [resolution]},
        head_resolution_markers={("danger", "2"): [resolution]},
    )
    assert result.returncode == (0 if expected else 1), result.stdout + result.stderr


@pytest.mark.parametrize("variable", ["python_full_version", "implementation_version"])
@pytest.mark.parametrize(
    ("operator", "operand", "release"),
    [
        pytest.param("==", "3.10.0.1", "3.10.0.1", id="wide-pep440-equality"),
        pytest.param("!=", "3.10.0.1", "3.10.0.1", id="wide-pep440-inequality"),
        pytest.param("<", "3.10.0.2", "3.10.0.1", id="wide-exclusive-ceiling"),
        pytest.param("<=", "3.10.0.1", "3.10.0.1", id="wide-inclusive-ceiling"),
        pytest.param(">", "3.10.0.1", "3.10.0.2", id="wide-exclusive-floor"),
        pytest.param(">=", "3.10.0.1", "3.10.0.1", id="wide-inclusive-floor"),
        pytest.param("~=", "3.10.0.1", "3.10.0.2", id="wide-compatible-range"),
        pytest.param("===", "3.10.0", "3.10.0", id="canonical-raw-equality"),
        pytest.param("===", "3.10.0", "3.10.1", id="canonical-raw-equality-rejects-other-patch"),
        pytest.param("in", "3.10.0.1, 3.10.0.2", "3.10.0", id="wide-membership-retains-real-python-version"),
        pytest.param("in", "3.10.0.1, 3.10.0.2", "3.10.3", id="wide-membership-rejects-other-python-version"),
        pytest.param("not in", "3.10.0.1, 3.10.0.2", "3.10.0", id="wide-negative-membership-excludes-real-version"),
        pytest.param("not in", "3.10.0.1, 3.10.0.2", "3.10.3", id="wide-negative-membership-keeps-other-version"),
        pytest.param("in", "3.10.0.10", "3.10.0", id="wide-membership-preserves-canonical-raw-prefix"),
        pytest.param("not in", "3.10.0.10", "3.10.0", id="wide-negative-membership-preserves-canonical-prefix"),
        pytest.param("===", "3.10.0a1", "3.10.0a1", id="canonical-raw-prerelease-equality"),
        pytest.param("in", "3.10.0.post1", "3.10.0.post1", id="canonical-postrelease-membership"),
        pytest.param("not in", "3.10.0.dev1", "3.10.0.dev1", id="canonical-development-negative-membership"),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_arbitrary_width_python_marker_operators_match_packaging(
    tmp_path: Path, variable: str, operator: str, operand: str, release: str, protected: bool
) -> None:
    marker = f"{variable} {operator} '{operand}'"
    expected = Marker(marker).evaluate(environment={variable: release})
    resolution = f"{variable} == '{release}'"
    previous, updated = "danger>=1; " + marker, "danger>=2; " + marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [updated],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=[updated] if protected else None,
        base_resolution_markers={("danger", "1"): [resolution]},
        head_resolution_markers={("danger", "2"): [resolution]},
    )
    assert result.returncode == (0 if expected else 1), result.stdout + result.stderr


@pytest.mark.parametrize("variable", ["python_full_version", "implementation_version"])
@pytest.mark.parametrize(
    "marker",
    [
        pytest.param("{variable} === '3.10.0.1'", id="wide-raw-equality-fails-closed"),
        pytest.param(
            "{variable} === '3.10.0' and {variable} === '3.10.0.0'",
            id="distinct-raw-equality-aliases-cannot-share-a-normalized-witness",
        ),
        pytest.param(
            "{variable} == '3.10.0a1' and {variable} in '3.10.0.0a1' and {variable} in '3.10.0a1'",
            id="distinct-prerelease-membership-aliases-cannot-share-a-normalized-witness",
        ),
        pytest.param(
            "{variable} === '3.10.0a1' and {variable} in '3.10.0.0a1'",
            id="raw-prerelease-equality-cannot-use-a-normalized-membership-alias",
        ),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_python_raw_marker_operators_cannot_merge_distinct_release_aliases(
    tmp_path: Path, variable: str, marker: str, protected: bool
) -> None:
    expression = marker.format(variable=variable)
    previous, updated = "danger>=1; " + expression, "danger>=2; " + expression
    release = "3.10.0a1" if "a1" in expression else "3.10.0.1" if "3.10.0.1" in expression else "3.10.0"
    resolution = f"{variable} == '{release}'"
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [updated],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=[updated] if protected else None,
        base_resolution_markers={("danger", "1"): [resolution]},
        head_resolution_markers={("danger", "2"): [resolution]},
    )
    assert result.returncode == 1, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variable", "compatible"),
    [
        pytest.param("platform_release", "6", id="single-component-compatible-operand-remains-invalid"),
        pytest.param("platform_release", "1!6.8.0.1", id="unsupported-compatible-epoch-fails-closed"),
        pytest.param("platform_release", "6.8.0.1+local", id="unsupported-compatible-local-version-fails-closed"),
        pytest.param("platform_release", "6.8.1234567890.1", id="unbounded-compatible-release-component-fails-closed"),
        pytest.param("platform_release", "6.8.0.1a1234567890", id="unbounded-compatible-alpha-serial-fails-closed"),
        pytest.param(
            "platform_release", "6.8.0.1.post1234567890", id="unbounded-compatible-postrelease-serial-fails-closed"
        ),
        pytest.param("platform_release", ".".join(["6"] * 33), id="unbounded-platform-compatible-width-fails-closed"),
        pytest.param(
            "python_full_version",
            ".".join(["3", "10", *(["0"] * 31)]),
            id="unbounded-python-compatible-width-fails-closed",
        ),
        pytest.param(
            "implementation_version",
            ".".join(["3", "10", *(["0"] * 31)]),
            id="unbounded-implementation-compatible-width-fails-closed",
        ),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_arbitrary_width_compatible_markers_preserve_fail_closed_bounds(
    tmp_path: Path, variable: str, compatible: str, protected: bool
) -> None:
    marker = f"{variable} ~= '{compatible}'"
    resolution = f"{variable} == '6.8.0.2'" if variable == "platform_release" else f"{variable} == '3.10.0'"
    previous, updated = "danger>=1; " + marker, "danger>=2; " + marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [updated],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=[updated] if protected else None,
        base_resolution_markers={("danger", "1"): [resolution]},
        head_resolution_markers={("danger", "2"): [resolution]},
    )
    assert result.returncode == 1, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("requirement_marker", "resolution_marker", "accepted"),
    [
        pytest.param(
            "python_version ~= '3.10'",
            "python_full_version == '3.11.4'",
            True,
            id="compatible-python-marker-includes-next-supported-minor",
        ),
        pytest.param(
            "python_version ~= '3.10'",
            "python_full_version == '4.0.1'",
            False,
            id="compatible-python-marker-rejects-next-major",
        ),
        pytest.param(
            "python_version ~= '3.10'",
            "python_full_version == '3.9.9'",
            False,
            id="compatible-python-marker-rejects-lower-minor",
        ),
        pytest.param(
            "python_version === '3.10'",
            "python_full_version == '3.10.4'",
            True,
            id="arbitrary-equality-python-marker-includes-exact-minor",
        ),
        pytest.param(
            "python_version === '3.10'",
            "python_full_version == '3.11.4'",
            False,
            id="arbitrary-equality-python-marker-excludes-other-minor",
        ),
        pytest.param(
            "implementation_version ~= '3.10'",
            "implementation_version == '3.11.4'",
            True,
            id="compatible-implementation-marker-includes-next-minor",
        ),
        pytest.param(
            "implementation_version ~= '3.10'",
            "implementation_version == '4.0.1'",
            False,
            id="compatible-implementation-marker-rejects-next-major",
        ),
        pytest.param(
            "python_version >= '3.10'",
            "python_full_version ~= '3.10.0'",
            True,
            id="compatible-resolution-marker-is-supported",
        ),
        pytest.param(
            "python_version is '3.10'",
            "python_full_version == '3.10.4'",
            False,
            id="raw-python-is-operator-is-not-a-pep508-marker",
        ),
        pytest.param(
            "python_version is not '3.10'",
            "python_full_version == '3.10.4'",
            False,
            id="raw-python-is-not-operator-is-not-a-pep508-marker",
        ),
        pytest.param(
            "python_version >= '3.10'",
            "python_full_version is '3.10.4'",
            False,
            id="raw-python-is-operator-is-rejected-in-resolution-marker",
        ),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_pep508_compatible_and_arbitrary_equality_marker_operators(
    tmp_path: Path, requirement_marker: str, resolution_marker: str, accepted: bool, protected: bool
) -> None:
    previous = "danger>=1; " + requirement_marker
    updated = "danger>=2; " + requirement_marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [updated],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=[updated] if protected else None,
        base_resolution_markers={("danger", "1"): [resolution_marker]},
        head_resolution_markers={("danger", "2"): [resolution_marker]},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("requirement_marker", "resolution_marker", "accepted"),
    [
        pytest.param(
            "python_full_version >= '3.15.0a1'",
            "python_full_version == '3.15.0a1'",
            True,
            id="alpha-bound-includes-exact-prerelease",
        ),
        pytest.param(
            "python_full_version >= '3.15.0a2'",
            "python_full_version == '3.15.0a1'",
            False,
            id="alpha-bound-rejects-earlier-alpha",
        ),
        pytest.param(
            "python_full_version >= '3.15.0a2'",
            "python_full_version == '3.15.0b1'",
            True,
            id="alpha-precedes-beta",
        ),
        pytest.param(
            "python_full_version >= '3.15.0b2'",
            "python_full_version == '3.15.0a9'",
            False,
            id="beta-bound-rejects-alpha",
        ),
        pytest.param(
            "python_full_version >= '3.15.0rc1'",
            "python_full_version == '3.15.0b9'",
            False,
            id="release-candidate-bound-rejects-beta",
        ),
        pytest.param(
            "python_full_version >= '3.15.0rc1'",
            "python_full_version == '3.15.0'",
            True,
            id="release-candidate-precedes-final",
        ),
        pytest.param(
            "python_full_version >= '3.15.0'",
            "python_full_version == '3.15.0rc1'",
            False,
            id="final-bound-rejects-release-candidate",
        ),
        pytest.param(
            "python_full_version < '3.15.0'",
            "python_full_version == '3.15.0rc1'",
            False,
            id="exclusive-final-ceiling-excludes-matching-release-prereleases",
        ),
        pytest.param(
            "python_full_version <= '3.15.0'",
            "python_full_version == '3.15.0rc1'",
            True,
            id="inclusive-final-ceiling-includes-release-candidate",
        ),
        pytest.param(
            "python_full_version > '3.15.0a1'",
            "python_full_version == '3.15.0a2'",
            True,
            id="exclusive-alpha-bound-includes-later-alpha",
        ),
        pytest.param(
            "python_full_version > '3.15.0a1'",
            "python_full_version == '3.15.0a1.post1'",
            False,
            id="exclusive-alpha-bound-excludes-post-release-of-same-alpha",
        ),
        pytest.param(
            "python_full_version > '3.15.0a1'",
            "python_full_version == '3.15.0a1.post1.dev1'",
            False,
            id="exclusive-alpha-bound-excludes-development-build-of-same-alpha-post-release",
        ),
        pytest.param(
            "python_full_version > '3.15.0b1'",
            "python_full_version == '3.15.0b1.post2'",
            False,
            id="exclusive-beta-bound-excludes-post-release-of-same-beta",
        ),
        pytest.param(
            "python_full_version > '3.15.0rc1'",
            "python_full_version == '3.15.0rc1.post1'",
            False,
            id="exclusive-release-candidate-bound-excludes-post-release-of-same-candidate",
        ),
        pytest.param(
            "implementation_version > '3.15.0a1'",
            "implementation_version == '3.15.0a1.post1'",
            False,
            id="exclusive-implementation-alpha-bound-excludes-post-release-of-same-alpha",
        ),
        pytest.param(
            "python_full_version > '3.15.0a1'",
            "python_full_version == '3.15.0a2.dev1'",
            True,
            id="exclusive-alpha-bound-includes-development-build-of-next-alpha",
        ),
        pytest.param(
            "python_full_version > '3.15.0a1.dev1'",
            "python_full_version == '3.15.0a1.post1'",
            True,
            id="exclusive-alpha-development-bound-includes-post-release-of-later-alpha",
        ),
        pytest.param(
            "python_full_version > '3.15.0a1.post1'",
            "python_full_version == '3.15.0a1.post2'",
            True,
            id="exclusive-alpha-post-release-bound-includes-later-post-releases",
        ),
        pytest.param(
            "python_full_version > '3.15.0a1.post1.dev1'",
            "python_full_version == '3.15.0a1.post1'",
            True,
            id="exclusive-alpha-post-development-bound-includes-its-post-release",
        ),
        pytest.param(
            "python_full_version < '3.15.0.post1'",
            "python_full_version == '3.15.0.post1.dev1'",
            False,
            id="exclusive-post-release-ceiling-excludes-its-own-development-build",
        ),
        pytest.param(
            "python_full_version < '3.15.0.post0'",
            "python_full_version == '3.15.0.post0.dev0'",
            False,
            id="exclusive-first-post-release-ceiling-excludes-its-own-development-build",
        ),
        pytest.param(
            "implementation_version < '3.15.0.post1'",
            "implementation_version == '3.15.0.post1.dev1'",
            False,
            id="exclusive-implementation-post-ceiling-excludes-its-own-development-build",
        ),
        pytest.param(
            "python_full_version <= '3.15.0.post1'",
            "python_full_version == '3.15.0.post1.dev1'",
            True,
            id="inclusive-post-release-ceiling-retains-its-own-development-build",
        ),
        pytest.param(
            "python_full_version < '3.15.0.post1'",
            "python_full_version == '3.15.0.post0.dev1'",
            True,
            id="exclusive-post-release-ceiling-retains-earlier-post-development-builds",
        ),
        pytest.param(
            "python_full_version < '3.15.0a1.post1'",
            "python_full_version == '3.15.0a1.post1.dev1'",
            True,
            id="exclusive-prerelease-post-ceiling-retains-its-own-development-build",
        ),
        pytest.param(
            "python_full_version < '3.15.0.post1.dev1'",
            "python_full_version == '3.15.0.post1.dev0'",
            True,
            id="exclusive-post-development-ceiling-retains-earlier-development-build",
        ),
        pytest.param(
            "python_full_version != '3.15.0a1'",
            "python_full_version == '3.15.0a1'",
            False,
            id="alpha-exclusion-removes-exact-prerelease",
        ),
        pytest.param(
            "python_full_version == '3.15.0a1'",
            "python_full_version == '3.15.0b1'",
            False,
            id="exact-alpha-excludes-later-prerelease-stages",
        ),
        pytest.param(
            "python_full_version == '3.15.0'",
            "python_full_version == '3.15.0a1'",
            False,
            id="exact-final-excludes-alpha",
        ),
        pytest.param(
            "python_full_version == '3.15.*'",
            "python_full_version == '3.15.0a1'",
            True,
            id="wildcard-minor-includes-alpha",
        ),
        pytest.param(
            "python_version == '3.15'",
            "python_full_version == '3.15.0a1'",
            True,
            id="python-minor-projection-includes-alpha",
        ),
        pytest.param(
            "python_version >= '3.15'",
            "python_full_version == '3.15.0a1'",
            True,
            id="python-minor-floor-includes-alpha",
        ),
        pytest.param(
            "python_version < '3.15'",
            "python_full_version == '3.15.0a1'",
            False,
            id="python-minor-ceiling-excludes-alpha-from-that-minor",
        ),
        pytest.param(
            "implementation_version >= '3.15.0a1'",
            "implementation_version == '3.15.0b2'",
            True,
            id="implementation-version-preserves-prerelease-ordering",
        ),
        pytest.param(
            "python_full_version ~= '3.15.0a1'",
            "python_full_version == '3.15.0b2'",
            True,
            id="compatible-alpha-bound-includes-beta",
        ),
        pytest.param(
            "python_full_version ~= '3.15.0a1'",
            "python_full_version == '3.16.0a1'",
            False,
            id="compatible-alpha-bound-excludes-next-minor-alpha",
        ),
        pytest.param(
            "python_full_version === '3.15.0a1'",
            "python_full_version == '3.15.0a1'",
            True,
            id="arbitrary-equality-preserves-alpha",
        ),
        pytest.param(
            "python_full_version in '3.15.0a1, 3.15.0b2'",
            "python_full_version == '3.15.0a1'",
            True,
            id="membership-preserves-alpha",
        ),
        pytest.param(
            "python_full_version not in '3.15.0a1, 3.15.0b2'",
            "python_full_version == '3.15.0a1'",
            False,
            id="negative-membership-excludes-alpha",
        ),
        pytest.param(
            "python_full_version in '3.15.0a1'",
            "python_full_version == '3.15.0'",
            True,
            id="membership-retains-final-substring-of-alpha",
        ),
        pytest.param(
            "python_full_version not in '3.15.0a1'",
            "python_full_version == '3.15.0'",
            False,
            id="negative-membership-excludes-final-substring-of-alpha",
        ),
        pytest.param(
            "python_full_version in '3.15.0a10'",
            "python_full_version == '3.15.0a1'",
            True,
            id="membership-retains-shorter-alpha-serial-substring",
        ),
        pytest.param(
            "python_full_version not in '3.15.0a10'",
            "python_full_version == '3.15.0a1'",
            False,
            id="negative-membership-excludes-shorter-alpha-serial-substring",
        ),
        pytest.param(
            "python_full_version >= '3.15.0z1'",
            "python_full_version == '3.15.0a1'",
            False,
            id="unknown-prerelease-stage-fails-closed",
        ),
        pytest.param(
            "python_full_version >= '3.15.0a'",
            "python_full_version == '3.15.0a1'",
            False,
            id="missing-prerelease-serial-fails-closed",
        ),
        pytest.param(
            "python_full_version >= '3.15.0.dev1'",
            "python_full_version == '3.15.0a1'",
            True,
            id="development-prerelease-precedes-alpha",
        ),
        pytest.param(
            "python_full_version >= '3.15.0.dev1'",
            "python_full_version == '3.15.0.dev2'",
            True,
            id="development-prerelease-ordering-preserves-later-builds",
        ),
        pytest.param(
            "python_full_version >= '3.15.0.dev2'",
            "python_full_version == '3.15.0.dev1'",
            False,
            id="development-prerelease-floor-rejects-earlier-builds",
        ),
        pytest.param(
            "python_full_version >= '3.15.0a1.dev2'",
            "python_full_version == '3.15.0a1.dev3'",
            True,
            id="alpha-development-builds-retain-their-own-ordering",
        ),
        pytest.param(
            "python_full_version >= '3.15.0.post1'",
            "python_full_version == '3.15.0.post2'",
            True,
            id="post-release-floor-preserves-later-post-releases",
        ),
        pytest.param(
            "python_full_version >= '3.15.0.post2'",
            "python_full_version == '3.15.0.post1'",
            False,
            id="post-release-floor-rejects-earlier-post-releases",
        ),
        pytest.param(
            "python_full_version >= '3.15.0.post1.dev2'",
            "python_full_version == '3.15.0.post1'",
            True,
            id="post-development-build-precedes-its-post-release",
        ),
        pytest.param(
            "python_full_version == '3.15.0'",
            "python_full_version == '3.15.0.post1'",
            False,
            id="exact-final-release-cannot-admit-a-post-release",
        ),
        pytest.param(
            "python_full_version > '3.15.0'",
            "python_full_version == '3.15.0.post1'",
            False,
            id="exclusive-final-floor-cannot-admit-same-release-post-versions",
        ),
        pytest.param(
            "implementation_version >= '3.15.0.post1'",
            "implementation_version == '3.15.0.post2'",
            True,
            id="implementation-version-preserves-post-release-ordering",
        ),
        pytest.param(
            "implementation_version >= '3.15.0.dev1'",
            "implementation_version == '3.15.0a1'",
            True,
            id="implementation-development-release-precedes-alpha",
        ),
        pytest.param(
            "python_version == '3.10.0'",
            "python_full_version == '3.10.4'",
            True,
            id="three-component-python-version-projects-zero-micro-to-minor",
        ),
        pytest.param(
            "python_version === '3.10'",
            "python_version == '3.10'",
            True,
            id="raw-python-version-equality-retains-exact-two-component-value",
        ),
        pytest.param(
            "python_version === '3.10.0'",
            "python_version == '3.10'",
            False,
            id="raw-python-version-equality-rejects-extra-zero-component",
        ),
        pytest.param(
            "python_version === '3.10.0'",
            "python_full_version == '3.10.4'",
            False,
            id="raw-python-version-equality-cannot-use-normalized-full-version",
        ),
        pytest.param(
            "python_version === '03.10'",
            "python_version == '3.10'",
            False,
            id="raw-python-version-equality-rejects-zero-padded-components",
        ),
        pytest.param(
            "python_version == '3.10.1'",
            "python_full_version == '3.10.1'",
            False,
            id="python-version-nonzero-micro-does-not-falsely-match-minor",
        ),
        pytest.param(
            "python_full_version in '3.15.0.dev1, 3.15.0.post2'",
            "python_full_version == '3.15.0.dev1'",
            True,
            id="membership-retains-development-and-post-release-operands",
        ),
        pytest.param(
            "python_full_version === '3.15.0.post2'",
            "python_full_version == '3.15.0.post2'",
            True,
            id="arbitrary-equality-preserves-post-release-identities",
        ),
        pytest.param(
            "python_full_version >= '3.15.0.post1'",
            "python_full_version == '3.15.0a1'",
            False,
            id="post-release-floor-rejects-earlier-prerelease-stages",
        ),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_prerelease_python_markers_preserve_pep440_security_domains(
    tmp_path: Path, requirement_marker: str, resolution_marker: str, accepted: bool, protected: bool
) -> None:
    previous = "danger>=1; " + requirement_marker
    updated = "danger>=2; " + requirement_marker
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=[] if protected else [previous],
        head_requirements=[] if protected else [updated],
        base_packages=[("danger", "1")],
        head_packages=[("danger", "2")],
        base_constraints=[previous] if protected else None,
        head_constraints=[updated] if protected else None,
        base_resolution_markers={("danger", "1"): [resolution_marker]},
        head_resolution_markers={("danger", "2"): [resolution_marker]},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("resolution_marker", "protected_markers", "accepted"),
    [
        pytest.param(
            "python_full_version >= '3.15.0a1'",
            ["python_full_version >= '3.15.0'"],
            False,
            id="final-only-protection-cannot-hide-unprotected-prerelease-domain",
        ),
        pytest.param(
            "python_version == '3.15'",
            ["python_full_version >= '3.15.0'"],
            False,
            id="final-only-protection-cannot-hide-prerelease-minor-projection",
        ),
        pytest.param(
            "python_full_version >= '3.14.0'",
            ["python_full_version < '3.15.0'", "python_full_version >= '3.15.0'"],
            False,
            id="ordered-final-complements-cannot-hide-prerelease-gap",
        ),
        pytest.param(
            "python_full_version >= '3.15.0a1'",
            ["python_full_version >= '3.15.0a1'"],
            True,
            id="reviewed-prerelease-floor-covers-complete-prerelease-domain",
        ),
    ],
)
def test_transitive_prerelease_security_boundaries_cannot_hide_unprotected_domains(
    tmp_path: Path, resolution_marker: str, protected_markers: list[str], accepted: bool
) -> None:
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1"],
        head_requirements=["patch-me>=1.1"],
        base_packages=[("patch-me", "1"), ("danger", "1")],
        head_packages=[("patch-me", "1.1"), ("danger", "2")],
        base_constraints=["danger>=1; " + marker for marker in protected_markers],
        head_constraints=["danger>=2; " + marker for marker in protected_markers],
        base_resolution_markers={("danger", "1"): [resolution_marker]},
        head_resolution_markers={("danger", "2"): [resolution_marker]},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("marker", "accepted"),
    [
        pytest.param("python_version == '3.10.0'", True, id="pep440-equality-normalizes-zero-component"),
        pytest.param("python_version === '3.10'", True, id="raw-equality-covers-exact-python-minor"),
        pytest.param("python_version === '3.10.0'", False, id="raw-equality-cannot-fake-python-minor-coverage"),
        pytest.param("python_version === '3.10.00'", False, id="raw-equality-rejects-noncanonical-zero-component"),
        pytest.param("python_version === '03.10'", False, id="raw-equality-rejects-zero-padded-python-major"),
    ],
)
@pytest.mark.parametrize("scope", ["constraint", "build", "group"])
def test_transitive_python_security_boundaries_preserve_raw_arbitrary_equality(
    tmp_path: Path, marker: str, accepted: bool, scope: str
) -> None:
    previous, updated = "danger>=1; " + marker, "danger>=2; " + marker
    resolution = "python_version == '3.10'"
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1"],
        head_requirements=["patch-me>=1.1"],
        base_packages=[("patch-me", "1"), ("danger", "1")],
        head_packages=[("patch-me", "1.1"), ("danger", "2")],
        base_constraints=[previous] if scope == "constraint" else None,
        head_constraints=[updated] if scope == "constraint" else None,
        base_build_constraints=[previous] if scope == "build" else None,
        head_build_constraints=[updated] if scope == "build" else None,
        base_dependency_groups={"reviewed": [previous]} if scope == "group" else None,
        head_dependency_groups={"reviewed": [updated]} if scope == "group" else None,
        base_resolution_markers={("danger", "1"): [resolution]},
        head_resolution_markers={("danger", "2"): [resolution]},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("previous_markers", "updated_markers", "accepted"),
    [
        pytest.param(
            ["python_full_version < '3.12'"],
            [
                "python_full_version < '3.11'",
                "python_full_version >= '3.11' and python_full_version < '3.12'",
            ],
            True,
            id="stable-only-lock-refinement-keeps-existing-complement-semantics",
        ),
        pytest.param(
            ["python_full_version >= '3.11.0a1' and python_full_version < '3.12'"],
            ["python_full_version >= '3.11' and python_full_version < '3.12'"],
            False,
            id="explicit-prerelease-lock-domain-cannot-be-dropped-during-refinement",
        ),
    ],
)
def test_resolution_refinement_preserves_explicit_prerelease_domains(
    tmp_path: Path, previous_markers: list[str], updated_markers: list[str], accepted: bool
) -> None:
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1"],
        head_requirements=["patch-me>=1.1"],
        base_packages=[("patch-me", "1"), ("danger", "2")],
        head_packages=[("patch-me", "1.1"), ("danger", "2")],
        base_resolution_markers={("danger", "2"): previous_markers},
        head_resolution_markers={("danger", "2"): updated_markers},
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("variable", "bound", "next_release"),
    [
        pytest.param("python_full_version", "3.15.0", "3.15.1", id="python-full-final-release"),
        pytest.param("python_full_version", "3.15.0a1", "3.15.0a2", id="python-full-prerelease"),
        pytest.param("implementation_version", "3.15.0", "3.15.1", id="implementation-final-release"),
        pytest.param("platform_release", "6.8.0", "6.8.1", id="platform-final-release"),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
@pytest.mark.parametrize("missing_posts", [False, True], ids=["complete-inclusive-domain", "missing-post-release-gap"])
@pytest.mark.parametrize("strict_floor", [False, True], ids=["inclusive-ceiling", "strict-floor"])
def test_inclusive_version_marker_partitions_preserve_post_release_contexts(
    tmp_path: Path,
    variable: str,
    bound: str,
    next_release: str,
    protected: bool,
    missing_posts: bool,
    strict_floor: bool,
) -> None:
    if strict_floor:
        original_marker = f"{variable} >= '{bound}.post0'" if missing_posts else f"{variable} > '{bound}'"
        replacement_marker = f"{variable} > '{bound}'"
    else:
        original_marker = f"{variable} < '{next_release}'" if missing_posts else f"{variable} <= '{bound}'"
        replacement_marker = f"{variable} <= '{bound}'"
    original = "danger>=1,<3; " + original_marker
    replacements = [
        f"danger>=1,<3; {replacement_marker} and sys_platform == 'linux'",
        f"danger>=1,<3; {replacement_marker} and sys_platform != 'linux'",
    ]
    resolutions = {
        ("danger", "1"): ["sys_platform == 'linux'"],
        ("danger", "2"): ["sys_platform != 'linux'"],
    }
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1"] + ([] if protected else [original]),
        head_requirements=["patch-me>=1.1"] + ([] if protected else replacements),
        base_packages=[("patch-me", "1"), ("danger", "1"), ("danger", "2")],
        head_packages=[("patch-me", "1.1"), ("danger", "1"), ("danger", "2")],
        base_constraints=[original] if protected else None,
        head_constraints=replacements if protected else None,
        base_resolution_markers=resolutions,
        head_resolution_markers=resolutions,
    )
    assert result.returncode == (1 if missing_posts else 0), result.stdout + result.stderr


@pytest.mark.parametrize("scope", ["runtime", "optional", "constraint", "build", "group"])
@pytest.mark.parametrize("marked", [False, True], ids=["unmarked", "marker-scoped"])
def test_arbitrary_equality_dependency_pins_can_track_reviewed_security_upgrades(
    tmp_path: Path, scope: str, marked: bool
) -> None:
    marker = "; python_version >= '3.11'" if marked else ""
    previous, current = "danger===1" + marker, "danger===2" + marker
    protected = scope in {"constraint", "build", "group"}
    resolutions = ["python_full_version >= '3.11'"] if marked else None
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1"] + ([] if protected else [previous]),
        head_requirements=["patch-me>=1.1"] + ([] if protected else [current]),
        base_packages=[("patch-me", "1"), ("danger", "1")],
        head_packages=[("patch-me", "1.1"), ("danger", "2")],
        optional=scope == "optional",
        base_constraints=[previous] if scope == "constraint" else None,
        head_constraints=[current] if scope == "constraint" else None,
        base_build_constraints=[previous] if scope == "build" else None,
        head_build_constraints=[current] if scope == "build" else None,
        base_dependency_groups={"reviewed": [previous]} if scope == "group" else None,
        head_dependency_groups={"reviewed": [current]} if scope == "group" else None,
        base_resolution_markers={("danger", "1"): resolutions} if resolutions is not None else None,
        head_resolution_markers={("danger", "2"): resolutions} if resolutions is not None else None,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("previous", "current", "before", "after", "accepted"),
    [
        pytest.param("danger===1", "danger===1", ["1"], ["1"], True, id="unchanged-canonical-arbitrary-pin"),
        pytest.param("danger===1.0", "danger===2.0", ["1.0"], ["2.0"], True, id="raw-dotted-arbitrary-pin-upgrade"),
        pytest.param("danger===1!1", "danger===1!2", ["1!1"], ["1!2"], True, id="raw-epoch-arbitrary-pin-upgrade"),
        pytest.param(
            "danger===1.post1",
            "danger===1.post2",
            ["1.post1"],
            ["1.post2"],
            True,
            id="raw-post-release-arbitrary-pin-upgrade",
        ),
        pytest.param("danger===1", "danger>=1", ["1"], ["1"], False, id="arbitrary-pin-cannot-widen-to-floor"),
        pytest.param("danger===1", "danger==1", ["1"], ["1"], False, id="arbitrary-pin-cannot-widen-to-pep440-pin"),
        pytest.param("danger==1", "danger===1", ["1"], ["1"], False, id="pep440-pin-cannot-narrow-to-arbitrary-pin"),
        pytest.param("danger===1", "danger===3", ["1"], ["2"], False, id="arbitrary-pin-must-match-patched-lock"),
        pytest.param("danger===2", "danger===1", ["2"], ["1"], False, id="arbitrary-pin-cannot-follow-downgrade"),
        pytest.param("danger===1", "danger===2", ["1", "2"], ["2"], False, id="arbitrary-pin-cannot-hide-old-alias"),
        pytest.param(
            "danger===1.0", "danger===2", ["1"], ["2"], False, id="trailing-zero-arbitrary-pin-is-not-raw-lock"
        ),
        pytest.param("danger===1", "danger===2", ["1.0"], ["2"], False, id="old-lock-alias-cannot-match-raw-pin"),
        pytest.param("danger===1", "danger===2", ["1"], ["2.0"], False, id="new-lock-alias-cannot-match-raw-pin"),
        pytest.param("danger===01", "danger===2", ["1"], ["2"], False, id="zero-padded-arbitrary-pin-fails-closed"),
        pytest.param("danger===0!1", "danger===2", ["1"], ["2"], False, id="epoch-arbitrary-pin-fails-closed"),
        pytest.param(
            "danger===1.post1",
            "danger===2",
            ["1.post01"],
            ["2"],
            False,
            id="post-release-arbitrary-pin-rejects-nonraw-serial",
        ),
        pytest.param("danger===1.*", "danger===2", ["1"], ["2"], False, id="wildcard-arbitrary-pin-fails-closed"),
    ],
)
@pytest.mark.parametrize("protected", [False, True], ids=["published-direct", "protected-constraint"])
def test_arbitrary_equality_dependency_pins_preserve_raw_security_boundaries(
    tmp_path: Path, previous: str, current: str, before: list[str], after: list[str], accepted: bool, protected: bool
) -> None:
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1"] + ([] if protected else [previous]),
        head_requirements=["patch-me>=1.1"] + ([] if protected else [current]),
        base_packages=[("patch-me", "1"), *[("danger", release) for release in before]],
        head_packages=[("patch-me", "1.1"), *[("danger", release) for release in after]],
        base_constraints=[previous] if protected else None,
        head_constraints=[current] if protected else None,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("pin", "locked", "accepted"),
    [
        pytest.param("plugin===1", "1", True, id="reviewed-arbitrary-pin-can-approve-new-extra-package"),
        pytest.param("plugin===1", "1.0", False, id="arbitrary-pin-cannot-approve-nonraw-extra-package-version"),
        pytest.param("plugin===1", "2", False, id="arbitrary-pin-cannot-approve-another-extra-package-version"),
    ],
)
def test_arbitrary_equality_pin_reviews_exact_new_extra_release(
    tmp_path: Path, pin: str, locked: str, accepted: bool
) -> None:
    optional: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = {
        ("parent", "1"): {"feature": [{"name": "plugin"}]}
    }
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1", "parent"],
        head_requirements=["patch-me>=1.1", "parent", "parent[feature]"],
        base_packages=[("patch-me", "1"), ("parent", "1")],
        head_packages=[("patch-me", "1.1"), ("parent", "1"), ("plugin", locked)],
        head_constraints=[pin],
        base_lock_optional_dependencies=optional,
        head_lock_optional_dependencies=optional,
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr


@pytest.mark.parametrize("optional", [False, True], ids=["published-runtime", "published-optional"])
@pytest.mark.parametrize(
    ("previous", "current"),
    [
        pytest.param("danger==1", "danger==1,===1", id="raw-pin-cannot-narrow-existing-pep440-equality"),
        pytest.param("danger>=1,<2", "danger>=1,<2,===1", id="raw-pin-cannot-narrow-existing-published-range"),
    ],
)
def test_new_arbitrary_equality_bound_cannot_narrow_existing_published_source(
    tmp_path: Path, previous: str, current: str, optional: bool
) -> None:
    result = run_security_dependency_floor_check(
        tmp_path,
        base_requirements=["patch-me>=1", previous],
        head_requirements=["patch-me>=1.1", current],
        base_packages=[("patch-me", "1"), ("danger", "1")],
        head_packages=[("patch-me", "1.1"), ("danger", "1")],
        optional=optional,
    )
    assert result.returncode != 0
