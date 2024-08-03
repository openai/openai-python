
# Version: 4.0
# This is a simple Python script that demonstrates how to use the OpenAI API to generate chat completions.
# This version includes the following updates:

# Added Chatlog
# Added user and bot names
# Added conversation log
# Added conversation log to text file
# Added conversation log to JSON file  
# Added assistant role
# Added thread and assistant IDs
# Created new thread ID: thread_QkJ2l057N4An9QvO7ZxAziep
# Created new assistant ID: asst_RL5yFuDStQtNvsJCTPNzDOM9
# Run ID: run_TYHQPH2Li5vkOu0VeWDKvHrP

# Import the required libraries
import os
import sys
import json
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables (loads your API Key) from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the model engine
model_engine = "gpt-4o"  # Ensure this is the correct model ID

# Define the assistant's role
assistant_role = "You are a useful helper, professor, the best programmer in the world, and computer technician in the style and tone of Christopher Walken."

# Define user and bot names
user_name = "Ranger"
bot_name = "Jervis"

# Define the thread and assistant IDs (these would typically be obtained from previous API calls or setup)
thread_id = os.getenv("THREAD_ID", None)
assistant_id = os.getenv("ASSISTANT_ID", None)

def create_thread_and_assistant():
    global thread_id, assistant_id
    thread = client.beta.threads.create()
    thread_id = thread.id
    assistant = client.beta.assistants.create(
        name="Jervis",
        instructions=assistant_role,
        model=model_engine
    )
    assistant_id = assistant.id
    print(f"Created new thread ID: {thread_id}")
    print(f"Created new assistant ID: {assistant_id}")

# Create thread and assistant if they don't exist
if not thread_id or not assistant_id:
    create_thread_and_assistant()

def chat_gpt4(query):
    # Add the user's message to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=query
    )

    # Create and poll a new run within the specified thread
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    # Optionally, handle the result
    print(f"Run ID: {run.id}")
    print(f"Status: {run.status}")

    # Retrieve the messages added by the assistant to the thread
    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )

    # Print the response from the model
    if messages.data:
        print(f"{bot_name}: {messages.data[0].content[0].text.value}")
    else:
        print("No messages found.")

    # Create a conversation log
    conversation_log = []

    try:
        # Generate a chat completion
        chat_completion = client.chat.completions.create(
            model=model_engine,
            messages=[
                {"role": "system", "content": assistant_role},
                {"role": "user", "content": query}
            ]
        )

        # Extract the response from the model
        response_content = chat_completion.choices[0].message.content

        # Add the user's query and the assistant's response to the conversation log
        conversation_log.append({"role": "user", "content": query})
        conversation_log.append({"role": "assistant", "content": response_content})

    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Save the conversation to a text file
    with open('rgpt4.txt', 'a', encoding='utf-8') as file:
        file.write("=== GPT-4 Chat started at {} ===\n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        for entry in conversation_log:
            file.write(f"[{entry['role'].capitalize()}]: {entry['content']}\n")
        file.write("=== GPT-4 Chat ended at {} ===\n\n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

    # Save the conversation to a JSON file
    with open('rgpt4.json', 'a', encoding='utf-8') as json_file:
        json.dump(conversation_log, json_file, ensure_ascii=False, indent=4)
        json_file.write('\n')

def main():
    if len(sys.argv) > 1:
        # If a question is provided as a command-line argument
        query = ' '.join(sys.argv[1:])
        chat_gpt4(query)
    else:
        # Start the conversation
        print(f"{bot_name}: How can I help?")

    while True:
        query = input(f"{user_name}: ")
        if query.lower() in ["exit", "quit"]:
            break
        chat_gpt4(query)
        follow_up = input(f"{bot_name}: Do you have another question? (yes/no): ")
        if follow_up.lower() not in ["yes", "y"]:
            break

if __name__ == "__main__":
    main()