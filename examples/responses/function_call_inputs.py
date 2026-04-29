from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {
            "role": "developer",
            "content": "Use the supplied function results to answer.",
        },
        {
            "role": "user",
            "content": "What is the current order status?",
        },
        {
            "type": "function_call",
            "call_id": "call_123",
            "name": "get_order_status",
            "arguments": '{"order_id":"order_123"}',
        },
        {
            "type": "function_call_output",
            "call_id": "call_123",
            "output": '{"status":"shipped"}',
        },
    ],
)

print(response.output_text)
