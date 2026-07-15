"""
Use the OpenAI Python client against DaoXE, a multi-model multi-protocol API gateway.

Chat Completions base URL: https://daoxe.com/v1
Use an exact model ID from your DaoXE account catalog (GET /v1/models).
Not available in mainland China.

DaoXE also exposes OpenAI Responses and Anthropic Messages for other clients;
this example uses Chat Completions.
"""

from __future__ import annotations

import os

from openai import OpenAI

# Prefer DaoXE-specific env vars; fall back to the standard OpenAI client env vars.
api_key = os.environ.get("DAOXE_API_KEY") or os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise SystemExit(
        "Set DAOXE_API_KEY (or OPENAI_API_KEY) before running this example."
    )

client = OpenAI(
    base_url=os.environ.get("DAOXE_BASE_URL")
    or os.environ.get("OPENAI_BASE_URL")
    or "https://daoxe.com/v1",
    api_key=api_key,
)

completion = client.chat.completions.create(
    model=os.environ.get("DAOXE_MODEL")
    or os.environ.get("OPENAI_MODEL")
    or "YOUR_DAOXE_MODEL_ID",
    messages=[
        {
            "role": "user",
            "content": "Reply with OK",
        },
    ],
    max_tokens=16,
)

print(completion.choices[0].message.content)
