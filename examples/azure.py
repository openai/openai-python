from openai import AzureOpenAI

# may change in the future
# https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning
api_version = "2023-07-01-preview"

# gets the API Key from environment variable AZURE_OPENAI_API_KEY
client = AzureOpenAI(
    api_version=api_version,
    # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
    azure_endpoint="https://example-endpoint.openai.azure.com",
)

completion = client.chat.completions.create(
    model="deployment-name",  # e.g. gpt-35-instant
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.model_dump_json(indent=2))


deployment_client = AzureOpenAI(
    api_version=api_version,
    # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
    azure_endpoint="https://example-resource.azure.openai.com/",
    # Navigate to the Azure OpenAI Studio to deploy a model.
    azure_deployment="deployment-name",  # e.g. gpt-35-instant
)

completion = deployment_client.chat.completions.create(
    model="<ignored>",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.model_dump_json(indent=2))
