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

rsp = client.responses.parse(
    input="solve 8x + 31 = 2",
    model="gpt-4o-2024-08-06",
    text_format=MathResponse,
)

for output in rsp.output:
    if output.type != "message":
        raise Exception("Unexpected non message")

    for item in output.content:
        if item.type != "output_text":
            raise Exception("unexpected output type")

        if not item.parsed:
            raise Exception("Could not parse response")

        rich.print(item.parsed)

        print("answer: ", item.parsed.final_answer)

# or

message = rsp.output[0]
assert message.type == "message"

text = message.content[0]
assert text.type == "output_text"

if not text.parsed:
    raise Exception("Could not parse response")

rich.print(text.parsed)

print("answer: ", text.parsed.final_answer)
