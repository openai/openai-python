from __future__ import annotations

import os
import ssl
import asyncio

from openai import AsyncOpenAI, DefaultAsyncHttpx2Client
from openai.auth import x509_workload_identity


def create_client() -> AsyncOpenAI:
    mode = os.getenv("OPENAI_AUTH_MODE", "api_key")
    if mode == "api_key":
        return AsyncOpenAI()
    if mode != "x509":
        raise ValueError("OPENAI_AUTH_MODE must be 'api_key' or 'x509'")

    tls_context = ssl.create_default_context(cafile=os.getenv("OPENAI_MTLS_CA_BUNDLE"))
    tls_context.load_cert_chain(
        certfile=os.environ["OPENAI_MTLS_CERTIFICATE_CHAIN"],
        keyfile=os.environ["OPENAI_MTLS_PRIVATE_KEY"],
        password=os.getenv("OPENAI_MTLS_PRIVATE_KEY_PASSWORD"),
    )

    return AsyncOpenAI(
        workload_identity=x509_workload_identity(
            identity_provider_id=os.environ["OPENAI_IDENTITY_PROVIDER_ID"],
            service_account_id=os.environ["OPENAI_SERVICE_ACCOUNT_ID"],
        ),
        base_url=os.getenv("OPENAI_BASE_URL"),
        http_client=DefaultAsyncHttpx2Client(verify=tls_context, follow_redirects=False),
    )


async def main() -> None:
    async with create_client() as client:
        response = await client.responses.create(model="gpt-5.5", input="Hello!")
        print(response.output_text)


if __name__ == "__main__":
    asyncio.run(main())
