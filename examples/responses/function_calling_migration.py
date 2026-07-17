"""
Migration guide: Chat Completions tool calls → Responses API function calls

This example shows how to migrate from the Chat Completions API's tool calling
pattern (using 'assistant' role with 'tool_calls' and 'tool' role) to the 
Responses API's function calling pattern (using typed items).

Related issue: https://github.com/openai/openai-python/issues/2677
"""

from openai import OpenAI
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================================
# OLD PATTERN (Chat Completions) - NO LONGER WORKS IN RESPONSES API
# ============================================================================
"""
# ❌ This pattern DOES NOT work in Responses API:
messages = [
    {"role": "developer", "content": "You are a helpful assistant"},
    {"role": "user", "content": "What's the weather in Paris?"},
    {"role": "assistant", "tool_calls": [...]},  # ❌ NOT SUPPORTED
    {"role": "tool", "content": "...", "tool_call_id": "..."}  # ❌ NOT SUPPORTED
]
response = client.responses.create(model="gpt-4o", input=messages)
# Will raise: "Unknown parameter: 'input[X].tool_calls'"
# Will raise: "Invalid value: 'tool'. Supported values are: 'assistant', 'system', 'developer', and 'user'."
"""

# ============================================================================
# NEW PATTERN (Responses API) - CORRECT APPROACH
# ============================================================================

# Define your custom functions
tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name, e.g., Paris, Tokyo"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        }
    }
]


def get_weather(location: str, unit: str = "celsius") -> dict:
    """Mock weather function - replace with actual API call"""
    mock_data = {
        "paris": {"temp": 18, "condition": "Partly cloudy"},
        "tokyo": {"temp": 24, "condition": "Sunny"},
        "london": {"temp": 12, "condition": "Rainy"}
    }
    
    data = mock_data.get(location.lower(), {"temp": 20, "condition": "Unknown"})
    return {
        "location": location,
        "temperature": data["temp"],
        "unit": unit,
        "condition": data["condition"]
    }


def execute_function_call(function_name: str, arguments: str) -> str:
    """Execute the function and return JSON result"""
    args = json.loads(arguments)
    
    if function_name == "get_weather":
        result = get_weather(**args)
    else:
        result = {"error": f"Unknown function: {function_name}"}
    
    return json.dumps(result)


def run_conversation_with_tools():
    """
    Correct pattern for using function calls in Responses API.
    
    Key differences from Chat Completions:
    1. Don't manually add 'assistant' messages with 'tool_calls'
    2. Don't use 'tool' role - use 'function_call_output' type instead
    3. Append entire response.output to input for continuation
    """
    
    # Start with user message
    input_messages = [
        {"role": "user", "content": "What's the weather in Paris and Tokyo?"}
    ]
    
    print("=" * 70)
    print("STEP 1: Initial request with function definitions")
    print("=" * 70)
    
    # Make initial request with tools
    response = client.responses.create(
        model="gpt-4o",
        instructions="You are a helpful weather assistant",
        tools=tools,
        input=input_messages
    )
    
    print(f"Response status: {response.status}")
    print(f"Output items: {len(response.output)}")
    
    # ✅ CRITICAL: Add entire output to input (not just tool_calls)
    input_messages.extend(response.output)
    
    # Check for function calls in output
    function_calls = [item for item in response.output if item.type == "function_call"]
    
    if function_calls:
        print(f"\nFound {len(function_calls)} function call(s)")
        
        print("\n" + "=" * 70)
        print("STEP 2: Execute functions and add outputs")
        print("=" * 70)
        
        # Execute each function call
        for fc in function_calls:
            print(f"\n  Executing: {fc.name}({fc.arguments})")
            result = execute_function_call(fc.name, fc.arguments)
            print(f"  Result: {result}")
            
            # ✅ Add function output as typed item (NOT 'tool' role)
            input_messages.append({
                "type": "function_call_output",  # Use 'type', not 'role'
                "call_id": fc.call_id,
                "output": result
            })
        
        print("\n" + "=" * 70)
        print("STEP 3: Get final response with function results")
        print("=" * 70)
        
        # Request final response
        final_response = client.responses.create(
            model="gpt-4o",
            instructions="You are a helpful weather assistant",
            tools=tools,
            input=input_messages
        )
        
        print(f"\nFinal answer: {final_response.output_text}")
        
    else:
        print(f"\nDirect response (no function calls): {response.output_text}")


def run_multi_turn_conversation():
    """
    Example of multi-turn conversation with function calling.
    Shows how to maintain conversation state across multiple turns.
    """
    print("\n\n" + "=" * 70)
    print("MULTI-TURN CONVERSATION EXAMPLE")
    print("=" * 70)
    
    input_messages = []
    
    # Turn 1
    input_messages.append({"role": "user", "content": "What's the weather in Paris?"})
    
    response = client.responses.create(
        model="gpt-4o",
        instructions="You are a helpful weather assistant",
        tools=tools,
        input=input_messages
    )
    
    input_messages.extend(response.output)
    
    # Execute function calls if present
    for item in response.output:
        if item.type == "function_call":
            result = execute_function_call(item.name, item.arguments)
            input_messages.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": result
            })
    
    # Get response after function execution
    response = client.responses.create(
        model="gpt-4o",
        instructions="You are a helpful weather assistant",
        tools=tools,
        input=input_messages
    )
    
    print(f"Turn 1 response: {response.output_text}")
    input_messages.extend(response.output)
    
    # Turn 2 - Follow-up question
    input_messages.append({"role": "user", "content": "What about Tokyo?"})
    
    response = client.responses.create(
        model="gpt-4o",
        instructions="You are a helpful weather assistant",
        tools=tools,
        input=input_messages
    )
    
    input_messages.extend(response.output)
    
    # Execute function calls
    for item in response.output:
        if item.type == "function_call":
            result = execute_function_call(item.name, item.arguments)
            input_messages.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": result
            })
    
    # Get final response
    response = client.responses.create(
        model="gpt-4o",
        instructions="You are a helpful weather assistant",
        tools=tools,
        input=input_messages
    )
    
    print(f"Turn 2 response: {response.output_text}")


if __name__ == "__main__":
    # Run basic example
    run_conversation_with_tools()
    
    # Run multi-turn example
    run_multi_turn_conversation()
    
    print("\n" + "=" * 70)
    print("MIGRATION CHECKLIST:")
    print("=" * 70)
    print("✅ Replace: {'role': 'assistant', 'tool_calls': [...]} ")
    print("   With: Append entire response.output to input")
    print()
    print("✅ Replace: {'role': 'tool', 'content': '...', 'tool_call_id': '...'}")
    print("   With: {'type': 'function_call_output', 'call_id': '...', 'output': '...'}")
    print()
    print("✅ Always extend input_messages with response.output")
    print()
    print("✅ Check item.type == 'function_call' to detect function calls")
    print("=" * 70)
