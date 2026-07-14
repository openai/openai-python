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

client = OpenAI(
    # Or set OPENAI_BASE_URL / OPENAI_API_KEY
    base_url=os.environ.get("DAOXE_BASE_URL", "https://daoxe.com/v1"),
    api_key=os.environ["DAOXE_API_KEY"],
)

completion = client.chat.completions.create(
    model=os.environ.get("DAOXE_MODEL", "YOUR_DAOXE_MODEL_ID"),
    messages=[
        {
            "role": "user",
            "content": "Reply with OK",
        },
    ],
    max_tokens=16,
)

print(completion.choices[0].message.content)
