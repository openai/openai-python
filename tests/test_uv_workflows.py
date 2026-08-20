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
    uv_overrides: dict[str, object] | None = None,
    extra_uv_config: str | None = None,
    project_name: str | None = None,
    trusted_fork: bool = False,
    trusted_base_requires: list[str] | None = None,
    trusted_base_group: list[str] | None = None,
    trusted_base_constraints: list[str] | None = None,
    trusted_base_backend: str = "hatchling.build",
    trusted_base_sha: str = "a" * 40,
    trusted_origin: str = "https://github.com/openai/openai-python.git",
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
        for name, source in uv_sources.items():
            values = ", ".join(key + " = " + json.dumps(value) for key, value in source.items())
            configuration += name + " = { " + values + " }\n"
    (tmp_path / "pyproject.toml").write_text(configuration)
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
        (tmp_path / "trusted-base.toml").write_text(trusted_configuration)
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
        assert "openai-agents" not in global_environment
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


def test_agents_sdk_build_exemption_only_covers_its_trusted_editable_project() -> None:
    workflow = (ROOT / ".github/workflows/detect-breaking-changes.yml").read_text()
    match = re.search(r"^  agents_sdk:\n(?P<body>.*?)(?=^  [\w-]+:\n|\Z)", workflow, re.MULTILINE | re.DOTALL)
    assert match is not None
    job = match.group("body")
    trusted_checkout = job.index("repository: openai/openai-agents-python")
    exception = "UV_NO_BINARY_PACKAGE: 'openai openai-agents'"
    reviewed_aiohttp = 'UV_NO_BINARY_PACKAGE="openai openai-agents ${reviewed_sources}" make sync'
    assert job.count(exception) == 3
    assert job.count(reviewed_aiohttp) == 1

    for command in ("uv add --no-sync ../openai-python", "make sync", "make mypy"):
        command_index = job.index(command)
        assert command_index > trusted_checkout
        step_start = job.rfind("\n      - ", 0, command_index)
        step_end = job.find("\n      - ", command_index)
        if step_end < 0:
            step_end = len(job)
        step = job[step_start:step_end]
        assert "working-directory: openai-agents-python" in step
        assert exception in step
        if command == "make sync":
            assert reviewed_aiohttp in step

    assert exception not in job[:trusted_checkout]
    assert reviewed_aiohttp not in job[:trusted_checkout]


def test_agents_source_allowlist_uses_its_immutable_reviewed_checkout() -> None:
    workflow = (ROOT / ".github/workflows/detect-breaking-changes.yml").read_text()
    job = workflow.split("\n  agents_sdk:\n", 1)[1]
    checkout = re.search(
        r"repository: openai/openai-agents-python\n(?P<inputs>(?:          [^\n]+\n)+)",
        job,
    )
    assert checkout is not None
    assert re.search(
        r"^          ref: 7e55afc9500d12937687988f1e91e900dcb4ad09$", checkout.group("inputs"), re.MULTILINE
    )


def test_agents_type_checks_reuse_only_the_validated_preinstalled_environment() -> None:
    workflow = (ROOT / ".github/workflows/detect-breaking-changes.yml").read_text()
    job = workflow.split("\n  agents_sdk:\n", 1)[1]
    checks = job.split("      - name: Run integration type checks\n", 1)[1]
    assert "UV_NO_SYNC: '1'" in checks
    assert "UV_NO_BINARY_PACKAGE: 'openai openai-agents'" in checks
    assert "reviewed_sources" not in checks
    assert checks.index("UV_NO_SYNC") < checks.index("run: make mypy")
    assert job.index('${reviewed_sources}" make sync') < job.index("UV_NO_SYNC")


def test_agents_link_only_relocks_before_reviewed_source_distributions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workflow = (ROOT / ".github/workflows/detect-breaking-changes.yml").read_text()
    job = workflow.split("\n  agents_sdk:\n", 1)[1]
    link = job.split("      - name: Link to local SDK\n", 1)[1].split("\n      - name:", 1)[0]
    match = re.search(r"^        run: (.+)$", link, re.MULTILINE)
    assert match is not None
    command = match.group(1)
    assert command == "uv add --no-sync ../openai-python"
    assert "UV_NO_BINARY_PACKAGE: 'openai openai-agents'" in link
    assert "aiohttp" not in link
    assert job.index(command) < job.index("Use only the immutable reviewed Agents source distributions")
    assert job.index("Use only the immutable reviewed Agents source distributions") < job.index("make sync")

    executable = tmp_path / "uv"
    uv = shutil.which("uv")
    if uv is not None:
        supported = subprocess.run([uv, "add", "--help"], capture_output=True, text=True, check=False)
        assert supported.returncode == 0, supported.stdout + supported.stderr
        assert "--no-sync" in supported.stdout
        assert "Avoid syncing the virtual environment" in supported.stdout

    executable.write_text(
        f"#!{sys.executable}\n"
        "import json, os, pathlib, sys\n"
        "root = pathlib.Path(os.environ['UV_TEST_ROOT'])\n"
        "if '--no-sync' not in sys.argv:\n"
        "    (root / 'environment-synced').write_text('unreviewed install')\n"
        "    raise SystemExit('unsafe environment sync before source validation')\n"
        "(root / 'relocked.json').write_text(json.dumps({'args': sys.argv[1:], "
        "'no_build': os.environ.get('UV_NO_BUILD'), "
        "'no_binary': os.environ.get('UV_NO_BINARY_PACKAGE')}))\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("UV_TEST_ROOT", str(tmp_path))
    monkeypatch.setenv("UV_NO_BUILD", "1")
    monkeypatch.setenv("UV_NO_BINARY_PACKAGE", "openai openai-agents")
    result = subprocess.run(["bash", "-e", "-c", command], cwd=tmp_path, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (tmp_path / "environment-synced").exists()
    relocked = cast(dict[str, object], json.loads((tmp_path / "relocked.json").read_text()))
    assert relocked["args"] == ["add", "--no-sync", "../openai-python"]
    assert relocked["no_build"] == "1"
    assert relocked["no_binary"] == "openai openai-agents"


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


@pytest.mark.parametrize(
    ("variant", "accepted"),
    [
        pytest.param("reviewed", True, id="trusted-agents-aiohttp-source"),
        pytest.param("version", False, id="agents-aiohttp-version-swapped"),
        pytest.param("wheel-upgrade", True, id="changed-reviewed-name-is-wheel-only-without-source-exemption"),
        pytest.param("wheel-url", False, id="changed-reviewed-name-rejects-nonpublic-wheel"),
        pytest.param("wheel-hash", False, id="changed-reviewed-name-rejects-invalid-wheel-hash"),
        pytest.param("wheel-sdist-url", False, id="changed-reviewed-name-rejects-nonpublic-source-artifact"),
        pytest.param("wheel-sdist-hash", False, id="changed-reviewed-name-rejects-invalid-source-hash"),
        pytest.param("removed", True, id="removed-reviewed-name-receives-no-source-exemption"),
        pytest.param("source", False, id="agents-aiohttp-private-registry"),
        pytest.param("url", False, id="agents-aiohttp-source-url-swapped"),
        pytest.param("hash", False, id="agents-aiohttp-source-hash-swapped"),
        pytest.param("duplicate", False, id="agents-aiohttp-canonical-name-collision"),
        pytest.param("trusted-hash", False, id="upstream-aiohttp-source-must-be-reviewed"),
        pytest.param("origin", False, id="agents-checkout-origin-must-be-trusted"),
    ],
)
@pytest.mark.parametrize("package", ["aiohttp", "markupsafe", "pyyaml", "evdev"])
def test_agents_aiohttp_source_must_match_immutable_trusted_upstream(
    tmp_path: Path, variant: str, accepted: bool, package: str
) -> None:
    workflow = (ROOT / ".github/workflows/detect-breaking-changes.yml").read_text()
    line = next(
        entry
        for entry in workflow.splitlines()
        if "python -c '" in entry and "Use only the immutable reviewed Agents source distributions" in entry
    )
    program = line.split("python -c '", 1)[1].rsplit("'", 1)[0]
    if sys.version_info < (3, 11):
        program = "import sys, tomli; sys.modules['tomllib'] = tomli; " + program

    reviewed = {
        "aiohttp": (
            "3.12.15",
            "9b/e7/d92a237d8802ca88483906c388f7c201bbe96cd80a165ffd0ac2f6a8d59f/aiohttp-3.12.15.tar.gz",
            "4fc61385e9c98d72fcdf47e6dd81833f47b2f77c114c29cd64a361be57a763a2",
        ),
        "markupsafe": (
            "3.0.2",
            "b2/97/5d42485e71dfc078108a86d6de8fa46db44a1a9295e89c5d6d4a06e23a62/markupsafe-3.0.2.tar.gz",
            "ee55d3edf80167e48ea11a923c7386f4669df67d7994554387f84e7d8b0a2bf0",
        ),
        "pyyaml": (
            "6.0.2",
            "54/ed/79a089b6be93607fa5cdaedf301d7dfb23af5f25c398d5ead2525b063e17/pyyaml-6.0.2.tar.gz",
            "d584d9ec91ad65861cc08d42e834324ef890a082e591037abe114850ff7bbc3e",
        ),
        "evdev": (
            "1.9.2",
            "63/fe/a17c106a1f4061ce83f04d14bcedcfb2c38c7793ea56bfb906a6fadae8cb/evdev-1.9.2.tar.gz",
            "5d3278892ce1f92a74d6bf888cc8525d9f68af85dbe336c95d1c87fb8f423069",
        ),
    }
    version, artifact_path, digest = reviewed[package]
    url = "https://files.pythonhosted.org/packages/" + artifact_path
    current_version = version
    current_url = url
    current_digest = digest
    current_registry = "https://pypi.org/simple"
    trusted_digest = digest
    origin = "https://github.com/openai/openai-agents-python.git"
    current_wheel_url: str | None = None
    current_wheel_digest = "c" * 64
    if variant == "version":
        current_version = "0.0.1"
    elif variant == "source":
        current_registry = "https://private.example/simple"
    elif variant in {"wheel-upgrade", "wheel-url", "wheel-hash", "wheel-sdist-url", "wheel-sdist-hash"}:
        current_version = "3.14.3" if package == "aiohttp" else "9.0.0"
        current_url = "https://files.pythonhosted.org/packages/aa/bb/" + package + "-" + current_version + ".tar.gz"
        current_digest = "a" * 64
        current_wheel_url = (
            "https://files.pythonhosted.org/packages/aa/bb/" + package + "-" + current_version + "-py3-none-any.whl"
        )
        if variant == "wheel-url":
            current_wheel_url = "https://private.example/packages/" + package + ".whl"
        if variant == "wheel-hash":
            current_wheel_digest = "invalid"
        if variant == "wheel-sdist-url":
            current_url = "https://private.example/packages/" + package + ".tar.gz"
        if variant == "wheel-sdist-hash":
            current_digest = "invalid"
    elif variant == "url":
        current_url = "https://unreviewed.example/packages/aiohttp.tar.gz"
    elif variant == "hash":
        current_digest = "b" * 64
    elif variant == "trusted-hash":
        current_digest = trusted_digest = "b" * 64
    elif variant == "origin":
        origin = "https://github.com/unreviewed/openai-agents-python.git"

    def lock(
        name: str,
        version: str,
        artifact_url: str,
        artifact_digest: str,
        registry: str,
        wheel_url: str | None = None,
    ) -> str:
        return (
            "[[package]]\nname = "
            + json.dumps(name)
            + "\nversion = "
            + json.dumps(version)
            + "\nsource = { registry = "
            + json.dumps(registry)
            + " }\nsdist = { url = "
            + json.dumps(artifact_url)
            + ', hash = "sha256:'
            + artifact_digest
            + '" }\n'
            + (
                "wheels = [{ url = " + json.dumps(wheel_url) + ', hash = "sha256:' + current_wheel_digest + '" }]\n'
                if wheel_url is not None
                else ""
            )
        )

    current_packages: list[str] = []
    trusted_packages: list[str] = []
    for name, (reviewed_version, reviewed_path, reviewed_digest) in reviewed.items():
        reviewed_url = "https://files.pythonhosted.org/packages/" + reviewed_path
        if name == package:
            if variant != "removed":
                current_packages.append(
                    lock(name, current_version, current_url, current_digest, current_registry, current_wheel_url)
                )
            trusted_packages.append(
                lock(name, reviewed_version, reviewed_url, trusted_digest, "https://pypi.org/simple")
            )
        else:
            current_packages.append(
                lock(name, reviewed_version, reviewed_url, reviewed_digest, "https://pypi.org/simple")
            )
            trusted_packages.append(
                lock(name, reviewed_version, reviewed_url, reviewed_digest, "https://pypi.org/simple")
            )
    current = "\n".join(current_packages)
    if variant == "duplicate":
        current += "\n" + lock(package.upper(), current_version, current_url, current_digest, current_registry)
    (tmp_path / "uv.lock").write_text(current)
    (tmp_path / "upstream.lock").write_text("\n".join(trusted_packages))
    fake_git = tmp_path / "git"
    fake_git.write_text(
        f"#!{sys.executable}\n"
        "import pathlib, sys\n"
        f"root = pathlib.Path({str(tmp_path)!r})\n"
        f"origin = {origin!r}\n"
        "arguments = sys.argv[1:]\n"
        "if arguments == ['remote', 'get-url', 'origin']:\n"
        "    print(origin)\n"
        "elif arguments == ['show', 'HEAD:uv.lock']:\n"
        "    print((root / 'upstream.lock').read_text(), end='')\n"
        "else:\n"
        "    raise SystemExit('Unexpected Agents checkout operation')\n"
    )
    fake_git.chmod(0o755)
    environment = dict(os.environ, PATH=str(tmp_path) + os.pathsep + os.environ["PATH"])
    result = subprocess.run(
        [sys.executable, "-c", program], cwd=tmp_path, env=environment, capture_output=True, text=True, check=False
    )
    assert result.returncode == (0 if accepted else 1), result.stdout + result.stderr
    if accepted:
        expected = set(reviewed)
        if variant in {"wheel-upgrade", "removed"}:
            expected.remove(package)
        assert set(result.stdout.split()) == expected


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


def test_security_dependency_policy_is_directly_testable_after_the_trusted_gate() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()
    job = dependency_workflow_jobs()["dependency-locks"]
    gate = job.index("Verify dependency source provenance before installing tools")
    policy = job.index("python scripts/check-dependency-security.py")
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
    assert "run: python scripts/check-dependency-security.py" in body
    program = (ROOT / "scripts/check-dependency-security.py").read_text()
    if sys.version_info < (3, 11):
        program = program.replace(
            "from __future__ import annotations",
            "from __future__ import annotations\nimport sys, tomli; sys.modules['tomllib'] = tomli",
            1,
        )
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
    base_resolution_markers: dict[tuple[str, str], list[str]] | None = None,
    head_resolution_markers: dict[tuple[str, str], list[str]] | None = None,
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

    def lock(packages: list[tuple[str, str]], resolutions: dict[tuple[str, str], list[str]] | None) -> str:
        result: list[str] = []
        for name, version in packages:
            entry = f"[[package]]\nname = {json.dumps(name)}\nversion = {json.dumps(version)}\n"
            if resolutions is not None and (name, version) in resolutions:
                entry += "resolution-markers = " + json.dumps(resolutions[(name, version)]) + "\n"
            result.append(entry)
        return "\n".join(result)

    (tmp_path / "pyproject.toml").write_text(
        project(
            head_requirements, head_optional_groups, head_constraints, head_build_constraints, head_dependency_groups
        )
    )
    (tmp_path / "uv.lock").write_text(lock(head_packages, head_resolution_markers))
    (tmp_path / "base-project.toml").write_text(
        project(
            base_requirements, base_optional_groups, base_constraints, base_build_constraints, base_dependency_groups
        )
    )
    (tmp_path / "base-lock.toml").write_text(lock(base_packages, base_resolution_markers))
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
            True,
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
            True,
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
            True,
            id="platform-membership-preserves-quoted-case",
        ),
        pytest.param(
            "python_version >= '3.10'",
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
            False,
            False,
            id="substring-ambiguous-membership-token-fails-closed",
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
            False,
            False,
            id="substring-ambiguous-platform-membership-fails-closed",
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
            False,
            False,
            id="source-level-or-membership-fails-closed",
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
        pytest.param("marker-low-unaffected", True, id="protected-unrelated-marker-line-remains-unchanged"),
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
    elif variant == "unbounded-group":
        base_constraints = head_constraints = None
        base_groups = head_groups = {"dev": ["ruff"]}
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
