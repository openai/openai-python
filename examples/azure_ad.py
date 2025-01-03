import asyncio

from openai.lib.azure import AzureOpenAI, AsyncAzureOpenAI, AzureADTokenProvider, AsyncAzureADTokenProvider

scopes = "https://cognitiveservices.azure.com/.default"

# May change in the future
# https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning
api_version = "2023-07-01-preview"

# https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
endpoint = "https://my-resource.openai.azure.com"

deployment_name = "deployment-name"  # e.g. gpt-35-instant


def sync_main() -> None:
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    token_provider: AzureADTokenProvider = get_bearer_token_provider(DefaultAzureCredential(), scopes)

    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        azure_ad_token_provider=token_provider,
    )

    completion = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "user",
                "content": "How do I output all files in a directory using Python?",
            }
        ],
    )

    print(completion.to_json())


async def async_main() -> None:
    from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

    token_provider: AsyncAzureADTokenProvider = get_bearer_token_provider(DefaultAzureCredential(), scopes)

    client = AsyncAzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        azure_ad_token_provider=token_provider,
    )

    completion = await client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "user",
                "content": "How do I output all files in a directory using Python?",
            }
        ],
    )

    print(completion.to_json())


sync_main()

asyncio.run(async_main())
