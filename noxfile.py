import nox


@nox.session(reuse_venv=True, name="test-pydantic-v1")
def test_pydantic_v1(session: nox.Session) -> None:
    session.install("-r", "requirements-dev.lock")
    session.install("pydantic<2")

    session.run("pytest", "--showlocals", "--ignore=tests/functional", *session.posargs)


# httpx2 is a Python 3.10+ optional extra and is absent from the 3.9-floored dev lock,
# so its tests are skipped by the default session. This session installs a real httpx2
# on a supported interpreter and runs the httpx2 suite so the widened exception tuples,
# timeout handling and URL coercion are actually exercised in CI.
#
# We install the package (with the httpx2 extra) plus the test tooling unpinned rather
# than `requirements-dev.lock`: that lock is resolved at the 3.9 floor and some pins
# (e.g. backports-asyncio-runner) refuse to install on Python 3.12+.
@nox.session(python=["3.10", "3.11", "3.12", "3.13", "3.14"], name="test-httpx2")
def test_httpx2(session: nox.Session) -> None:
    session.install("-e", ".[httpx2]")
    session.install("pytest", "pytest-asyncio", "pytest-xdist")

    session.run(
        "pytest",
        "tests/test_httpx2_client.py",
        "tests/test_httpx2_not_installed.py",
        *session.posargs,
    )
