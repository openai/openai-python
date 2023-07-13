import json
import subprocess
from pathlib import Path

import pytest

from openai.datalib.numpy_helper import HAS_NUMPY, NUMPY_INSTRUCTIONS
from openai.datalib.pandas_helper import HAS_PANDAS, PANDAS_INSTRUCTIONS


@pytest.mark.skipif(not HAS_PANDAS, reason=PANDAS_INSTRUCTIONS)
@pytest.mark.skipif(not HAS_NUMPY, reason=NUMPY_INSTRUCTIONS)
def test_long_examples_validator(tmp_path: Path) -> None:
    """
    Ensures that long_examples_validator() handles previously applied recommendations,
    namely dropped duplicates, without resulting in a KeyError.
    """

    # data
    short_prompt = "a prompt "
    long_prompt = short_prompt * 500

    short_completion = "a completion "
    long_completion = short_completion * 500

    # the order of these matters
    unprepared_training_data = [
        {"prompt": long_prompt, "completion": long_completion},  # 1 of 2 duplicates
        {"prompt": short_prompt, "completion": short_completion},
        {"prompt": long_prompt, "completion": long_completion},  # 2 of 2 duplicates
    ]

    train_file = tmp_path / "data.jsonl"
    print(train_file)  # show the full path to the temporary file
    with open(train_file, mode="w", encoding="utf-8") as file:
        for prompt_completion_row in unprepared_training_data:
            print(json.dumps(prompt_completion_row), file=file)

    prepared_data_cmd_output = subprocess.run(
        ["openai", "tools", "fine_tunes.prepare_data", "-f", str(train_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input="y\ny\ny\ny\ny",  # apply all recommendations, one at a time
        text=True,
    )

    # validate data was prepared successfully
    assert prepared_data_cmd_output.stderr == ""
    # validate get_long_indexes() applied during optional_fn() call in long_examples_validator()
    assert "indices of the long examples has changed" in prepared_data_cmd_output.stdout

    return prepared_data_cmd_output.stdout
