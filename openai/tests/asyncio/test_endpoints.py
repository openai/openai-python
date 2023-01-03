import io
import json

import pytest

import openai
from openai import error


pytestmark = [pytest.mark.asyncio]


# FILE TESTS
async def test_file_upload():
    result = await openai.File.acreate(
        file=io.StringIO(json.dumps({"text": "test file data"})),
        purpose="search",
    )
    assert result.purpose == "search"
    assert "id" in result

    result = await openai.File.aretrieve(id=result.id)
    assert result.status == "uploaded"


# COMPLETION TESTS
async def test_completions():
    result = await openai.Completion.acreate(
        prompt="This was a test", n=5, engine="ada"
    )
    assert len(result.choices) == 5


async def test_completions_multiple_prompts():
    result = await openai.Completion.acreate(
        prompt=["This was a test", "This was another test"], n=5, engine="ada"
    )
    assert len(result.choices) == 10


async def test_completions_model():
    result = await openai.Completion.acreate(prompt="This was a test", n=5, model="ada")
    assert len(result.choices) == 5
    assert result.model.startswith("ada")


async def test_timeout_raises_error():
    # A query that should take awhile to return
    with pytest.raises(error.Timeout):
        await openai.Completion.acreate(
            prompt="test" * 1000,
            n=10,
            model="ada",
            max_tokens=100,
            request_timeout=0.01,
        )


async def test_timeout_does_not_error():
    # A query that should be fast
    await openai.Completion.acreate(
        prompt="test",
        model="ada",
        request_timeout=10,
    )
