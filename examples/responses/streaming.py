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

with client.responses.stream(
    input="solve 8x + 31 = 2",
    model="gpt-4o-2024-08-06",
    text_format=MathResponse,
) as stream:
    for event in stream:
        if "output_text" in event.type:
            rich.print(event)

rich.print(stream.get_final_response())
