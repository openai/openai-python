import nox


@nox.session(reuse_venv=True, name="test-pydantic-v1")
def test_pydantic_v1(session: nox.Session) -> None:
    # Exported from uv.lock to keep this nox compatibility path stable for now.
    session.install("-r", "requirements-dev.lock")
    session.install("pydantic<2")

    session.run("pytest", "--showlocals", "--ignore=tests/functional", *session.posargs)
