import openai
openai.api_key = "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"  # supply your API key however you choose

completion = openai.ChatCompletion.create(model="gpt-4-0314", messages=[{"role": "user", "content": ""}])
print(completion.choices[0].message.content)