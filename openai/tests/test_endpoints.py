import openai
import io
import json


# FILE TESTS
def test_file_upload():
    result = openai.File.create(
        file=io.StringIO(json.dumps({"text": "test file data"})),
        purpose="search",
    )
    assert result.purpose == "search"
    assert "id" in result


# COMPLETION TESTS
def test_completions():
    result = openai.Completion.create(prompt="This was a test", n=5, engine="davinci")
    assert len(result.choices) == 5


def test_completions_multiple_prompts():
    result = openai.Completion.create(
        prompt=["This was a test", "This was another test"], n=5, engine="davinci"
    )
    assert len(result.choices) == 10
