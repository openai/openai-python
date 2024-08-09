
# Version 3.0
# Added thread and assistant IDs
# Thread ID: thread_7ntSWu3OuitLNx7gnPVDPtJa
# Assistant ID: asst_BL0bO717dz9uhpgf6ppuWs5v
# Run ID: run_FXbb2OVKHYwAdwDhPW1o1w5c

# Import the required libraries
import os
import sys
from openai import OpenAI
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

# Create a thread and assistant
thread = client.beta.threads.create()
thread_id = thread.id
print(f"Thread ID: {thread_id}")

assistant = client.beta.assistants.create(
    name="Jervis",
    instructions=assistant_role,
    model=model_engine
)
assistant_id = assistant.id
print(f"Assistant ID: {assistant_id}")

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