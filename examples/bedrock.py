from openai import OpenAI
from openai.providers import bedrock

client = OpenAI(
    provider=bedrock(
        region="us-west-2",
    )
)

response = client.responses.create(
    model="openai.gpt-5.4",
    input="Say hello!",
)

print(response.output_text)
