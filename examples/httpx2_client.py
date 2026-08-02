from openai import OpenAI, DefaultHttpx2Client

client = OpenAI(http_client=DefaultHttpx2Client())

response = client.responses.create(
    model="gpt-5.2",
    input="Say this is a test",
)

print(response.output_text)
