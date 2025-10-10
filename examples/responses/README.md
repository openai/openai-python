# Responses API Examples

Examples demonstrating the Responses API functionality.

## Files

- **`function_calling_migration.py`** - Complete guide for migrating from Chat Completions tool calling to Responses API function calling. Addresses [Issue #2677](https://github.com/openai/openai-python/issues/2677).

## Key Differences from Chat Completions

The Responses API does **NOT** support:
- `role: "assistant"` messages with `tool_calls` in input
- `role: "tool"` messages

Instead, use:
- `type: "function_call"` items (from model output)
- `type: "function_call_output"` items (your function results)

See `function_calling_migration.py` for detailed examples.

## Running Examples

export OPENAI_API_KEY="your-api-key"
python examples/responses/function_calling_migration.py

text
undefined