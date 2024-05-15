from __future__ import annotations

from typing_extensions import override

import openai
from openai import AssistantEventHandler
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import RunStep, RunStepDelta


class EventHandler(AssistantEventHandler):
    @override
    def on_event(self, event: AssistantStreamEvent) -> None:
        if event.event == "thread.run.step.created":
            details = event.data.step_details
            if details.type == "tool_calls":
                print("Generating code to interpret:\n\n```py")
        elif event.event == "thread.message.created":
            print("\nResponse:\n")

    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:
        print(delta.value, end="", flush=True)

    @override
    def on_run_step_done(self, run_step: RunStep) -> None:
        details = run_step.step_details
        if details.type == "tool_calls":
            for tool in details.tool_calls:
                if tool.type == "code_interpreter":
                    print("\n```\nExecuting code...")

    @override
    def on_run_step_delta(self, delta: RunStepDelta, snapshot: RunStep) -> None:
        details = delta.step_details
        if details is not None and details.type == "tool_calls":
            for tool in details.tool_calls or []:
                if tool.type == "code_interpreter" and tool.code_interpreter and tool.code_interpreter.input:
                    print(tool.code_interpreter.input, end="", flush=True)


def main() -> None:
    client = openai.OpenAI()

    assistant = client.beta.assistants.create(
        name="Math Tutor",
        instructions="You are a personal math tutor. Write and run code to answer math questions.",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-1106-preview",
    )

    try:
        question = "I need to solve the equation `3x + 11 = 14`. Can you help me?"

        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                },
            ]
        )
        print(f"Question: {question}\n")

        with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Please address the user as Jane Doe. The user has a premium account.",
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()
            print()
    finally:
        client.beta.assistants.delete(assistant.id)


main()
