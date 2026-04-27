from __future__ import annotations

import sys
import argparse
from typing import Literal

from ._models import BaseModel

Shell = Literal["bash", "zsh", "fish", "powershell"]


class CompletionArgs(BaseModel):
    shell: Shell


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser], parser: argparse.ArgumentParser) -> None:
    sub = subparsers.add_parser(
        "completion",
        help="Generate shell completion script",
        description="Generate a shell completion script for the OpenAI CLI.",
    )
    sub.add_argument(
        "shell",
        choices=("bash", "zsh", "fish", "powershell"),
        help="Shell to generate completions for.",
    )
    sub.set_defaults(
        func=lambda args: print_completion(parser, args.shell),
        args_model=CompletionArgs,
    )


def print_completion(parser: argparse.ArgumentParser, shell: Shell) -> None:
    sys.stdout.write(generate_completion(parser, shell))


def generate_completion(parser: argparse.ArgumentParser, shell: Shell) -> str:
    commands = _collect_commands(parser)
    top_level = sorted(commands[()])
    api_commands = sorted(commands.get(("api",), []))
    tool_commands = sorted(commands.get(("tools",), []))
    shells = ["bash", "zsh", "fish", "powershell"]

    if shell == "bash":
        return _bash(top_level, api_commands, tool_commands, shells)
    if shell == "zsh":
        return _zsh(top_level, api_commands, tool_commands, shells)
    if shell == "fish":
        return _fish(top_level, api_commands, tool_commands, shells)
    return _powershell(top_level, api_commands, tool_commands, shells)


def _collect_commands(parser: argparse.ArgumentParser) -> dict[tuple[str, ...], list[str]]:
    commands: dict[tuple[str, ...], list[str]] = {}

    def visit(current: argparse.ArgumentParser, path: tuple[str, ...]) -> None:
        for action in current._actions:
            choices = getattr(action, "choices", None)
            if not isinstance(choices, dict) or not choices:
                continue
            subcommands = [name for name in choices if name != "completion"]
            if path == ():
                subcommands.append("completion")
            commands[path] = sorted(set(subcommands))
            for name, subparser in choices.items():
                if isinstance(subparser, argparse.ArgumentParser):
                    visit(subparser, (*path, name))

    visit(parser, ())
    return commands


def _quote_words(words: list[str]) -> str:
    return " ".join(words)


def _bash(
    top_level: list[str],
    api_commands: list[str],
    tool_commands: list[str],
    shells: list[str],
) -> str:
    return f'''# bash completion for openai
_openai_completion() {{
    local cur root
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    root="${{COMP_WORDS[1]}}"

    case "$root" in
        api)
            if [[ $COMP_CWORD -eq 2 ]]; then
                COMPREPLY=( $(compgen -W "{_quote_words(api_commands)}" -- "$cur") )
            fi
            ;;
        tools)
            if [[ $COMP_CWORD -eq 2 ]]; then
                COMPREPLY=( $(compgen -W "{_quote_words(tool_commands)}" -- "$cur") )
            fi
            ;;
        completion)
            if [[ $COMP_CWORD -eq 2 ]]; then
                COMPREPLY=( $(compgen -W "{_quote_words(shells)}" -- "$cur") )
            fi
            ;;
        *)
            if [[ "$cur" == -* ]]; then
                COMPREPLY=( $(compgen -W "-v --verbose -b --api-base -k --api-key -p --proxy -o --organization -t --api-type --api-version --azure-endpoint --azure-ad-token -V --version -h --help" -- "$cur") )
            else
                COMPREPLY=( $(compgen -W "{_quote_words(top_level)}" -- "$cur") )
            fi
            ;;
    esac
}}
complete -F _openai_completion openai
'''


def _zsh(
    top_level: list[str],
    api_commands: list[str],
    tool_commands: list[str],
    shells: list[str],
) -> str:
    return f"""#compdef openai
# zsh completion for openai
_openai() {{
    local -a commands api_commands tool_commands shells
    commands=({_quote_words(top_level)})
    api_commands=({_quote_words(api_commands)})
    tool_commands=({_quote_words(tool_commands)})
    shells=({_quote_words(shells)})

    case $words[2] in
        api) _values 'api command' $api_commands ;;
        tools) _values 'tool command' $tool_commands ;;
        completion) _values 'shell' $shells ;;
        *) _values 'command' $commands ;;
    esac
}}
compdef _openai openai
"""


def _fish(
    top_level: list[str],
    api_commands: list[str],
    tool_commands: list[str],
    shells: list[str],
) -> str:
    lines = ["# fish completion for openai"]
    for command in top_level:
        lines.append(f"complete -c openai -n '__fish_use_subcommand' -a '{command}'")
    for command in api_commands:
        lines.append(f"complete -c openai -n '__fish_seen_subcommand_from api' -a '{command}'")
    for command in tool_commands:
        lines.append(f"complete -c openai -n '__fish_seen_subcommand_from tools' -a '{command}'")
    for shell in shells:
        lines.append(f"complete -c openai -n '__fish_seen_subcommand_from completion' -a '{shell}'")
    return "\n".join(lines) + "\n"


def _powershell(
    top_level: list[str],
    api_commands: list[str],
    tool_commands: list[str],
    shells: list[str],
) -> str:
    top_level_values = "', '".join(top_level)
    api_values = "', '".join(api_commands)
    tool_values = "', '".join(tool_commands)
    shell_values = "', '".join(shells)
    return f"""# PowerShell completion for openai
Register-ArgumentCompleter -Native -CommandName openai -ScriptBlock {{
    param($wordToComplete, $commandAst, $cursorPosition)
    $words = $commandAst.CommandElements | ForEach-Object {{ $_.Extent.Text }}
    $candidates = switch ($words[1]) {{
        'api' {{ @('{api_values}') }}
        'tools' {{ @('{tool_values}') }}
        'completion' {{ @('{shell_values}') }}
        default {{ @('{top_level_values}') }}
    }}
    $candidates | Where-Object {{ $_ -like "$wordToComplete*" }} | ForEach-Object {{
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }}
}}
"""
