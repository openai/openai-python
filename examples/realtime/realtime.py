#!/usr/bin/env -S uv run python
from openai import OpenAI

# Azure OpenAI Realtime Docs

# How-to: https://learn.microsoft.com/azure/ai-services/openai/how-to/realtime-audio
# Supported models and API versions: https://learn.microsoft.com/azure/ai-services/openai/how-to/realtime-audio#supported-models
# Entra ID auth: https://learn.microsoft.com/azure/ai-services/openai/how-to/managed-identity


def main() -> None:
    """The following example demonstrates how to configure OpenAI to use the Realtime API.
    For an audio example, see push_to_talk_app.py and update the client and model parameter accordingly.

    When prompted for user input, type a message and hit enter to send it to the model.
    Enter "q" to quit the conversation.
    """

    client = OpenAI()
    with client.realtime.connect(
        model="gpt-realtime",
    ) as connection:
        connection.session.update(
            session={
                "output_modalities": ["text"],
                "model": "gpt-realtime",
                "type": "realtime",
            }
        )
        while True:
            user_input = input("Enter a message: ")
            if user_input == "q":
                break

            connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_input}],
                }
            )
            connection.response.create()
            for event in connection:
                if event.type == "response.output_text.delta":
                    print(event.delta, flush=True, end="")
                elif event.type == "response.output_text.done":
                    print()
                elif event.type == "response.done":
                    break


main()
