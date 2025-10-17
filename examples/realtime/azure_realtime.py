#!/usr/bin/env uv run
#
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "textual",
#     "numpy",
#     "pyaudio",
#     "pydub",
#     "sounddevice",
#     "openai[realtime]",
#     "azure-identity",
#     "aiohttp",
#     "python-dotenv",
# ]
#
# [tool.uv.sources]
# openai = { path = "../../", editable = true }
# ///

import logging
from dotenv import load_dotenv
import httpx

load_dotenv()

import os
import base64
import asyncio

from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

from openai import AsyncAzureOpenAI

# Azure OpenAI Realtime Docs

# How-to: https://learn.microsoft.com/azure/ai-services/openai/how-to/realtime-audio
# Supported models and API versions: https://learn.microsoft.com/azure/ai-services/openai/how-to/realtime-audio#supported-models
# Entra ID auth: https://learn.microsoft.com/azure/ai-services/openai/how-to/managed-identity

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("websockets").setLevel(logging.DEBUG)

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.DEBUG,
)


async def main() -> None:
    """The following example demonstrates how to configure Azure OpenAI to use the Realtime API.
    For an audio example, see push_to_talk_app.py and update the client and model parameter accordingly.

    When prompted for user input, type a message and hit enter to send it to the model.
    Enter "q" to quit the conversation.
    """

    credential = DefaultAzureCredential()

    if not (api_key := os.environ.get("AZURE_OPENAI_API_KEY")):
        token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
    else:
        token_provider = None

    endpoint = httpx.URL(os.environ["AZURE_OPENAI_ENDPOINT"])
    if endpoint.scheme in ("ws", "wss"):
        websocket_base_url, azure_endpoint = f"{endpoint}/openai", None
    else:
        websocket_base_url, azure_endpoint = None, endpoint

    print(f"{websocket_base_url=}, {azure_endpoint=}")

    client = AsyncAzureOpenAI(
        azure_deployment="gpt-realtime",
        azure_endpoint=str(azure_endpoint),
        websocket_base_url=websocket_base_url,
        azure_ad_token_provider=token_provider,
        api_key=api_key,
        api_version="2025-04-01-preview"
    )  # type: ignore

    async with client.beta.realtime.connect(
        model="gpt-realtime",  # deployment name for your model
    ) as connection:
        await connection.session.update(
            session={
                # "output_modalities": ["text"],
                # "model": "gpt-realtime",
                # "type": "realtime",
            }
        )

        while True:
            user_input = input("Enter a message: ")
            if user_input == "q":
                break

            await connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_input}],
                }
            )

            await connection.response.create()
            async for event in connection:
                print(f"Event: {event.type}")

                if event.type == "error":
                    print(f"ERROR: {event}")

                if event.type == "response.text.delta":
                    print(event.delta, flush=True, end="")
                if event.type == "response.text.done":
                    print()
                if event.type == "response.done":
                    print(f"final response: {event.response.output[0].content[0].transcript}")
                    print(f"usage: {event.response.usage}")

                if event.type == "response.audio.delta":
                    audio_data = base64.b64decode(event.delta)
                    print(f"Received {len(audio_data)} bytes of audio data.")

                if event.type == "response.audio_transcript.delta":
                    print(f"Received text delta: {event.delta}")

    await credential.close()


asyncio.run(main())
