"""Explicitly opt-in live coverage for Amazon Bedrock Mantle and Runtime.

BEDROCK_LIVE_TEST=1 BEDROCK_LIVE_ENDPOINT=runtime AWS_REGION=us-west-2 \
    uv run --locked --all-extras pytest -q -s tests/lib/bedrock_live.py

Runtime defaults to the three US GPT-5.6 inference profiles. Override them with
``BEDROCK_LIVE_MODEL`` or comma-separated ``BEDROCK_LIVE_MODELS``. Select one
authentication mode with ``BEDROCK_LIVE_AUTH`` or several with comma-separated
``BEDROCK_LIVE_AUTHS``. Supported modes are ``bearer``, ``environment-bearer``,
``token-provider``, ``default-chain``, ``profile``, and ``static``.

Set ``BEDROCK_LIVE_STREAM=1`` to exercise streaming and
``BEDROCK_LIVE_RESPONSES=1`` to include Runtime Responses. Mantle retains its
existing Responses test and requires an explicit ``AWS_BEDROCK_BASE_URL``.
"""

from __future__ import annotations

import os
import re
from typing import Literal, cast
from pathlib import Path

from openai import OpenAI
from openai._provider import _Provider
from openai.providers import bedrock

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_RUNTIME_MODELS = (
    "us.openai.gpt-5.6-sol",
    "us.openai.gpt-5.6-terra",
    "us.openai.gpt-5.6-luna",
)
_AUTH_MODES = {"bearer", "environment-bearer", "token-provider", "default-chain", "profile", "static"}


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


def _required_environment(name: str) -> str:
    value = os.environ.get(name)
    if value is None or not value.strip():
        raise RuntimeError(f"Set {name} before running the Bedrock live test.")
    return value.strip()


def _live_provider(
    *, endpoint: Literal["mantle", "runtime"], authentication: str, region: str | None, base_url: str | None
) -> _Provider:
    profile = os.environ.get("BEDROCK_LIVE_PROFILE") or os.environ.get("AWS_PROFILE") or None
    if authentication == "bearer":
        return bedrock(
            endpoint=endpoint,
            region=region,
            base_url=base_url,
            api_key=_required_environment("AWS_BEARER_TOKEN_BEDROCK"),
        )
    if authentication == "environment-bearer":
        _required_environment("AWS_BEARER_TOKEN_BEDROCK")
        return bedrock(endpoint=endpoint, region=region, base_url=base_url)
    if authentication == "token-provider":
        return bedrock(
            endpoint=endpoint,
            region=region,
            base_url=base_url,
            token_provider=lambda: _required_environment("AWS_BEARER_TOKEN_BEDROCK"),
        )
    if authentication == "profile":
        if profile is None:
            raise RuntimeError("Set BEDROCK_LIVE_PROFILE or AWS_PROFILE before testing profile authentication.")
        return bedrock(endpoint=endpoint, region=region, base_url=base_url, profile=profile, api_key=None)
    if authentication == "static":
        return bedrock(
            endpoint=endpoint,
            region=region,
            base_url=base_url,
            access_key_id=_required_environment("AWS_ACCESS_KEY_ID"),
            secret_access_key=_required_environment("AWS_SECRET_ACCESS_KEY"),
            session_token=os.environ.get("AWS_SESSION_TOKEN") or None,
        )
    return bedrock(endpoint=endpoint, region=region, base_url=base_url, profile=profile, api_key=None)


def test_bedrock_live_response() -> None:
    if os.environ.get("BEDROCK_LIVE_TEST") != "1":
        raise RuntimeError("Refusing live AWS requests. Set BEDROCK_LIVE_TEST=1 to run this test.")

    configured_endpoint = os.environ.get("BEDROCK_LIVE_ENDPOINT", "mantle")
    if configured_endpoint not in {"mantle", "runtime"}:
        raise RuntimeError("BEDROCK_LIVE_ENDPOINT must be 'mantle' or 'runtime'.")
    endpoint = cast("Literal['mantle', 'runtime']", configured_endpoint)
    region = os.environ.get("BEDROCK_LIVE_REGION") or None
    base_url = os.environ.get("AWS_BEDROCK_BASE_URL") or None
    if endpoint == "mantle" and base_url is None:
        raise RuntimeError(
            "Set AWS_BEDROCK_BASE_URL to the Bedrock GPT-OSS endpoint, for example "
            "https://bedrock-mantle.us-west-2.api.aws/v1."
        )

    configured_models = os.environ.get("BEDROCK_LIVE_MODELS") or os.environ.get("BEDROCK_LIVE_MODEL")
    models = (
        tuple(model.strip() for model in configured_models.split(",") if model.strip())
        if configured_models
        else _RUNTIME_MODELS
        if endpoint == "runtime"
        else ("openai.gpt-oss-120b",)
    )
    if not models:
        raise RuntimeError("Set at least one Bedrock model or inference-profile ID.")
    configured_auth = os.environ.get("BEDROCK_LIVE_AUTHS") or os.environ.get("BEDROCK_LIVE_AUTH", "default-chain")
    authentication_modes = tuple(mode.strip() for mode in configured_auth.split(",") if mode.strip())
    invalid_modes = set(authentication_modes) - _AUTH_MODES
    if not authentication_modes or invalid_modes:
        raise RuntimeError(f"Unsupported Bedrock live authentication mode(s): {', '.join(sorted(invalid_modes))}.")

    stream = os.environ.get("BEDROCK_LIVE_STREAM") == "1"
    run_responses = endpoint == "mantle" or os.environ.get("BEDROCK_LIVE_RESPONSES") == "1"
    for authentication in authentication_modes:
        provider = _live_provider(endpoint=endpoint, authentication=authentication, region=region, base_url=base_url)
        with OpenAI(provider=provider, timeout=60, max_retries=2) as client:
            for model in models:
                if endpoint == "runtime":
                    completion = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": "Reply with exactly: bedrock live test ok"}],
                    )
                    assert completion.choices[0].message.content
                    assert completion.choices[0].finish_reason
                    assert completion.usage is not None
                    print(f"Bedrock Runtime {authentication} chat {completion.id}: {model}")

                    if stream:
                        chat_stream = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": "Reply with exactly: bedrock live test ok"}],
                            stream=True,
                        )
                        chunks = list(chat_stream)
                        assert chunks and any(chunk.choices[0].delta.content for chunk in chunks if chunk.choices)
                        assert any(chunk.choices[0].finish_reason for chunk in chunks if chunk.choices)

                if run_responses:
                    response = client.responses.create(
                        model=model, input="Reply with exactly: bedrock live test ok", store=False
                    )
                    assert response.output_text.strip(), f"Bedrock returned no output text for response {response.id}"
                    print(f"Bedrock {endpoint} {authentication} response {response.id}: {model}")

                    if stream:
                        events = list(
                            client.responses.create(
                                model=model, input="Reply with exactly: bedrock live test ok", store=False, stream=True
                            )
                        )
                        assert events and events[-1].type == "response.completed"
