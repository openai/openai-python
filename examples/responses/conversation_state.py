from openai import OpenAI


client = OpenAI()

response = client.responses.create(
    model="gpt-5.2",
    input="Write a haiku about recursion in programming.",
)
print(response.output_text)

response = client.responses.create(
    model="gpt-5.2",
    input="Now explain it in plain English.",
    previous_response_id=response.id,
)
print(response.output_text)

# If you manually manage conversation history instead of using
# previous_response_id, append response.output items in order. Reasoning models
# may return reasoning items together with assistant messages, and filtering
# those items down to only messages can break the next request.
