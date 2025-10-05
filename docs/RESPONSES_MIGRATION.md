# Migrating Function Calling from Chat Completions to Responses API

## Overview

The Responses API (`/v1/responses`) uses a fundamentally different approach to function calling compared to the Chat Completions API (`/v1/chat/completions`). This guide helps you migrate existing code.

## Issue Reference

- GitHub Issue: [#2677](https://github.com/openai/openai-python/issues/2677)
- API Documentation: [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling?api-mode=responses)

## Key Differences

| Aspect | Chat Completions | Responses API |
|--------|-----------------|---------------|
| **Function requests from model** | `role: "assistant"` with `tool_calls` | `type: "function_call"` items in output |
| **Function results to model** | `role: "tool"` messages | `type: "function_call_output"` items |
| **Conversation management** | Manual message construction | Append entire `response.output` |
| **Tool role support** | ✅ Supported | ❌ Not supported (raises error) |
| **Assistant tool_calls in input** | ✅ Supported | ❌ Not supported (raises error) |

## Error Messages You Might See

{
"error": {
"message": "Unknown parameter: 'input.tool_calls'.",
"type": "invalid_request_error"
}
}

text
undefined
{
"error": {
"message": "Invalid value: 'tool'. Supported values are: 'assistant', 'system', 'developer', and 'user'.",
"type": "invalid_request_error"
}
}

text

These errors indicate you're using Chat Completions patterns in the Responses API.

## Migration Steps

### Step 1: Remove Manual Tool Message Construction

**Before (Chat Completions):**
messages = [
{"role": "user", "content": "What's the weather?"},
{"role": "assistant", "tool_calls": [{"id": "call_123", ...}]},
{"role": "tool", "content": '{"temp": 20}', "tool_call_id": "call_123"}
]

text

**After (Responses API):**
input_messages = [
{"role": "user", "content": "What's the weather?"}
]

response = client.responses.create(model="gpt-4o", tools=tools, input=input_messages)
input_messages.extend(response.output) # Append entire output

text

### Step 2: Update Function Output Format

**Before:**
messages.append({
"role": "tool",
"tool_call_id": tool_call.id,
"content": json.dumps(result)
})

text

**After:**
input_messages.append({
"type": "function_call_output",
"call_id": item.call_id,
"output": json.dumps(result)
})

text

### Step 3: Update Function Call Detection

**Before:**
if response_message.tool_calls:
for tool_call in response_message.tool_calls:
# Execute function

text

**After:**
for item in response.output:
if item.type == "function_call":
# Execute function

text

## Complete Example

See [`examples/responses/function_calling_migration.py`](../examples/responses/function_calling_migration.py) for a fully working example.

## Alternative: Use Built-in Tools

For common tasks, consider using OpenAI's built-in tools instead of custom functions:

response = client.responses.create(
model="gpt-4o",
input="Search for latest AI news",
tools=[{"type": "web_search_preview"}] # No manual loop needed
)

print(response.output_text) # Automatically includes search results

text

## When to Use Each API

- **Use Chat Completions** if you need the traditional conversation format or are integrating with existing tooling
- **Use Responses API** for new projects, especially those using reasoning models or built-in tools

Both APIs are supported indefinitely.

## Additional Resources

- [Official Migration Guide](https://platform.openai.com/docs/guides/responses-vs-chat-completions)
- [Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling?api-mode=responses)
- [Example Code](../examples/responses/)