from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function":{
            "name": "get_horoscope",
            "description": "Get today's horoscope for an astrological sign.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sign": {
                        "type": "string",
                        "description": "An astrological sign like Taurus or Aquarius",
                    },
                },
                "required": ["sign"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "say",
            "description": "say something to the user when no other tools are available",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "say something to the user",
                    }
                },
                "required": ["text"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and country name e.g. Bogotá, Colombia",
                    }
                },
                "required": ["location"],
            },
        }
    },
]

tool_choice = {
    "type": "allowed_tools",
    "mode": "auto",
    "allowed_tools": {
        "mode": "auto",
        "tools": [
            {"type": "function", "function": {"name": 'get_weather'}},
            {"type": "function", "function": {"name": 'say'}},
        ]
    }

}

messages = [ {"role": "user", "content": "What is my horoscope? I am an Aquarius."} ]

response = client.chat.completions.create(
  messages = messages,
  model = "gpt-4o-2024-11-20",
  stream = False,
  tools = tools,
  tool_choice = tool_choice
)

print("Response:", response.choices[0].message.content)
print("Hit Tools:", [ i.function for i in response.choices[0].message.tool_calls] )
