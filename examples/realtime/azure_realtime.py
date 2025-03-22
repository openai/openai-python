import os
import asyncio

from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

from openai import AsyncAzureOpenAI

# Azure OpenAI Realtime Docs

# How-to: https://learn.microsoft.com/azure/ai-services/openai/how-to/realtime-audio
# Supported models and API versions: https://learn.microsoft.com/azure/ai-services/openai/how-to/realtime-audio#supported-models
# Entra ID auth: https://learn.microsoft.com/azure/ai-services/openai/how-to/managed-identity


async def main() -> None:
    """The following example demonstrates how to configure Azure OpenAI to use the Realtime API.
    For an audio example, see push_to_talk_app.py and update the client and model parameter accordingly.

    When prompted for user input, type a message and hit enter to send it to the model.
    Enter "q" to quit the conversation.
    """

    credential = DefaultAzureCredential()
    client = AsyncAzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_ad_token_provider=get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default"),
        api_version="2024-10-01-preview",
    )
    async with client.beta.realtime.connect(
        model="gpt-4o-realtime-preview",  # deployment name for your model
    ) as connection:
        await connection.session.update(session={"modalities": ["text"]})  # type: ignore
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
                if event.type == "response.text.delta":
                    print(event.delta, flush=True, end="")
                elif event.type == "response.text.done":
                    print()
                elif event.type == "response.done":
                    break

    await credential.close()


asyncio.run(main())
