"""Run Amazon Bedrock Runtime Chat Completions with bearer or AWS authentication.

AWS_REGION=us-west-2 python examples/bedrock_runtime.py
AWS_REGION=us-west-2 BEDROCK_MODEL=us.openai.gpt-5.6-terra BEDROCK_STREAM=1 python examples/bedrock_runtime.py
AWS_REGION=us-west-2 BEDROCK_AUTH=bearer python examples/bedrock_runtime.py
"""

from __future__ import annotations

import os

from openai import OpenAI
from openai.providers import bedrock
from openai.types.chat import ChatCompletionMessageParam

authentication = os.environ.get("BEDROCK_AUTH", "sigv4")
region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
profile = os.environ.get("AWS_PROFILE") or None

if authentication == "bearer":
    token = os.environ.get("AWS_BEARER_TOKEN_BEDROCK")
    if not token:
        raise RuntimeError("Bearer authentication requires AWS_BEARER_TOKEN_BEDROCK.")
    provider = bedrock(endpoint="runtime", region=region, api_key=token)
elif authentication == "sigv4":
    provider = bedrock(endpoint="runtime", region=region, profile=profile, api_key=None)
else:
    raise RuntimeError("BEDROCK_AUTH must be either 'sigv4' or 'bearer'.")

client = OpenAI(provider=provider)
model = os.environ.get("BEDROCK_MODEL", "us.openai.gpt-5.6-sol")
messages: list[ChatCompletionMessageParam] = [{"role": "user", "content": "Say hello from Amazon Bedrock Runtime!"}]

if os.environ.get("BEDROCK_STREAM") == "1":
    stream = client.chat.completions.create(model=model, messages=messages, stream=True)
    for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
    print()
else:
    completion = client.chat.completions.create(model=model, messages=messages)
    print(completion.choices[0].message.content)
