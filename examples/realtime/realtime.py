#!/usr/bin/env -S uv run python
import os
import sys
import codecs
import select

from openai import OpenAI

# Azure OpenAI Realtime Docs

# How-to: https://learn.microsoft.com/azure/ai-services/openai/how-to/realtime-audio
# Supported models and API versions: https://learn.microsoft.com/azure/ai-services/openai/how-to/realtime-audio#supported-models
# Entra ID auth: https://learn.microsoft.com/azure/ai-services/openai/how-to/managed-identity


def read_input(prompt: str) -> str:
    if sys.platform == "win32":
        # Windows console input does not support select().
        return input(prompt)

    # SIGINT may reach a WebSocket thread. Poll on the main thread so Python
    # can run its signal handler, without leaving a stdin reader at shutdown.
    print(prompt, end="", flush=True)
    decoder = codecs.getincrementaldecoder(sys.stdin.encoding)(errors=sys.stdin.errors or "strict")
    characters: list[str] = []
    while True:
        readable, _, _ = select.select([sys.stdin], [], [], 0.1)
        if not readable:
            continue
        # Do not read ahead into the next prompt or block on a partial line.
        data = os.read(sys.stdin.fileno(), 1)
        character = decoder.decode(data, final=not data)
        if character == "\n":
            return "".join(characters).removesuffix("\r")
        characters.append(character)
        if not data:
            text = "".join(characters)
            if not text:
                raise EOFError
            return text


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
            user_input = read_input("Enter a message: ")
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
