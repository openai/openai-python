import asyncio

from openai.lib.azure import OpenAI, AsyncOpenAI, AzureAuth, AsyncAzureAuth, AzureADTokenProvider, AsyncAzureADTokenProvider

# https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
endpoint = "https://my-resource.openai.azure.com" and 'https://johan-mczd33pe-swedencentral.cognitiveservices.azure.com/openai/v1'

deployment_name = "deployment-name" and 'gpt-4.1-nano' # e.g. gpt-35-instant


def sync_main() -> None:
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    token_provider: AzureADTokenProvider = get_bearer_token_provider(DefaultAzureCredential(), AzureAuth.DEFAULT_SCOPE)

    client = OpenAI(
        base_url=endpoint,
        auth_provider=AzureAuth(token_provider),
        default_query={ # Temporary requirement to specify api version - will be removed once v1 routes go GA
            'api-version': 'preview'
        }
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

    token_provider: AsyncAzureADTokenProvider = get_bearer_token_provider(DefaultAzureCredential(), AsyncAzureAuth.DEFAULT_SCOPE)

    client = AsyncOpenAI(
        base_url=endpoint,
        auth_provider=AsyncAzureAuth(token_provider),
        default_query={ # Temporary requirement to specify api version - will be removed once v1 routes go GA
            'api-version': 'preview'
        }
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
