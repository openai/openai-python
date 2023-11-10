import openai
import time

# gets API Key from environment variable OPENAI_API_KEY
client = openai.OpenAI()

assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-1106-preview",
)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
)

run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="Please address the user as Jane Doe. The user has a premium account."
)

print("checking assistant status. ")
while True:
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

    if run.status == "completed":
        print("done!")
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )

        print("messages: ")
        for message in messages:
            print({
                "role": message.role,
                "message": message.content[0].text.value
            })

        client.beta.assistants.delete(assistant.id)
        
        break
    else:
        print("in progress...")
        time.sleep(5)