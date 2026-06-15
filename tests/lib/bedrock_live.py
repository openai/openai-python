"""Opt-in live test for the Amazon Bedrock provider.

This file is intentionally named ``bedrock_live.py`` so the standard pytest
suite does not collect it. Run it explicitly with:

    rye run pytest -q -s tests/lib/bedrock_live.py

The test loads ``.env`` from the repository root when it exists. Set
``BEDROCK_LIVE_ENV_FILE`` to load a different file. Existing environment
variables take precedence over values from the file.

Useful environment variables:

- ``BEDROCK_LIVE_MODEL`` (defaults to ``openai.gpt-5.4``)
- ``BEDROCK_LIVE_REGION`` (otherwise uses the normal AWS region chain)
- ``BEDROCK_LIVE_PROFILE`` (otherwise uses the normal AWS credential chain)
- ``AWS_BEDROCK_BASE_URL`` (optional endpoint override)

The normal AWS environment variables, shared config, credential-process, SSO,
and workload credential sources are resolved by botocore. The test explicitly
disables the ``AWS_BEARER_TOKEN_BEDROCK`` fallback so a passing run proves that
AWS credentials and SigV4 signing worked.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from openai import OpenAI
from openai.providers import bedrock

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _load_env_file() -> None:
    configured_path = os.environ.get("BEDROCK_LIVE_ENV_FILE")
    path = Path(configured_path).expanduser() if configured_path else _REPOSITORY_ROOT / ".env"
    if not path.exists():
        if configured_path:
            raise RuntimeError(f"BEDROCK_LIVE_ENV_FILE does not exist: {path}")
        return

    for line_number, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").lstrip()

        name, separator, raw_value = line.partition("=")
        name = name.strip()
        if not separator or _ENV_NAME.fullmatch(name) is None:
            raise RuntimeError(f"Invalid environment assignment at {path}:{line_number}")

        value = raw_value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()

        os.environ.setdefault(name, value)


_load_env_file()


def test_bedrock_live_response() -> None:
    model = os.environ.get("BEDROCK_LIVE_MODEL") or "openai.gpt-5.4"
    region = os.environ.get("BEDROCK_LIVE_REGION") or None
    profile = os.environ.get("BEDROCK_LIVE_PROFILE") or None

    with OpenAI(
        provider=bedrock(
            region=region,
            profile=profile,
            api_key=None,
        ),
        timeout=60,
        max_retries=2,
    ) as client:
        response = client.responses.create(
            model=model,
            input="Reply with exactly: bedrock live test ok",
            max_output_tokens=64,
        )

    output_text = response.output_text.strip()
    assert output_text, f"Bedrock returned no output text for response {response.id}"
    assert "bedrock live test ok" in output_text.lower()
    print(f"Bedrock live response {response.id}: {output_text}")
