#!/usr/bin/env python

import base64
from pathlib import Path

from openai import OpenAI

client = OpenAI()


def main() -> None:
    """Example of OpenAI image streaming with partial images."""
    stream = client.images.generate(
        model="gpt-image-1",
        prompt="A cute baby sea otter",
        n=1,
        size="1024x1024",
        stream=True,
        partial_images=3,
    )

    for event in stream:
        if event.type == "image_generation.partial_image":
            print(f"  Partial image {event.partial_image_index + 1}/3 received")
            print(f"   Size: {len(event.b64_json)} characters (base64)")

            # Save partial image to file
            filename = f"partial_{event.partial_image_index + 1}.png"
            image_data = base64.b64decode(event.b64_json)
            with open(filename, "wb") as f:
                f.write(image_data)
            print(f"   💾 Saved to: {Path(filename).resolve()}")

        elif event.type == "image_generation.completed":
            print(f"\n✅ Final image completed!")
            print(f"   Size: {len(event.b64_json)} characters (base64)")

            # Save final image to file
            filename = "final_image.png"
            image_data = base64.b64decode(event.b64_json)
            with open(filename, "wb") as f:
                f.write(image_data)
            print(f"   💾 Saved to: {Path(filename).resolve()}")

        else:
            print(f"❓ Unknown event: {event}")  # type: ignore[unreachable]


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Error generating image: {error}")