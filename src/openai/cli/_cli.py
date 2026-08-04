from __future__ import annotations

import sys
import argparse
from typing import Optional

from .. import __version__

_SHELL_TYPES = ("bash", "zsh", "fish", "powershell")

_BASH_COMPLETION_SCRIPT = """# openai completion for bash
# Save this to a file and source it, or add to ~/.bashrc:
#   eval "$(openai completion -s bash)"

_openai_completion() {
    local cur

    # Collect all words up to current position for context
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"

    # Complete using the CLI itself
    local IFS=$'\\n'
    local completions
    completions="$(OPENAI_COMPLETE=bash_source openai "${COMP_WORDS[@]:1}" 2>/dev/null)"
    if [[ $? -eq 0 ]]; then
        COMPREPLY=($(compgen -W "$completions" -- "$cur"))
    fi
    return 0
}

complete -F _openai_completion openai
"""

_ZSH_COMPLETION_SCRIPT = """#compdef openai
# openai completion for zsh
# Save this to a file in your fpath, or add to ~/.zshrc:
#   eval "$(openai completion -s zsh)"

_openai() {
    local -a completions
    local curcontext="$curcontext" state line
    typeset -A opt_args

    local IFS=$'\\n'
    completions=("${(@f)$(OPENAI_COMPLETE=zsh_source openai "${words[@]:1}" 2>/dev/null)}")

    if [[ -n $completions ]]; then
        _describe 'values' completions
    fi
}

_openai
"""

_FISH_COMPLETION_SCRIPT = """# openai completion for fish
# Save this to ~/.config/fish/completions/openai.fish
# or generate with: openai completion -s fish > ~/.config/fish/completions/openai.fish

function _openai_completion
    set -l args (commandline -opc)
    set -l current (commandline -ct)
    set -e args[1]
    set -l completions (OPENAI_COMPLETE=fish_source openai $args 2>/dev/null)
    if test $status -eq 0
        for comp in $completions
            echo $comp
        end
    end
end

complete -f -c openai -a "(_openai_completion)"
"""

_POWERSHELL_COMPLETION_SCRIPT = """# openai completion for PowerShell
# Add to your PowerShell profile:
#   openai completion -s powershell | Out-String | Invoke-Expression

Register-ArgumentCompleter -Native -CommandName openai -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $commandElements = $commandAst.CommandElements
    $arguments = @()
    for ($i = 1; $i -lt $commandElements.Count; $i++) {
        $arguments += $commandElements[$i].Value
    }

    $env:OPENAI_COMPLETE = "powershell_source"
    $result = & openai $arguments 2>$null

    if ($LASTEXITCODE -eq 0) {
        $result | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    }
}
"""


def _get_completions(subcommands: list[str], flags: list[str], current_word: str) -> list[str]:
    """Return possible completions based on the current word."""
    all_options = subcommands + flags
    if not current_word:
        return all_options
    return [opt for opt in all_options if opt.startswith(current_word)]


def _handle_bash_source(args: list[str]) -> None:
    """Handle bash completion source requests."""
    # Parse the command line to understand context
    subcommands = ["completion", "--help", "-h", "--version", "-V"]
    flags = ["--help", "-h", "--version", "-V"]

    if len(args) <= 1:
        # Completing the first argument
        for opt in subcommands:
            if not args or (len(args) == 1 and opt.startswith(args[0])):
                print(opt)
    else:
        current = args[-1] if args[-1] != "" else ""
        prev = args[-2] if len(args) >= 2 else ""

        if prev == "completion":
            # Complete completion subcommand flags
            completion_opts = ["--help", "-h", "-s", "--shell"]
            for opt in completion_opts:
                if opt.startswith(current):
                    print(opt)
        elif prev in ("-s", "--shell"):
            # Complete shell types
            for shell in _SHELL_TYPES:
                if shell.startswith(current):
                    print(shell)


def _handle_zsh_source(args: list[str]) -> None:
    """Handle zsh completion source requests."""
    subcommands = ["completion", "--help", "-h", "--version", "-V"]
    flags = ["--help", "-h", "--version", "-V"]

    if len(args) <= 1:
        for opt in subcommands:
            if not args or (len(args) == 1 and opt.startswith(args[0])):
                print(opt)
    else:
        current = args[-1] if args[-1] != "" else ""
        prev = args[-2] if len(args) >= 2 else ""

        if prev == "completion":
            completion_opts = ["--help", "-h", "-s", "--shell"]
            for opt in completion_opts:
                if opt.startswith(current):
                    print(opt)
        elif prev in ("-s", "--shell"):
            for shell in _SHELL_TYPES:
                if shell.startswith(current):
                    print(shell)


def _handle_fish_source(args: list[str]) -> None:
    """Handle fish completion source requests."""
    subcommands = ["completion", "--help", "-h", "--version", "-V"]

    if len(args) <= 1:
        for opt in subcommands:
            if not args or (len(args) == 1 and opt.startswith(args[0])):
                print(opt)
    else:
        current = args[-1] if args[-1] != "" else ""
        prev = args[-2] if len(args) >= 2 else ""

        if prev == "completion":
            completion_opts = ["--help", "-h", "-s", "--shell"]
            for opt in completion_opts:
                if opt.startswith(current):
                    print(opt)
        elif prev in ("-s", "--shell"):
            for shell in _SHELL_TYPES:
                if shell.startswith(current):
                    print(shell)


def _handle_powershell_source(args: list[str]) -> None:
    """Handle PowerShell completion source requests."""
    subcommands = ["completion", "--help", "-h", "--version", "-V"]

    if len(args) <= 1:
        for opt in subcommands:
            if not args or (len(args) == 1 and opt.startswith(args[0])):
                print(opt)
    else:
        current = args[-1] if args[-1] != "" else ""
        prev = args[-2] if len(args) >= 2 else ""

        if prev == "completion":
            completion_opts = ["--help", "-h", "-s", "--shell"]
            for opt in completion_opts:
                if opt.startswith(current):
                    print(opt)
        elif prev in ("-s", "--shell"):
            for shell in _SHELL_TYPES:
                if shell.startswith(current):
                    print(shell)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OpenAI CLI",
        prog="openai",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s " + __version__,
    )

    subparsers = parser.add_subparsers(dest="command")

    # completion subcommand
    completion_parser = subparsers.add_parser(
        "completion",
        help="Generate shell completion scripts",
        description="Generate shell completion scripts for the openai CLI.",
    )
    completion_parser.add_argument(
        "-s",
        "--shell",
        type=str,
        choices=_SHELL_TYPES,
        required=True,
        help="Shell type to generate completion for",
    )
    completion_parser.set_defaults(func=_run_completion)

    return parser


def _run_completion(args: argparse.Namespace) -> None:
    """Generate and print the completion script for the specified shell."""
    shell = args.shell

    if shell == "bash":
        print(_BASH_COMPLETION_SCRIPT)
    elif shell == "zsh":
        print(_ZSH_COMPLETION_SCRIPT)
    elif shell == "fish":
        print(_FISH_COMPLETION_SCRIPT)
    elif shell == "powershell":
        print(_POWERSHELL_COMPLETION_SCRIPT)


def _parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """Parse arguments and return namespace."""
    return parser.parse_args()


def _main() -> None:
    # Check if this is a completion source request
    completion_source = _get_completion_source()
    if completion_source:
        args = sys.argv[1:]
        if completion_source == "bash_source":
            _handle_bash_source(args)
        elif completion_source == "zsh_source":
            _handle_zsh_source(args)
        elif completion_source == "fish_source":
            _handle_fish_source(args)
        elif completion_source == "powershell_source":
            _handle_powershell_source(args)
        return

    parser = _build_parser()
    parsed = _parse_args(parser)

    if hasattr(parsed, "func"):
        parsed.func(parsed)
    else:
        parser.print_help()


def _get_completion_source() -> Optional[str]:
    """Check if the CLI was invoked as a completion source."""
    import os

    return os.environ.get("OPENAI_COMPLETE")


def main() -> int:
    try:
        _main()
    except Exception as err:
        sys.stderr.write(f"Error: {err}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
