import importlib.util
from pathlib import Path

import pytest

project_root = Path(__file__).resolve().parents[1]
completion_path = project_root / "src" / "openai" / "cli" / "_completion.py"
cli_path = project_root / "src" / "openai" / "cli" / "_cli.py"

spec_completion = importlib.util.spec_from_file_location("openai.cli._completion", completion_path)
assert spec_completion and spec_completion.loader
completion = importlib.util.module_from_spec(spec_completion)
spec_completion.loader.exec_module(completion)
import sys

sys.modules["openai.cli._completion"] = completion

spec_cli = importlib.util.spec_from_file_location("openai.cli._cli", cli_path)
assert spec_cli and spec_cli.loader
_cli = importlib.util.module_from_spec(spec_cli)
spec_cli.loader.exec_module(_cli)


@pytest.mark.parametrize("shell", ["bash", "zsh", "tcsh"])
def test_completion_generates_script(shell: str, capsys: pytest.CaptureFixture[str]) -> None:
    parser = _cli._build_parser()
    with pytest.raises(SystemExit) as exc:
        completion.handle_completion(parser, ["--completion", shell])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert len(captured.out) > 100
    assert "openai" in captured.out.lower()
