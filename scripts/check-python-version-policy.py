from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED = ("3.10", "3.11", "3.12", "3.13", "3.14")
MINIMUM = SUPPORTED[0]
CURRENT_STABLE = SUPPORTED[-1]
PRERELEASE = "3.15"
UNMARKED_DEPENDENCIES = (
    "aiohttp>=3.14.1",
    "httpx2>=2.7.0, <3",
    "anyio>=4.10.0, <5",
    "botocore>=1.40.0,<2",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def workflow_job(workflow: str, name: str) -> str:
    match = re.search(
        rf"^  {re.escape(name)}:\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
        workflow,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise RuntimeError(f"CI does not define the {name!r} job")
    return match.group("body")


def matrix_body(job: str) -> str:
    match = re.search(
        r"^      matrix:\n(?P<body>.*?)(?=^    [A-Za-z0-9_-]+:\n|\Z)",
        job,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise RuntimeError("CI job does not define a strategy matrix")
    return match.group("body")


def matrix_versions(job: str) -> tuple[str, ...]:
    versions: list[str] = []
    for line in matrix_body(job).splitlines():
        if re.match(r"^\s+(?:-\s+)?python-version:", line):
            versions.extend(re.findall(r'"(3\.\d+)"', line))
    return tuple(versions)


def compatibility_matrix(job: str) -> tuple[tuple[str, bool], ...]:
    rows = re.findall(
        r'^ +-\s+python-version: "(3\.\d+)"\n +experimental: (true|false)$',
        matrix_body(job),
        re.MULTILINE,
    )
    return tuple((version, experimental == "true") for version, experimental in rows)


def main() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text()
    readme = (ROOT / "README.md").read_text()
    contributing = (ROOT / "CONTRIBUTING.md").read_text()
    policy = (ROOT / "PYTHON_VERSION_POLICY.md").read_text()
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()
    uv_lock = (ROOT / "uv.lock").read_text()
    realtime_example = (ROOT / "examples/realtime/push_to_talk_app.py").read_text()
    python_version = (ROOT / ".python-version").read_text().strip()

    requires_python = re.findall(r'^requires-python = "([^"]+)"$', pyproject, re.MULTILINE)
    require(requires_python == [f">= {MINIMUM}"], f"Unexpected requires-python values: {requires_python}")

    uv_metadata = uv_lock.split("[[package]]", 1)[0]
    uv_requires_python = re.findall(r'^requires-python = "([^"]+)"$', uv_metadata, re.MULTILINE)
    require(
        uv_requires_python == [f">={MINIMUM}"],
        f"uv.lock requires-python is {uv_requires_python}, expected >={MINIMUM}",
    )

    classifiers = re.findall(r'"Programming Language :: Python :: (3\.\d+)"', pyproject)
    require(tuple(classifiers) == SUPPORTED, f"Unexpected Python classifiers: {classifiers}")

    require(f'pythonVersion = "{MINIMUM}"' in pyproject, "Pyright does not target the minimum Python")
    require(f'target-version = "py{MINIMUM.replace(".", "")}"' in pyproject, "Ruff does not target the minimum Python")
    require(python_version.startswith(f"{MINIMUM}."), f".python-version is not on Python {MINIMUM}: {python_version}")
    require(f"Python {MINIMUM}+" in readme, "README introduction does not state the minimum Python")
    require(f"Python {MINIMUM} or higher." in readme, "README requirements do not state the minimum Python")
    require("PYTHON_VERSION_POLICY.md" in contributing, "CONTRIBUTING does not link the Python policy")
    require(
        f'# requires-python = ">={MINIMUM}"' in realtime_example,
        "Realtime example metadata does not state the minimum Python",
    )

    pr_versions = matrix_versions(workflow_job(workflow, "test"))
    expected_pr_versions = (MINIMUM, CURRENT_STABLE)
    require(
        pr_versions == expected_pr_versions,
        f"PR test matrix is {pr_versions}, expected {expected_pr_versions}",
    )

    compatibility_job = workflow_job(workflow, "compatibility")
    require(
        "continue-on-error: ${{ matrix.experimental }}" in compatibility_job,
        "Scheduled compatibility failures are not controlled by matrix.experimental",
    )
    require(
        "allow-prereleases: ${{ matrix.experimental }}" in compatibility_job,
        "Scheduled compatibility prerelease setup is not controlled by matrix.experimental",
    )
    compatibility = compatibility_matrix(compatibility_job)
    expected_compatibility = tuple((version, False) for version in SUPPORTED) + ((PRERELEASE, True),)
    require(
        compatibility == expected_compatibility,
        f"Scheduled compatibility matrix is {compatibility}, expected {expected_compatibility}",
    )
    require(
        f"Python {MINIMUM} through\n{CURRENT_STABLE}" in policy,
        "Policy current-compatibility text does not match the supported matrix",
    )

    project_metadata = pyproject.split("[tool.rye]", 1)[0]
    for requirement in UNMARKED_DEPENDENCIES:
        require(
            f'"{requirement}"' in project_metadata,
            f"Package metadata does not contain the unmarked requirement {requirement!r}",
        )
        require(
            re.search(rf'"{re.escape(requirement)};\s*python_version\b', project_metadata) is None,
            f"Package metadata still contains a Python marker for {requirement!r}",
        )

    print(
        f"Python policy is synchronized: minimum {MINIMUM}, "
        f"supported {SUPPORTED[0]}-{SUPPORTED[-1]}, prerelease {PRERELEASE}"
    )


if __name__ == "__main__":
    main()
