#!/usr/bin/env python

from pathlib import Path

from openai import OpenAI

# gets OPENAI_API_KEY from your environment variables
openai = OpenAI()
prompt = "An astronaut lounging in a tropical resort in space, pixel art"
def main() -> None:
    # Generate the image based on the prompt
    response = openai.images.generate(prompt=prompt)
    # Prints response with url link to image
    print(response)
if __name__ == "__main__":
    main()
