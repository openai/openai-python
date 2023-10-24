import openai

openai.azure = True
openai.azure_endpoint = "https://example-endpoint.openai.azure.com"

# may change in the future
# https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning
openai.api_version = "2023-07-01-preview"


completion = openai.chat.completions.create(
    model="deployment-name",  # e.g. gpt-35-instant
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.model_dump_json(indent=2))
