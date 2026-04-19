from __future__ import annotations

import pytest

from openai.cli._tools.completion import (
    CompletionArgs,
    completion,
    _bash_completion,
    _zsh_completion,
    _fish_completion,
    _powershell_completion,
)


class TestCompletionScripts:
    def test_bash_completion_contains_required_elements(self) -> None:
        script = _bash_completion()
        assert "_openai_completion()" in script
        assert "complete -F _openai_completion openai" in script
        assert "api" in script
        assert "tools" in script

    def test_zsh_completion_contains_required_elements(self) -> None:
        script = _zsh_completion()
        assert "#compdef openai" in script
        assert "_openai()" in script
        assert "api:Direct API calls" in script
        assert "tools:Client side tools" in script

    def test_fish_completion_contains_required_elements(self) -> None:
        script = _fish_completion()
        assert "complete -c openai" in script
        assert "__fish_use_subcommand" in script
        assert "api" in script
        assert "tools" in script

    def test_powershell_completion_contains_required_elements(self) -> None:
        script = _powershell_completion()
        assert "$scriptblock" in script
        assert "Register-ArgumentCompleter" in script
        assert "openai" in script


class TestCompletionFunction:
    def test_completion_bash(self, capsys: pytest.CaptureFixture[str]) -> None:
        args = CompletionArgs(shell="bash")
        completion(args)
        captured = capsys.readouterr()
        assert "_openai_completion()" in captured.out

    def test_completion_zsh(self, capsys: pytest.CaptureFixture[str]) -> None:
        args = CompletionArgs(shell="zsh")
        completion(args)
        captured = capsys.readouterr()
        assert "#compdef openai" in captured.out

    def test_completion_fish(self, capsys: pytest.CaptureFixture[str]) -> None:
        args = CompletionArgs(shell="fish")
        completion(args)
        captured = capsys.readouterr()
        assert "complete -c openai" in captured.out

    def test_completion_powershell(self, capsys: pytest.CaptureFixture[str]) -> None:
        args = CompletionArgs(shell="powershell")
        completion(args)
        captured = capsys.readouterr()
        assert "Register-ArgumentCompleter" in captured.out
