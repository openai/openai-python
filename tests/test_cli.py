from __future__ import annotations

import sys
import json

import pytest

from openai.types import Completion
from openai._compat import model_parse
from openai.cli._cli import _parse_args, _build_parser
from openai.cli._errors import CLIError
from openai.cli._api.completions import CLICompletions, CLICompletionCreateArgs
from openai.types.completion_choice import CompletionChoice


def test_api_json_flag_is_passed_to_completion_args(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["openai", "api", "--json", "completions.create", "--model", "gpt-3.5-turbo-instruct"],
    )

    parsed, args, _ = _parse_args(_build_parser())
    assert args.args_model is CLICompletionCreateArgs

    completion_args = model_parse(
        CLICompletionCreateArgs, {key: value for key, value in vars(parsed).items() if value is not None}
    )
    assert completion_args.json_output is True


def test_completion_create_prints_json(capsys: pytest.CaptureFixture[str]) -> None:
    completion = Completion(
        id="cmpl-123",
        choices=[CompletionChoice(finish_reason="length", index=0, text="Hello")],
        created=1,
        model="gpt-3.5-turbo-instruct",
        object="text_completion",
    )

    CLICompletions._create(completion, json_output=True)

    assert json.loads(capsys.readouterr().out) == {
        "id": "cmpl-123",
        "choices": [{"finish_reason": "length", "index": 0, "text": "Hello"}],
        "created": 1,
        "model": "gpt-3.5-turbo-instruct",
        "object": "text_completion",
    }


def test_completion_create_rejects_streaming_json() -> None:
    args = CLICompletionCreateArgs(model="gpt-3.5-turbo-instruct", stream=True, json_output=True)

    with pytest.raises(CLIError, match="Can't stream completions as JSON"):
        CLICompletions.create(args)
