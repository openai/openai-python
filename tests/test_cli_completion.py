from __future__ import annotations

from openai.cli._cli import _build_parser
from openai.cli._completion import generate_completion


def test_bash_completion_includes_top_level_commands() -> None:
    output = generate_completion(_build_parser(), "bash")

    assert "complete -F _openai_completion openai" in output
    assert "api completion" in output
    assert "chat.completions.create" in output
    assert "fine_tunes.prepare_data" in output


def test_zsh_completion_includes_shell_choices() -> None:
    output = generate_completion(_build_parser(), "zsh")

    assert "#compdef openai" in output
    assert "bash zsh fish powershell" in output


def test_fish_completion_includes_completion_subcommand() -> None:
    output = generate_completion(_build_parser(), "fish")

    assert "complete -c openai -n '__fish_use_subcommand' -a 'completion'" in output
    assert "__fish_seen_subcommand_from api" in output


def test_powershell_completion_registers_openai() -> None:
    output = generate_completion(_build_parser(), "powershell")

    assert "Register-ArgumentCompleter -Native -CommandName openai" in output
    assert "'completion' { @('bash', 'zsh', 'fish', 'powershell') }" in output
