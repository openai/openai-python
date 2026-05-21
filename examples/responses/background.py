from typing import List

import rich
from pydantic import BaseModel

from openai import OpenAI


class Step(BaseModel):
    explanation: str
    output: str


class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str


client = OpenAI()
id = None

with client.responses.create(
    input="solve 8x + 31 = 2",
    model="gpt-4o-2024-08-06",
    background=True,
    stream=True,
) as stream:
    for event in stream:
        if event.type == "response.created":
            id = event.response.id
        if "output_text" in event.type:
            rich.print(event)
        if event.sequence_number == 10:
            break

print("Interrupted. Continuing...")

assert id is not None
with client.responses.retrieve(
    response_id=id,
    stream=True,
    starting_after=10,
) as stream:
    for event in stream:
        if "output_text" in event.type:
            rich.print(event)
