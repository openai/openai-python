from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential


credentials = DefaultAzureCredential()


def get_token() -> str:
    return credentials.get_token("https://cognitiveservices.azure.com/.default").token


# may change in the future
# https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning
api_version = "2023-07-01-preview"

# https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
endpoint = "https://my-resource.openai.azure.com"

client = AzureOpenAI(
    api_version=api_version,
    endpoint=endpoint,
    get_ad_token=get_token,
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
