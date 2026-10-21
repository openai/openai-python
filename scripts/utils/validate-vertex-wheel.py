from __future__ import annotations

import os
import sys
import tempfile
import subprocess
from pathlib import Path
from collections.abc import Callable


def check_installed(with_vertex: bool) -> None:
    from typing import get_type_hints
    from importlib import metadata
    from unittest.mock import patch

    import httpx2

    import openai
    from openai.providers import vertex

    assert Path(openai.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()), openai.__file__
    assert "credentials" in get_type_hints(vertex)

    def handle(request: httpx2.Request) -> httpx2.Response:
        assert request.headers["authorization"] == "Bearer fixture-token"
        return httpx2.Response(200, json={"id": "resp_fixture", "object": "response", "output": []})

    def send(token_provider: Callable[[], str] | None = None) -> None:
        with openai.OpenAI(
            provider=vertex(base_url="https://vertex.example/v1", token_provider=token_provider),
            http_client=httpx2.Client(transport=httpx2.MockTransport(handle), trust_env=False),
        ) as client:
            client.responses.create(model="fixture", input="hello")

    if with_vertex:
        from google.oauth2.credentials import Credentials

        create_credentials: Callable[[str], object] = Credentials
        with patch("google.auth.default", return_value=(create_credentials("fixture-token"), "fixture-project")):
            send()
    else:
        try:
            metadata.version("google-auth")
        except metadata.PackageNotFoundError:
            pass
        else:
            raise AssertionError("The base wheel installed google-auth")

        send(lambda: "fixture-token")
        try:
            send()
        except openai.OpenAIError as error:
            assert str(error) == "Install openai[vertex] to use Google credentials, or supply token_provider."
        else:
            raise AssertionError("Vertex ADC should require the vertex extra")


def main() -> None:
    wheels = list(Path("dist").glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"Expected exactly one wheel in dist/, found: {wheels}")

    wheel = wheels[0].resolve()
    install_env = os.environ.copy()
    # CI builds openai from source by default; this check must install the wheel it just built.
    install_env.pop("UV_NO_BINARY_PACKAGE", None)
    with tempfile.TemporaryDirectory() as directory:
        venv = Path(directory) / "venv"
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(["uv", "venv", "--python", sys.executable, str(venv)], check=True)
        for requirement, mode in ((str(wheel), "--plain"), (f"{wheel}[vertex]", "--vertex")):
            subprocess.run(["uv", "pip", "install", "--python", str(python), requirement], env=install_env, check=True)
            subprocess.run([str(python), "-I", str(Path(__file__).resolve()), mode], cwd=directory, check=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["--plain"]:
        check_installed(with_vertex=False)
    elif sys.argv[1:] == ["--vertex"]:
        check_installed(with_vertex=True)
    elif len(sys.argv) == 1:
        main()
    else:
        raise SystemExit("usage: validate-vertex-wheel.py [--plain | --vertex]")
