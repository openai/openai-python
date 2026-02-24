"""Shell completion support for the OpenAI CLI."""

from __future__ import annotations

import argparse


BASH_COMPLETION = '''
_openai_completion() {
    local cur prev words cword
    _init_completion || return

    local commands="api tools completion"
    local global_opts="-v --verbose -b --api-base -k --api-key -p --proxy -o --organization -t --api-type --api-version --azure-endpoint --azure-ad-token -V --version -h --help"

    case "${prev}" in
        openai)
            COMPREPLY=($(compgen -W "${commands} ${global_opts}" -- "${cur}"))
            return
            ;;
        completion)
            COMPREPLY=($(compgen -W "bash zsh fish pwsh" -- "${cur}"))
            return
            ;;
        -t|--api-type)
            COMPREPLY=($(compgen -W "openai azure" -- "${cur}"))
            return
            ;;
    esac

    if [[ "${cur}" == -* ]]; then
        COMPREPLY=($(compgen -W "${global_opts}" -- "${cur}"))
    else
        COMPREPLY=($(compgen -W "${commands}" -- "${cur}"))
    fi
}

complete -F _openai_completion openai
'''

ZSH_COMPLETION = '''
#compdef openai

_openai() {
    local -a commands global_opts shells

    commands=(
        'api:Direct API calls'
        'tools:Client side tools for convenience'
        'completion:Generate shell completion scripts'
    )

    shells=(
        'bash:Generate bash completion script'
        'zsh:Generate zsh completion script'
        'fish:Generate fish completion script'
        'pwsh:Generate PowerShell completion script'
    )

    _arguments -C \
        '-v[Set verbosity]' \
        '--verbose[Set verbosity]' \
        '-b[API base URL]:url:' \
        '--api-base[API base URL]:url:' \
        '-k[API key]:key:' \
        '--api-key[API key]:key:' \
        '-t[API type]:type:(openai azure)' \
        '--api-type[API type]:type:(openai azure)' \
        '-V[Show version]' \
        '--version[Show version]' \
        '1:command:->command' \
        '*::arg:->args'

    case "$state" in
        command)
            _describe -t commands 'openai commands' commands
            ;;
        args)
            case "$words[1]" in
                completion)
                    _describe -t shells 'shells' shells
                    ;;
            esac
            ;;
    esac
}

_openai "$@"
'''

FISH_COMPLETION = '''
# Fish completion for openai CLI
complete -c openai -f
complete -c openai -s v -l verbose -d "Set verbosity"
complete -c openai -s b -l api-base -d "API base URL" -r
complete -c openai -s k -l api-key -d "API key" -r
complete -c openai -s t -l api-type -d "API type" -r -a "openai azure"
complete -c openai -s V -l version -d "Show version"
complete -c openai -n "__fish_use_subcommand" -a api -d "Direct API calls"
complete -c openai -n "__fish_use_subcommand" -a tools -d "Client side tools"
complete -c openai -n "__fish_use_subcommand" -a completion -d "Generate shell completion"
complete -c openai -n "__fish_seen_subcommand_from completion" -a "bash zsh fish pwsh"
'''

POWERSHELL_COMPLETION = '''
Register-ArgumentCompleter -Native -CommandName openai -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $commands = @('api', 'tools', 'completion')
    $shells = @('bash', 'zsh', 'fish', 'pwsh')
    $cmds = $commandAst.CommandElements
    if ($cmds.Count -eq 1) {
        $commands | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    } elseif ($cmds.Count -ge 2 -and $cmds[1].ToString() -eq 'completion') {
        $shells | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    }
}
'''


def _get_completion_script(shell: str) -> str:
    scripts = {
        "bash": BASH_COMPLETION,
        "zsh": ZSH_COMPLETION,
        "fish": FISH_COMPLETION,
        "pwsh": POWERSHELL_COMPLETION,
        "powershell": POWERSHELL_COMPLETION,
    }
    script = scripts.get(shell.lower())
    if script is None:
        raise ValueError(f"Unsupported shell: {shell}. Supported: bash, zsh, fish, pwsh")
    return script.strip()


def register_completion_commands(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers()
    for shell in ["bash", "zsh", "fish", "pwsh"]:
        shell_parser = subparsers.add_parser(shell, help=f"Generate {shell} completion script")
        shell_parser.set_defaults(func=lambda s=shell: print(_get_completion_script(s)))
