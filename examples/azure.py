import os

from openai import OpenAI

# The name of your Azure OpenAI Resource.
# https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
resource = "<your resource name>"

# Corresponds to your Model deployment within your OpenAI resource, e.g. my-gpt35-16k-deployment
# Navigate to the Azure OpenAI Studio to deploy a model.
model = "<your model>"

# https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning
api_version = "2023-08-01-preview"

api_key = os.environ.get("AZURE_OPENAI_API_KEY")

if not api_key:
    raise Exception("The AZURE_OPENAI_API_KEY environment variable is missing or empty.")

# Azure OpenAI requires a custom baseURL, api-version query param, and api-key header.
client = OpenAI(
    api_key=api_key,
    base_url=f"https://{resource}.openai.azure.com/openai/deployments/{model}",
    default_query={
        "api-version": api_version,
    },
    default_headers={"api-key": api_key},
)

completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.model_dump_json(indent=2))
