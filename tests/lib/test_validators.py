from __future__ import annotations

from openai.lib._validators import _fine_tuning_instructions


def test_fine_tuning_instructions_use_current_python_client() -> None:
    instructions = _fine_tuning_instructions("prepared.jsonl")

    assert 'client.files.create(..., purpose="fine-tune")' in instructions
    assert "client.fine_tuning.jobs.create(...)" in instructions
    assert "openai api fine_tunes.create" not in instructions


def test_fine_tuning_instructions_include_validation_file() -> None:
    instructions = _fine_tuning_instructions("prepared_train.jsonl", validation_file="prepared_valid.jsonl")

    assert 'Upload "prepared_train.jsonl"' in instructions
    assert 'after uploading "prepared_valid.jsonl"' in instructions
    assert "`validation_file`" in instructions
