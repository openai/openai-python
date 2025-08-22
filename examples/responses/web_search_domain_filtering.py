from openai import OpenAI

client = OpenAI()

# Example with domain filtering
response = client.responses.create(
    model="gpt-4o",
    tools=[
        {
            "type": "web_search_preview",
            "user_location": {
                "type": "approximate",
                "country": "US",
                "city": "San Francisco",
            },
            # Include only academic and official sources
            "include_domains": ["arxiv.org", "openai.com", "nature.com", "*.edu", "*.gov"],
            # Exclude social media and forums
            "exclude_domains": ["medium.com", "reddit.com", "quora.com"]
        }
    ],
    input="Latest AI research papers",
)

print(response.output_text)