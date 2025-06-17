#!/usr/bin/env -S rye run python

"""
This script demonstrates how to handle various API errors that the
OpenAI Python library might raise, as documented in the README.

It's a good practice to handle these exceptions gracefully in your applications.
"""

import openai
from openai import OpenAI


def trigger_authentication_error():
    """
    Demonstrates handling an AuthenticationError.
    This error is raised when the API key is invalid or missing.
    This function will always work, as it does not require a valid key.
    """
    print("\n--- Triggering AuthenticationError ---")
    try:
        # We'll use a client with a deliberately invalid API key.
        invalid_key_client = OpenAI(api_key="invalid-key-for-testing")
        invalid_key_client.models.list()
    except openai.AuthenticationError as e:
        print("Successfully caught an AuthenticationError!")
        print(f"Status code: {e.status_code}")
        if isinstance(e.body, dict) and "message" in e.body:
            print(f"Error message: {e.body['message']}")
        print(f"Request ID: {e.request_id}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def trigger_not_found_error():
    """
    Demonstrates handling a NotFoundError.
    This happens when you try to access a resource that doesn't exist.
    This function REQUIRES a valid OPENAI_API_KEY to be set.
    """
    print("\n--- Triggering NotFoundError ---")
    try:
        # Client is created here. It will raise an error if the key is missing.
        client = OpenAI()
        client.models.retrieve("this-model-does-not-exist")
    except openai.NotFoundError as e:
        print("Successfully caught a NotFoundError!")
        print(f"Status code: {e.status_code}")
        if isinstance(e.body, dict) and "message" in e.body:
            print(f"Error message: {e.body['message']}")
        print(f"Request ID: {e.request_id}")
    except openai.OpenAIError as e:
        # Catches errors like missing API key.
        print(f"Skipping test. An OpenAI API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def trigger_bad_request_error():
    """
    Demonstrates handling a BadRequestError.
    This occurs when the API request is malformed (e.g., invalid parameters).
    This function REQUIRES a valid OPENAI_API_KEY to be set.
    """
    print("\n--- Triggering BadRequestError ---")
    try:
        # Client is created here.
        client = OpenAI()
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello!"}],
            temperature=99.0,
        )
    except openai.BadRequestError as e:
        print("Successfully caught a BadRequestError!")
        print(f"Status code: {e.status_code}")
        if isinstance(e.body, dict) and "message" in e.body:
            print(f"Error message: {e.body['message']}")
        print(f"Request ID: {e.request_id}")
    except openai.OpenAIError as e:
        # Catches errors like missing API key.
        print(f"Skipping test. An OpenAI API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def handle_rate_limit_error_concept():
    """
    Provides a template for handling RateLimitError.
    """
    print("\n--- Conceptual Handling of RateLimitError ---")
    print("This function only shows the 'except' block code for a RateLimitError.")
    # In a real app, the try block would contain your actual API call.
    # except openai.RateLimitError as e:
    #     print("Caught a RateLimitError!")
    #     print("In a real application, you should implement exponential backoff here.")


if __name__ == "__main__":
    print("Running OpenAI Error Handling Examples...")
    print("Note: Some examples require a valid OPENAI_API_KEY to be set in your environment.")

    trigger_authentication_error()
    trigger_not_found_error()
    trigger_bad_request_error()
    handle_rate_limit_error_concept()

    print("\n--- All examples finished ---")
