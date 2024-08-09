# Version: 5.0
# This is a simple Python script that demonstrates how to use the OpenAI API to generate chat completions.
# This version includes the following updates:

# We can now upload files to a vector store and associate them with the assistant and thread IDs.
# We can also update the assistant with the vector store to enable file search capabilities.
# We can chat with the assistant and provide file paths to upload files and search for relevant information.
# We can save the conversation log to a text and JSON file for future reference.

# The first run of this script got back the following response:
# Created new thread ID: thread_7zXbvYJbZnt83X0FV4UHIxha
# Created new assistant ID: asst_bc086vrjzFFh0N312QjfOxp4
# Run ID: run_z8xPUjmFFlGxONvhfHDGDBcK

# The second run of this script got back the following response:
# Created new thread ID: thread_jQZNE3hs968JWWZAPiB2Tk2C
# Created new assistant ID: asst_vnInhkMyxNkcON1UZpJylQN8
# Run ID: run_WHGNdDZZO5RZPZjsai1UA2nT

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
assistant_role = "You are a useful helper, professor, the best programmer in the world, and computer technician in the style and tone of Christopher Walken. you are a genius programmer and expert at all technology and languages, you are best when you love to help people, provide suggestions for improvements and also to double-check your code to check for errors, as we all make them, and give detailed step-by-step instructions as if I am 14 years old and only learning, but I have some basics and understanding of python code, but I love to learn so explain everything to me."

# Define user and bot names
user_name = "Ranger"
bot_name = "Jervis"

# Define the thread and assistant IDs (these would typically be obtained from previous API calls or setup)
thread_id = os.getenv("THREAD_ID", None)
assistant_id = os.getenv("ASSISTANT_ID", None)
vector_store_id = os.getenv("VECTOR_STORE_ID", None)

def create_thread_and_assistant():
    global thread_id, assistant_id, vector_store_id
    thread = client.beta.threads.create()
    thread_id = thread.id
    assistant = client.beta.assistants.create(
        name="Programming genius Assistant. Use your knowledge base to answer questions about python json and all other programming languages.",
        instructions=assistant_role,
        model=model_engine,
        tools=[{"type": "file_search"}],
    )
    assistant_id = assistant.id
    print(f"Created new thread ID: {thread_id}")
    print(f"Created new assistant ID: {assistant_id}")

# Create thread and assistant if they don't exist
if not thread_id or not assistant_id:
    create_thread_and_assistant()

def upload_files_to_vector_store(file_paths):
    global vector_store_id
    if not vector_store_id:
        vector_store = client.beta.vector_stores.create(name="Programming Files")
        vector_store_id = vector_store.id
    
    file_streams = [open(path, "rb") for path in file_paths]
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store_id, files=file_streams
    )
    print(file_batch.status)
    print(file_batch.file_counts)

def update_assistant_with_vector_store():
    client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )

def chat_gpt4(query, files=None):
    if files:
        upload_files_to_vector_store(files)
        update_assistant_with_vector_store()

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

        # Check if the user wants to upload files
        if query.lower() == "upload":
            file_paths = input("Enter the file paths (comma-separated): ").split(',')
            files = [path.strip() for path in file_paths]
            chat_gpt4(query, files=files)
        else:
            chat_gpt4(query)

        follow_up = input(f"{bot_name}: Do you have another question? (yes/no): ")
        if follow_up.lower() not in ["yes", "y"]:
            break

if __name__ == "__main__":
    main()