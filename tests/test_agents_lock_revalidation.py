from __future__ import annotations

import os
import sys
import copy
import json
import shutil
import textwrap
import subprocess
from typing import cast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/detect-breaking-changes.yml"
BASE_SHA = "a" * 40
REGISTRY = {"registry": "https://pypi.org/simple"}
REVIEWED_SOURCES = {
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


def _program() -> str:
    workflow = WORKFLOW.read_text()
    marker = "      - name: Verify relinked Agents lock package provenance\n"
    if marker in workflow:
        step = workflow.split(marker, 1)[1].split("      - name:", 1)[0]
        program = step.split("          python -I <<'PY'\n", 1)[1].split("          PY\n", 1)[0]
        return textwrap.dedent(program)

    line = next(
        line
        for line in workflow.splitlines()
        if "python -c '" in line and "Use only the immutable reviewed Agents source distributions" in line
    )
    return line.split("python -c '", 1)[1].rsplit("'", 1)[0]


def _constraints_program() -> str:
    workflow = WORKFLOW.read_text()
    marker = "      - name: Constrain Agents-only packages to reviewed locked versions\n"
    step = workflow.split(marker, 1)[1].split("      - name:", 1)[0]
    program = step.split("          python -I - \"$constraints\" <<'PY'\n", 1)[1].split("          PY\n", 1)[0]
    return textwrap.dedent(program)


def _artifact(name: str, version: str, digest: str, suffix: str) -> dict[str, str]:
    return {
        "url": "https://files.pythonhosted.org/packages/aa/bb/" + name + "-" + version + suffix,
        "hash": "sha256:" + digest * 64,
    }


def _package(
    name: str,
    version: str,
    *,
    source: dict[str, str] | None = None,
    sdist: bool = True,
    wheels: int = 1,
) -> dict[str, object]:
    package: dict[str, object] = {"name": name, "version": version, "source": source or REGISTRY.copy()}
    if source is not None and "registry" not in source:
        return package
    if sdist:
        package["sdist"] = _artifact(name, version, "a", ".tar.gz")
    if wheels:
        package["wheels"] = [
            _artifact(name, version, str(index + 1), "-" + str(index) + ".whl") for index in range(wheels)
        ]
    return package


def _lock(packages: list[dict[str, object]]) -> str:
    entries: list[str] = []
    for package in packages:
        lines = [
            "[[package]]",
            "name = " + json.dumps(package["name"]),
            "version = " + json.dumps(package["version"]),
        ]
        source = package["source"]
        assert isinstance(source, dict)
        typed_source = cast(dict[str, object], source)
        lines.append(
            "source = { " + ", ".join(key + " = " + json.dumps(value) for key, value in typed_source.items()) + " }"
        )
        sdist = package.get("sdist")
        if isinstance(sdist, dict):
            typed_sdist = cast(dict[str, object], sdist)
            lines.append(
                "sdist = { " + ", ".join(key + " = " + json.dumps(value) for key, value in typed_sdist.items()) + " }"
            )
        wheels = package.get("wheels")
        if isinstance(wheels, list):
            typed_wheels = cast(list[dict[str, object]], wheels)
            lines.append(
                "wheels = ["
                + ", ".join(
                    "{ " + ", ".join(key + " = " + json.dumps(value) for key, value in wheel.items()) + " }"
                    for wheel in typed_wheels
                )
                + "]"
            )
        entries.append("\n".join(lines))
    return "\n\n".join(entries) + "\n"


def _execute(
    tmp_path: Path, variant: str, *, fork: bool = True, constraints: bool = False
) -> subprocess.CompletedProcess[str]:
    agents = tmp_path / "agents"
    sdk = tmp_path / "openai-python"
    binaries = tmp_path / "bin"
    agents.mkdir()
    sdk.mkdir()
    binaries.mkdir()

    reviewed: list[dict[str, object]] = []
    for name, (version, path, digest) in REVIEWED_SOURCES.items():
        package = _package(name, version, wheels=0)
        package["sdist"] = {
            "url": "https://files.pythonhosted.org/packages/" + path,
            "hash": "sha256:" + digest,
        }
        reviewed.append(package)

    agents_root = _package("openai-agents", "0.22.0", source={"editable": "."})
    sdk_root = _package("openai", "3.3.1", source={"editable": "."})
    linked_sdk = _package("openai", "3.3.1", source={"directory": "../openai-python"})
    httpx = _package("httpx", "0.28.1", wheels=2)
    sdk_only = _package("sdk-only-lib", "1.0.0")
    wheel_only = _package("playwright", "1.0.0", sdist=False)
    old_sdk = _package("openai", "3.0.0")
    pynput = _package("pynput", "1.8.1")
    multiple = [_package("multi-version", "1.0.0"), _package("multi-version", "2.0.0")]
    trusted_agents = [agents_root, *reviewed, httpx, wheel_only, old_sdk, pynput, *multiple]
    trusted_sdk = [sdk_root, sdk_only, _package("httpx", "0.29.0")]
    current = copy.deepcopy([agents_root, linked_sdk, *reviewed, httpx, wheel_only, sdk_only])

    reviewed_pynput = _package("pynput", "1.6.8")
    reviewed_pynput_sdist: dict[str, str] = {
        "url": "https://files.pythonhosted.org/packages/e7/32/"
        "fa88984fc580de9e9fd08ee36dfd78ea15658d5b0268095785da7ab75ba0/pynput-1.6.8.tar.gz",
        "hash": "sha256:68c1863d6a1520b44b6a915e866cbfa1b8d127aef9289f25183c93e28ee5049a",
    }
    reviewed_pynput["sdist"] = reviewed_pynput_sdist
    reviewed_pynput_wheels: list[dict[str, str]] = [
        {
            "url": "https://files.pythonhosted.org/packages/33/0a/"
            "ea13c055a90b1aff5945e7eb330584f15e5282aead15a8f3cdb977a1534e/pynput-1.6.8-py2.py3-none-any.whl",
            "hash": "sha256:42d6d58abe401a4c98ea04e443e61f74b6b0f97672f42042f566c68700ad0c65",
        }
    ]
    reviewed_pynput["wheels"] = reviewed_pynput_wheels

    target = next(package for package in current if package["name"] == "httpx")
    if variant == "unreviewed-wheel":
        current.append(_package("unreviewed-wheel", "9.9.9", sdist=False))
    elif variant == "version":
        target["version"] = "9.9.9"
    elif variant == "sdk-reviewed-version":
        current[current.index(target)] = copy.deepcopy(trusted_sdk[-1])
    elif variant == "multiple-reviewed-versions":
        current.append(copy.deepcopy(trusted_sdk[-1]))
    elif variant == "wheel-url":
        wheels = target["wheels"]
        assert isinstance(wheels, list)
        wheels[0]["url"] = "https://files.pythonhosted.org/packages/aa/bb/replaced.whl"
    elif variant == "wheel-hash":
        wheels = target["wheels"]
        assert isinstance(wheels, list)
        wheels[0]["hash"] = "sha256:" + "f" * 64
    elif variant == "artifact-order":
        wheels = target["wheels"]
        assert isinstance(wheels, list)
        wheels.reverse()
    elif variant == "duplicate-artifact":
        wheels = target["wheels"]
        assert isinstance(wheels, list)
        typed_wheels = cast(list[dict[str, object]], wheels)
        typed_wheels.append(copy.deepcopy(typed_wheels[0]))
    elif variant == "missing-sdist":
        del target["sdist"]
    elif variant == "private-registry":
        target["source"] = {"registry": "https://private.example/simple"}
    elif variant == "no-artifacts":
        target.pop("sdist", None)
        target.pop("wheels", None)
    elif variant == "duplicate-name":
        duplicate = copy.deepcopy(sdk_only)
        duplicate["name"] = "SDK_only.lib"
        current.append(duplicate)
    elif variant == "extra-editable":
        current.append(_package("rogue-root", "1.0.0", source={"editable": "."}))
    elif variant == "sdk-editable":
        next(package for package in current if package["name"] == "openai")["source"] = {"editable": "../openai-python"}
    elif variant == "sdk-other-directory":
        next(package for package in current if package["name"] == "openai")["source"] = {"directory": "../other"}
    elif variant == "sdk-version":
        next(package for package in current if package["name"] == "openai")["version"] = "9.9.9"
    elif variant == "agents-version":
        next(package for package in current if package["name"] == "openai-agents")["version"] = "9.9.9"
    elif variant == "fork-submitted-lock":
        injected = _package("fork-submitted-wheel", "9.9.9", sdist=False)
        current.append(injected)
        submitted_sdk = copy.deepcopy(trusted_sdk) + [injected]
    elif variant == "fork-submitted-pynput":
        submitted_sdk = copy.deepcopy(trusted_sdk) + [_package("pynput", "1.8.2")]
    elif variant == "sdk-symlink":
        sdk.rmdir()
        outside = tmp_path / "outside"
        outside.mkdir()
        sdk.symlink_to(outside, target_is_directory=True)
    elif variant.startswith("pynput-"):
        current.append(reviewed_pynput)
        if variant == "pynput-version":
            reviewed_pynput["version"] = "1.6.9"
        elif variant == "pynput-registry":
            reviewed_pynput["source"] = {"registry": "https://private.example/simple"}
        elif variant == "pynput-sdist-url":
            reviewed_pynput_sdist["url"] += ".replaced"
        elif variant == "pynput-sdist-hash":
            reviewed_pynput_sdist["hash"] = "sha256:" + "b" * 64
        elif variant == "pynput-wheel-url":
            reviewed_pynput_wheels[0]["url"] = "https://files.pythonhosted.org/packages/aa/bb/replaced.whl"
        elif variant == "pynput-wheel-hash":
            reviewed_pynput_wheels[0]["hash"] = "sha256:" + "c" * 64
        elif variant == "pynput-extra-wheel":
            reviewed_pynput_wheels.append(_artifact("pynput", "1.6.8", "d", ".whl"))
        elif variant == "pynput-missing-wheel":
            reviewed_pynput.pop("wheels")
        elif variant == "pynput-missing-sdist":
            reviewed_pynput.pop("sdist")

    submitted_sdk = locals().get("submitted_sdk", copy.deepcopy(trusted_sdk))
    (agents / "uv.lock").write_text(_lock(current))
    (sdk / "uv.lock").write_text(_lock(submitted_sdk))
    (tmp_path / "trusted-agents.lock").write_text(_lock(trusted_agents))
    (tmp_path / "trusted-sdk.lock").write_text(_lock(trusted_sdk))

    fake_git = binaries / "git"
    fake_git.write_text(
        "#!" + sys.executable + "\n"
        "import os, pathlib, sys\n"
        "root = pathlib.Path(os.environ['TEST_LOCK_ROOT'])\n"
        "args = sys.argv[1:]\n"
        "if args == ['remote', 'get-url', 'origin']:\n"
        "    print('https://github.com/openai/openai-agents-python.git')\n"
        "elif args == ['show', 'HEAD:uv.lock']:\n"
        "    print((root / 'trusted-agents.lock').read_text(), end='')\n"
        "elif args == ['-C', '../openai-python', 'remote', 'get-url', 'origin']:\n"
        "    print('https://github.com/openai/openai-python.git')\n"
        "elif args == ['-C', '../openai-python', 'show', os.environ['TRUSTED_BUILD_BASE_SHA'] + ':uv.lock']:\n"
        "    print((root / 'trusted-sdk.lock').read_text(), end='')\n"
        "else:\n"
        "    raise SystemExit('unexpected git arguments: ' + repr(args))\n"
    )
    fake_git.chmod(0o755)
    environment = dict(os.environ)
    environment.update(
        {
            "PATH": str(binaries) + os.pathsep + os.environ["PATH"],
            "TEST_LOCK_ROOT": str(tmp_path),
            "UNTRUSTED_BUILD_FORK": "1" if fork else "0",
            "TRUSTED_BUILD_BASE_SHA": BASE_SHA,
            "RUNNER_TEMP": str(tmp_path),
        }
    )

    program = _constraints_program() if constraints else _program()
    if sys.version_info < (3, 11):
        program = "import sys, tomli; sys.modules['tomllib'] = tomli\n" + program
    arguments = [sys.executable, "-c", program]
    if constraints:
        constraints_path = tmp_path / "reviewed-constraints.txt"
        constraints_path.touch(mode=0o600)
        arguments.append(str(constraints_path))
    return subprocess.run(
        arguments,
        cwd=agents,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    "variant",
    [
        pytest.param("unreviewed-wheel", id="unreviewed-wheel-introduced-by-relock"),
        pytest.param("version", id="reviewed-package-version-re-resolved"),
        pytest.param("wheel-url", id="reviewed-wheel-url-substituted"),
        pytest.param("wheel-hash", id="reviewed-wheel-hash-substituted"),
        pytest.param("duplicate-artifact", id="duplicate-wheel-record"),
        pytest.param("missing-sdist", id="reviewed-source-artifact-removed"),
        pytest.param("private-registry", id="private-package-registry"),
        pytest.param("no-artifacts", id="artifact-free-registry-package"),
        pytest.param("duplicate-name", id="duplicate-canonical-package-identity"),
        pytest.param("extra-editable", id="unreviewed-editable-root"),
        pytest.param("sdk-editable", id="sdk-source-kind-changed"),
        pytest.param("sdk-other-directory", id="sdk-directory-escape"),
        pytest.param("sdk-version", id="unreviewed-local-sdk-version"),
        pytest.param("agents-version", id="unreviewed-agents-root-version"),
        pytest.param("fork-submitted-lock", id="fork-lock-cannot-expand-trusted-union"),
        pytest.param("sdk-symlink", id="local-sdk-symlink-escape"),
        pytest.param("pynput-version", id="curated-pynput-version-substituted"),
        pytest.param("pynput-registry", id="curated-pynput-private-registry"),
        pytest.param("pynput-sdist-url", id="curated-pynput-source-url-substituted"),
        pytest.param("pynput-sdist-hash", id="curated-pynput-source-digest-substituted"),
        pytest.param("pynput-wheel-url", id="curated-pynput-wheel-url-substituted"),
        pytest.param("pynput-wheel-hash", id="curated-pynput-wheel-digest-substituted"),
        pytest.param("pynput-extra-wheel", id="curated-pynput-extra-wheel"),
        pytest.param("pynput-missing-wheel", id="curated-pynput-wheel-removed"),
        pytest.param("pynput-missing-sdist", id="curated-pynput-source-removed"),
    ],
)
def test_relinked_agents_lock_rejects_unreviewed_package_identities(tmp_path: Path, variant: str) -> None:
    result = _execute(tmp_path, variant)
    assert result.returncode != 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "variant",
    [
        pytest.param("reviewed", id="trusted-union-includes-sdk-only-and-wheel-only"),
        pytest.param("artifact-order", id="wheel-order-is-not-security-significant"),
        pytest.param("sdk-reviewed-version", id="sdk-trusted-version-may-replace-agents-version"),
        pytest.param("multiple-reviewed-versions", id="distinct-reviewed-versions-of-same-name"),
        pytest.param("pynput-reviewed", id="curated-no-build-compatible-pynput-168-full-identity"),
    ],
)
@pytest.mark.parametrize("fork", [True, False], ids=["immutable-fork-base", "reviewed-same-repository"])
def test_relinked_agents_lock_accepts_complete_trusted_identities(tmp_path: Path, variant: str, fork: bool) -> None:
    result = _execute(tmp_path, variant, fork=fork)
    assert result.returncode == 0, result.stdout + result.stderr


def test_full_agents_lock_validation_runs_before_any_dependency_installation() -> None:
    workflow = WORKFLOW.read_text()
    link = workflow.index("run: uv add --no-sync ../openai-python")
    validation = workflow.index("- name: Verify relinked Agents lock package provenance")
    source_review = workflow.index("reviewed_sources=", validation)
    installation = workflow.index('UV_NO_BINARY_PACKAGE="openai openai-agents ${reviewed_sources}" make sync')
    assert link < validation < source_review < installation
    assert "          python -I <<'PY'\n" in workflow[validation:source_review]


def test_agents_sync_inherits_its_step_scoped_immutable_lock_policy(tmp_path: Path) -> None:
    workflow = WORKFLOW.read_text()
    link_step = workflow.split("      - name: Link to local SDK\n", 1)[1].split("      - name:", 1)[0]
    agents_workflow = workflow.split("      - name: Verify relinked Agents lock package provenance\n", 1)[1]
    install_step = agents_workflow.split("      - name: Install dependencies\n", 1)[1].split("      - name:", 1)[0]
    assert "UV_LOCKED:" not in link_step
    assert "          UV_LOCKED: '1'\n" in install_step
    command = next(line.strip() for line in install_step.splitlines() if line.strip().endswith(" make sync"))

    make = tmp_path / "make"
    make.write_text(
        "#!" + sys.executable + "\n"
        "import os, sys\n"
        "assert sys.argv[1:] == ['sync']\n"
        "assert os.environ['UV_LOCKED'] == '1'\n"
        "assert os.environ['UV_NO_BINARY_PACKAGE'] == 'openai openai-agents aiohttp'\n"
    )
    make.chmod(0o755)
    environment = dict(os.environ)
    environment["PATH"] = str(tmp_path) + os.pathsep + os.environ["PATH"]
    environment["UV_LOCKED"] = next(
        line.split(":", 1)[1].strip().strip("'") for line in install_step.splitlines() if "UV_LOCKED:" in line
    )
    result = subprocess.run(
        ["bash", "-ec", "reviewed_sources=aiohttp\n" + command],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_uv_locked_rejects_dependency_resolution_after_lock_validation(tmp_path: Path) -> None:
    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("uv is unavailable")

    project = tmp_path / "project"
    project.mkdir()
    pyproject = project / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "reviewed-project"\nversion = "1.0.0"\nrequires-python = ">=3.10"\ndependencies = []\n'
    )
    environment = dict(os.environ)
    environment["UV_CACHE_DIR"] = str(tmp_path / "cache")
    environment["UV_PYTHON_DOWNLOADS"] = "never"
    initial = subprocess.run(
        [uv, "--offline", "--directory", str(project), "lock"],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert initial.returncode == 0, initial.stdout + initial.stderr

    pyproject.write_text(pyproject.read_text().replace('version = "1.0.0"', 'version = "9.9.9"'))
    environment["UV_LOCKED"] = "1"
    attempted = subprocess.run(
        [uv, "--offline", "--directory", str(project), "sync", "--dry-run"],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert attempted.returncode != 0
    assert "lock" in attempted.stderr.lower()


@pytest.mark.parametrize("fork", [True, False], ids=["immutable-fork-base", "reviewed-same-repository"])
def test_agents_constraints_pin_only_unique_reviewed_agents_only_packages(tmp_path: Path, fork: bool) -> None:
    result = _execute(tmp_path, "reviewed", fork=fork, constraints=True)
    assert result.returncode == 0, result.stdout + result.stderr
    pins = set((tmp_path / "reviewed-constraints.txt").read_text().splitlines())
    assert "pynput==1.6.8" in pins
    assert "playwright==1.0.0" in pins
    assert "httpx==0.28.1" not in pins
    assert "httpx==0.29.0" not in pins
    assert not any(pin.startswith("multi-version==") for pin in pins)
    assert not any(pin.startswith("openai==") or pin.startswith("openai-agents==") for pin in pins)
    assert "sdk-only-lib==1.0.0" not in pins


@pytest.mark.parametrize("fork", [True, False], ids=["immutable-fork-base", "reviewed-same-repository"])
def test_submitted_fork_lock_cannot_remove_reviewed_agents_constraint(tmp_path: Path, fork: bool) -> None:
    result = _execute(tmp_path, "fork-submitted-pynput", fork=fork, constraints=True)
    assert result.returncode == 0, result.stdout + result.stderr
    pins = set((tmp_path / "reviewed-constraints.txt").read_text().splitlines())
    assert ("pynput==1.6.8" in pins) == fork


def test_reviewed_constraints_apply_only_to_existing_no_sync_link_step() -> None:
    workflow = WORKFLOW.read_text()
    generator = workflow.index("      - name: Constrain Agents-only packages to reviewed locked versions\n")
    link = workflow.index("      - name: Link to local SDK\n", generator)
    validator = workflow.index("      - name: Verify relinked Agents lock package provenance\n", link)
    install = workflow.index("      - name: Install dependencies\n", validator)
    link_step = workflow[link:validator]
    assert generator < link < validator < install
    assert "          UV_CONSTRAINT: " in link_step
    assert "steps.reviewed_agents_constraints.outputs.path" in link_step
    assert "        run: uv add --no-sync ../openai-python\n" in link_step
    assert "UV_CONSTRAINT:" not in workflow[validator:]
    assert "mktemp" in workflow[generator:link]
    assert "GITHUB_OUTPUT" in workflow[generator:link]


def test_uv_constraint_prevents_unreviewed_agents_only_upgrade_before_relink(tmp_path: Path) -> None:
    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("uv is unavailable")

    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "pyproject.toml").write_text(
        '[project]\nname = "pynput"\nversion = "1.8.2"\nrequires-python = ">=3.10"\ndependencies = []\n'
    )
    vulnerable = tmp_path / "vulnerable"
    protected = tmp_path / "protected"
    for project in (vulnerable, protected):
        project.mkdir()
        (project / "pyproject.toml").write_text(
            '[project]\nname = "reviewed-agents"\nversion = "1.0.0"\nrequires-python = ">=3.10"\ndependencies = []\n'
        )

    environment = dict(os.environ)
    environment.pop("UV_CONSTRAINT", None)
    environment["UV_CACHE_DIR"] = str(tmp_path / "cache")
    environment["UV_PYTHON_DOWNLOADS"] = "never"
    unconstrained = subprocess.run(
        [uv, "--offline", "--directory", str(vulnerable), "add", "--no-sync", "../candidate"],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert unconstrained.returncode == 0, unconstrained.stdout + unconstrained.stderr
    assert 'version = "1.8.2"' in (vulnerable / "uv.lock").read_text()

    constraints = tmp_path / "reviewed-constraints.txt"
    constraints.write_text("pynput==1.6.8\n")
    environment["UV_CONSTRAINT"] = str(constraints)
    constrained = subprocess.run(
        [uv, "--offline", "--directory", str(protected), "add", "--no-sync", "../candidate"],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert constrained.returncode != 0
    assert "pynput" in constrained.stderr
