#!/usr/bin/env python
"""Azure OpenAI image generation example using a GPT-Image deployment.

Shows both ``images.generate`` and ``images.edit`` against an Azure deployment
of one of the GPT-Image family models (``gpt-image-1``, ``gpt-image-1-mini``,
``gpt-image-1.5``, ``gpt-image-2``).

For Azure, you supply the *deployment name* as the ``model`` argument — the
SDK still accepts that as ``str`` even when the deployment name isn't in the
``ImageModel`` literal.

Reference:
    https://learn.microsoft.com/azure/ai-foundry/openai/how-to/dall-e
"""

from __future__ import annotations

import os
import base64
from pathlib import Path

from openai import AzureOpenAI

# https://learn.microsoft.com/azure/ai-services/openai/reference#api-versions
api_version = "2024-10-21"

# Deployment name you created in the Azure portal for your GPT-Image model.
deployment = os.environ.get("AZURE_OPENAI_IMAGE_DEPLOYMENT", "gpt-image-2")

client = AzureOpenAI(
    api_version=api_version,
    # Reads credentials from the environment by default:
    #   AZURE_OPENAI_ENDPOINT  e.g. "https://<resource>.openai.azure.com"
    #   AZURE_OPENAI_API_KEY
    # You can also pass them explicitly, e.g.:
    #   azure_endpoint="https://example-endpoint.openai.azure.com",
    #   api_key="...",
)


def generate() -> Path:
    """Generate a single 1024x1024 ``low`` quality image and save it to disk."""
    result = client.images.generate(
        model=deployment,
        prompt="a cute corgi puppy sitting on grass, studio lighting",
        n=1,
        size="1024x1024",
        quality="low",
    )

    image = result.data[0] if result.data else None
    if image is None or image.b64_json is None:
        raise RuntimeError("response did not include base64 image data")

    out = Path("azure_image_generated.png")
    out.write_bytes(base64.b64decode(image.b64_json))
    print(f"generated -> {out.resolve()}")

    # The GPT-Image family returns token usage details. Older models (dall-e-*)
    # return ``usage=None``.
    if result.usage is not None:
        print(
            f"usage: input={result.usage.input_tokens} "
            f"output={result.usage.output_tokens} "
            f"total={result.usage.total_tokens}"
        )
    return out


def edit(source: Path) -> None:
    """Edit an existing image with a text prompt."""
    with source.open("rb") as f:
        result = client.images.edit(
            model=deployment,
            image=f,
            prompt="add a small red bow tie",
            size="1024x1024",
            quality="low",
            n=1,
        )

    image = result.data[0] if result.data else None
    if image is None or image.b64_json is None:
        raise RuntimeError("response did not include base64 image data")

    out = Path("azure_image_edited.png")
    out.write_bytes(base64.b64decode(image.b64_json))
    print(f"edited    -> {out.resolve()}")


def main() -> None:
    generated = generate()
    edit(generated)


if __name__ == "__main__":
    main()
