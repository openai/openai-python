#!/usr/bin/env -S rye run python

import os
import ssl
import asyncio

from openai import AsyncOpenAI, DefaultAsyncHttpx2Client


async def main() -> None:
    ssl_context = ssl.create_default_context(
        cafile=os.environ.get("OPENAI_MTLS_CA_BUNDLE"),
    )
    ssl_context.load_cert_chain(
        # Leaf certificate first; if intermediate-chain support is enabled,
        # follow it with all required intermediates.
        certfile=os.environ["OPENAI_MTLS_CERTIFICATE_CHAIN"],
        keyfile=os.environ["OPENAI_MTLS_PRIVATE_KEY"],
        password=os.environ.get("OPENAI_MTLS_PRIVATE_KEY_PASSWORD"),
    )

    async with AsyncOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get(
            "OPENAI_BASE_URL",
            "https://mtls.api.openai.com/v1",
        ),
        http_client=DefaultAsyncHttpx2Client(
            verify=ssl_context,
            follow_redirects=False,
        ),
    ) as client:
        print(await client.files.list())


asyncio.run(main())
