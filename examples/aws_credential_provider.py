"""Example: Using AwsOpenAI with a custom credential provider and auto-refresh.

This shows how to:
  1. Use a custom credential provider that returns fresh credentials on each call
  2. Use botocore's RefreshableCredentials for automatic STS assume-role refresh
  3. Use an async credential provider with AsyncAwsOpenAI

Requires:
  - botocore installed (pip install botocore)
  - boto3 installed (pip install boto3) — for the STS assume-role example
  - AWS credentials configured for the initial session
  - AWS_REGION or AWS_DEFAULT_REGION set (or pass region= explicitly)

Run:
  export AWS_REGION=us-west-2
  PYTHONPATH=src python3 examples/bedrock_mantle_credential_provider.py
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable
from dataclasses import dataclass

from openai.lib.aws import AwsOpenAI, AsyncAwsOpenAI

# ---------------------------------------------------------------------------
# 1. Simple custom credential provider
# ---------------------------------------------------------------------------


@dataclass
class MyCredentials:
    """Minimal object satisfying the Credentials protocol."""

    access_key: str
    secret_key: str
    token: str | None = None


def my_credential_provider() -> MyCredentials:
    """Return credentials from your own secret store, vault, etc.

    This callable is invoked before every request, so returning fresh
    credentials here is all you need for auto-refresh.
    """
    # Replace with your actual credential fetching logic
    return MyCredentials(
        access_key="AKIA...",
        secret_key="wJalr...",
        token="FwoGZX...",  # optional session token
    )


client = AwsOpenAI(
    region="us-west-2",
    credential_provider=my_credential_provider,
)

response = client.chat.completions.create(
    model="openai.gpt-oss-120b",
    messages=[{"role": "user", "content": "Hello from custom credentials!"}],
)
print("Custom provider:", response.choices[0].message.content)


# ---------------------------------------------------------------------------
# 2. Auto-refreshing STS assume-role credentials via botocore
# ---------------------------------------------------------------------------


def make_sts_credential_provider(role_arn: str, session_name: str = "bedrock-mantle") -> Callable[[], Any]:
    """Create a credential provider that assumes an IAM role and auto-refreshes.

    botocore's RefreshableCredentials handles expiry checks and refresh
    transparently — accessing .access_key / .secret_key / .token on the
    returned object triggers a refresh if the credentials are expired.
    """
    import botocore.session  # type: ignore[import-untyped, import-not-found]
    import botocore.credentials  # type: ignore[import-untyped, import-not-found]

    session: Any = botocore.session.get_session()  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    sts: Any = session.create_client("sts")  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]

    def fetch_credentials() -> dict[str, Any]:
        resp: Any = sts.assume_role(RoleArn=role_arn, RoleSessionName=session_name)["Credentials"]  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        return {
            "access_key": resp["AccessKeyId"],
            "secret_key": resp["SecretAccessKey"],
            "token": resp["SessionToken"],
            "expiry_time": resp["Expiration"].isoformat(),  # pyright: ignore[reportUnknownMemberType]
        }

    refreshable: Any = botocore.credentials.RefreshableCredentials.create_from_metadata(  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        metadata=fetch_credentials(),
        refresh_using=fetch_credentials,
        method="sts-assume-role",
    )

    # Return a provider that gives back the refreshable object.
    # Accessing its attributes auto-refreshes when expired.
    def provider() -> Any:
        return refreshable  # pyright: ignore[reportUnknownVariableType]

    return provider


# Uncomment to use:
# sts_client = AwsOpenAI(
#     region="us-west-2",
#     credential_provider=make_sts_credential_provider("arn:aws:iam::123456789012:role/MyRole"),
# )


# ---------------------------------------------------------------------------
# 3. Async credential provider
# ---------------------------------------------------------------------------


async def async_credential_provider() -> MyCredentials:
    """An async provider — useful when credentials come from an async API."""
    # Simulate async credential fetch (e.g., from an async HTTP vault client)
    await asyncio.sleep(0)
    return MyCredentials(
        access_key="AKIA...",
        secret_key="wJalr...",
        token="FwoGZX...",
    )


async def main() -> None:
    async_client = AsyncAwsOpenAI(
        region="us-west-2",
        credential_provider=async_credential_provider,
    )

    response = await async_client.chat.completions.create(
        model="openai.gpt-oss-120b",
        messages=[{"role": "user", "content": "Hello from async credentials!"}],
    )
    print("Async provider:", response.choices[0].message.content)


asyncio.run(main())
