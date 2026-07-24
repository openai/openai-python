from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MINIMUM = "3.10"
CURRENT_STABLE = "3.14"
SUPPORTED = ("3.10", "3.11", "3.12", "3.13", "3.14")
PRERELEASE = "3.15"


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


def matrix_versions(job: str) -> tuple[str, ...]:
    versions: list[str] = []
    for match in re.finditer(
        r'^\s+(?:-\s+)?python-version:\s*(?:"(?P<single>3\.\d+)"|\[(?P<inline>[^\]]+)\])\s*$',
        job,
        re.MULTILINE,
    ):
        if single := match.group("single"):
            versions.append(single)
        else:
            inline = match.group("inline")
            if inline is None:
                raise RuntimeError("Malformed Python version matrix")
            versions.extend(re.findall(r'"(3\.\d+)"', inline))
    return tuple(versions)


def main() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text()
    readme = (ROOT / "README.md").read_text()
    contributing = (ROOT / "CONTRIBUTING.md").read_text()
    policy = (ROOT / "PYTHON_VERSION_POLICY.md").read_text()
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()
    realtime_example = (ROOT / "examples/realtime/push_to_talk_app.py").read_text()
    python_version = (ROOT / ".python-version").read_text().strip()

    requires_python = re.findall(r'^requires-python = "([^"]+)"$', pyproject, re.MULTILINE)
    require(requires_python == [f">= {MINIMUM}"], f"Unexpected requires-python values: {requires_python}")

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

    compatibility_versions = matrix_versions(workflow_job(workflow, "compatibility"))
    expected_compatibility_versions = SUPPORTED + (PRERELEASE,)
    require(
        compatibility_versions == expected_compatibility_versions,
        "Scheduled compatibility matrix is "
        f"{compatibility_versions}, expected {expected_compatibility_versions}",
    )
    require(
        f"Python {MINIMUM} through\n{CURRENT_STABLE}" in policy,
        "Policy current-compatibility text does not match the supported matrix",
    )

    project_metadata = pyproject.split("[tool.rye]", 1)[0]
    require("python_version" not in project_metadata, "Package metadata contains a redundant Python-version marker")
    require('"botocore>=1.40.0,<2"' in project_metadata, "Bedrock does not use the supported Botocore range")

    print(
        f"Python policy is synchronized: minimum {MINIMUM}, "
        f"supported {SUPPORTED[0]}-{SUPPORTED[-1]}, prerelease {PRERELEASE}"
    )


if __name__ == "__main__":
    main()
