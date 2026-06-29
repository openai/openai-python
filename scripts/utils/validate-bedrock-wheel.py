from __future__ import annotations

import os
import sys
import email
import zipfile
import tempfile
import subprocess
from pathlib import Path

_SMOKE_TEST = r"""
import os
import sys
import importlib.abc
from pathlib import Path

import httpx


class BlockBotocore(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "botocore" or fullname.startswith("botocore."):
            raise ImportError(f"unexpected AWS import: {fullname}")
        return None


wheel_root = Path(os.environ["OPENAI_WHEEL_ROOT"]).resolve()
blocker = BlockBotocore()
sys.meta_path.insert(0, blocker)

import openai
from openai import OpenAI
from openai.providers import bedrock

assert Path(openai.__file__).resolve().is_relative_to(wheel_root), openai.__file__

requests = []


def handler(request):
    requests.append(request)
    return httpx.Response(200, request=request, json={})


http_client = httpx.Client(transport=httpx.MockTransport(handler), trust_env=False)
with OpenAI(
    provider=bedrock(region="us-east-1", api_key="bearer-token"),
    http_client=http_client,
) as client:
    client.get("/models", cast_to=httpx.Response)

assert requests[0].headers["Authorization"] == "Bearer bearer-token"
assert not any(name == "botocore" or name.startswith("botocore.") for name in sys.modules)

sys.meta_path.remove(blocker)
requests.clear()
http_client = httpx.Client(transport=httpx.MockTransport(handler), trust_env=False)
with OpenAI(
    provider=bedrock(
        region="us-east-1",
        access_key_id="fixture-access-key",
        secret_access_key="fixture-secret-key",
        session_token="fixture-session-token",
    ),
    http_client=http_client,
) as client:
    client.get("/models", cast_to=httpx.Response)

assert "Credential=fixture-access-key/" in requests[0].headers["Authorization"]
assert requests[0].headers["X-Amz-Security-Token"] == "fixture-session-token"
"""


def main() -> None:
    wheels = list(Path("dist").glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"Expected exactly one wheel in dist/, found: {wheels}")

    wheel = wheels[0]
    with tempfile.TemporaryDirectory() as directory:
        wheel_root = Path(directory)
        with zipfile.ZipFile(wheel) as archive:
            metadata_names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
            if len(metadata_names) != 1:
                raise RuntimeError(f"Expected exactly one METADATA file in {wheel}, found: {metadata_names}")

            metadata = email.message_from_bytes(archive.read(metadata_names[0]))
            archive.extractall(wheel_root)

        requirements = metadata.get_all("Requires-Dist", [])
        botocore_requirements = [requirement for requirement in requirements if requirement.startswith("botocore")]
        if len(botocore_requirements) != 2:
            raise RuntimeError(f"Expected two Python-version-specific botocore requirements: {botocore_requirements}")
        if any("[crt]" in requirement for requirement in botocore_requirements):
            raise RuntimeError(
                f"The Bedrock extra must not install the unused botocore CRT extra: {botocore_requirements}"
            )
        if not all("extra == 'bedrock'" in requirement for requirement in botocore_requirements):
            raise RuntimeError(f"Botocore requirements must belong to the Bedrock extra: {botocore_requirements}")

        environment = os.environ.copy()
        for name in (
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
            "AWS_PROFILE",
            "AWS_REGION",
            "AWS_DEFAULT_REGION",
            "AWS_BEARER_TOKEN_BEDROCK",
            "AWS_BEDROCK_BASE_URL",
            "OPENAI_API_KEY",
            "OPENAI_ORG_ID",
            "OPENAI_PROJECT_ID",
            "OPENAI_CUSTOM_HEADERS",
        ):
            environment.pop(name, None)
        environment["OPENAI_WHEEL_ROOT"] = str(wheel_root)
        environment["PYTHONPATH"] = str(wheel_root)
        subprocess.run([sys.executable, "-c", _SMOKE_TEST], cwd=wheel_root, env=environment, check=True)


if __name__ == "__main__":
    main()
