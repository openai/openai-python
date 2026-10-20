from pathlib import Path

import nox


@nox.session(reuse_venv=True, name="test-pydantic-v1")
def test_pydantic_v1(session: nox.Session) -> None:
    # The CI bridge resolves a runtime-specific lock outside the source distribution.
    requirements = Path(".venv/requirements-dev.lock")
    if not requirements.is_file():
        requirements = Path("requirements-dev.lock")
    session.install("-r", str(requirements))
    session.install("pydantic<2")

    session.run("pytest", "--showlocals", "--ignore=tests/functional", *session.posargs)
