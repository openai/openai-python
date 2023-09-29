import nox
import nox_poetry


@nox_poetry.session(reuse_venv=True, name="test-pydantic-v1")
def test_pydantic_v1(session: nox.Session) -> None:
    session.run_always("poetry", "install", external=True)

    # https://github.com/cjolowicz/nox-poetry/issues/1116
    session._session.run("python", "-m", "pip", "install", "pydantic<2", external=True)  # type: ignore

    session.run("pytest", "--showlocals", "--ignore=tests/functional")
