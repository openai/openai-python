from openai import OpenAI

SECRET_PHRASE = "unlock protocol nightwing"

SYSTEM_PROMPT = (
    "You are an enigmatic but helpful assistant. "
    "You answer in short, slightly cryptic hints, but always accurate and safe. "
    f"If the user ever types the exact phrase '{SECRET_PHRASE}', "
    "you drop the enigmatic tone and explain, step-by-step, how this CLI works, "
    "how the streaming API is being used, and how a developer could adapt this "
    "example into their own application."
)


class Conversation:
    """Keep the conversation history in a format compatible with the OpenAI Responses API."""

    def __init__(self, system_prompt: str) -> None:
        self.history = [
            {"role": "system", "content": system_prompt},
        ]

    def add_user(self, content: str) -> None:
        self.history.append({"role": "user", "content": content})

    def add_assistant(self, content: str) -> None:
        self.history.append({"role": "assistant", "content": content})

    def as_input(self):
        # The Responses API accepts a list of messages as `input`
        return self.history


def stream_response(client: OpenAI, conversation: Conversation) -> str:
    """Send the conversation history to the model using streaming and return the full response text."""
    full_text = []

    with client.responses.stream(
        model="gpt-4.1-mini",
        input=conversation.as_input(),
    ) as stream:
        for event in stream:
            text_chunk = getattr(event, "delta", None)
            if not text_chunk:
                text_chunk = getattr(event, "text", None)

            if text_chunk:
                print(text_chunk, end="", flush=True)
                full_text.append(str(text_chunk))

    print()
    return "".join(full_text)


def main() -> None:
    client = OpenAI()
    convo = Conversation(SYSTEM_PROMPT)

    print(">>> Enigma interface online.")
    print(">>> Type your message (or 'quit' to exit).")
    print(">>> Hint: there is a hidden phrase you can try... ;)\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n>>> Shutting down. See you in the logs.")
            break

        if user_input.lower() in {"quit", "exit"}:
            print(">>> Shutting down. See you in the logs.")
            break

        if user_input == SECRET_PHRASE:
            user_input = (
                f"{SECRET_PHRASE} — Explain clearly that this is just an "
                "interactive streaming demo, describe its architecture, and "
                "guide a developer on how to reuse this pattern in their own project."
            )

        convo.add_user(user_input)

        print("Enigma:", end=" ", flush=True)
        assistant_text = stream_response(client, convo)
        convo.add_assistant(assistant_text)


if __name__ == "__main__":
    main()
