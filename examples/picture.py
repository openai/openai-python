#!/usr/bin/env python
"""
Example script demonstrating image generation using DALL-E 3.

This script generates an image from a text prompt using OpenAI's DALL-E 3 model
and prints the response containing a URL to the generated image.
"""

from openai import OpenAI

# gets OPENAI_API_KEY from your environment variables
openai = OpenAI()

prompt = "An astronaut lounging in a tropical resort in space, pixel art"
model = "dall-e-3"


def main() -> None:
    # Generate an image based on the prompt
    response = openai.images.generate(prompt=prompt, model=model)

    # Prints response containing a URL link to image
    print(response)


if __name__ == "__main__":
    main()
