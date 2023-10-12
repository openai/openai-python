#!/usr/bin/env -S poetry run python

from openai import OpenAI

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI()

# Non-streaming:
completion = client.completions.create(
    model="text-davinci-003",
    prompt="Say this is a test",
)
print(completion.choices[0].text)

# Streaming:
stream = client.completions.create(
    model="text-davinci-003",
    prompt="Say this is a test",
    stream=True,
)
for completion in stream:
    print(completion.choices[0].text, end="")
print()
