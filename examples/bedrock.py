from openai import BedrockOpenAI

client = BedrockOpenAI()

# For refreshed Bedrock bearer tokens:
# client = BedrockOpenAI(aws_region="us-west-2", bedrock_token_provider=get_bedrock_token)

response = client.responses.create(
    model="openai.gpt-5.4",
    input="Say hello!",
)

print(response.output_text)
