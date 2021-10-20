import io
import json

import openai


# FILE TESTS
def test_file_upload():
    result = openai.File.create(
        file=io.StringIO(json.dumps({"text": "test file data"})),
        purpose="search",
    )
    assert result.purpose == "search"
    assert "id" in result

    result = openai.File.retrieve(id=result.id)
    assert result.status == "uploaded"


# COMPLETION TESTS
def test_completions():
    result = openai.Completion.create(prompt="This was a test", n=5, engine="ada")
    assert len(result.choices) == 5


def test_completions_multiple_prompts():
    result = openai.Completion.create(
        prompt=["This was a test", "This was another test"], n=5, engine="ada"
    )
    assert len(result.choices) == 10
