"""
Shell completion support for the OpenAI CLI.

This module provides shell completion scripts for bash, zsh, fish, and powershell.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional


def register_commands(parser: argparse.ArgumentParser) -> None:
    """Register the complete subcommand."""
    subparsers = parser.add_subparsers(dest="shell")

    # Add subparser for each shell
    for shell in ["bash", "zsh", "fish", "powershell"]:
        subparsers.add_parser(shell, help=f"Generate completion script for {shell}")

    parser.set_defaults(func=generate_completion)


def generate_completion(args: argparse.Namespace) -> None:
    """Generate and print the completion script for the specified shell."""
    shell = args.shell

    if shell is None:
        print("Error: No shell specified. Use: openai complete <shell>", file=sys.stderr)
        print("Supported shells: bash, zsh, fish, powershell", file=sys.stderr)
        sys.exit(1)

    scripts = {
        "bash": BASH_COMPLETION,
        "zsh": ZSH_COMPLETION,
        "fish": FISH_COMPLETION,
        "powershell": POWERSHELL_COMPLETION,
    }

    script = scripts.get(shell)
    if script is None:
        print(f"Error: Unsupported shell '{shell}'", file=sys.stderr)
        print("Supported shells: bash, zsh, fish, powershell", file=sys.stderr)
        sys.exit(1)

    print(script)


# Bash completion script
BASH_COMPLETION = r'''# bash completion for openai
# To enable, run: source <(openai complete bash)
# Or add to your .bashrc:
#   which openai > /dev/null && source <(openai complete bash)

_openai_completion() {
    local cur prev words cword
    _init_completion || return

    # Main commands
    local commands="api tools complete"

    # Global options
    local global_opts="-v --verbose -b --api-base -k --api-key -p --proxy -o --organization -t --api-type --api-version --azure-endpoint --azure-ad-token -V --version -h --help"

    if [[ ${cword} -eq 1 ]]; then
        # Completing the first word (main command)
        COMPREPLY=($(compgen -W "${commands} ${global_opts}" -- "${cur}"))
        return
    fi

    case ${words[1]} in
        api)
            # API subcommands
            local api_commands="chat completions models files fine-tuning embeddings audio images moderations assistants threads runs messages"
            if [[ ${cword} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${api_commands}" -- "${cur}"))
            fi
            ;;
        tools)
            # Tools subcommands
            local tools_commands=""
            if [[ ${cword} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${tools_commands}" -- "${cur}"))
            fi
            ;;
        complete)
            # Complete subcommand - shell names
            local shells="bash zsh fish powershell"
            if [[ ${cword} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${shells}" -- "${cur}"))
            fi
            ;;
    esac
}

complete -F _openai_completion openai
'''


# Zsh completion script
ZSH_COMPLETION = r'''#compdef openai
# zsh completion for openai
# To enable, run: source <(openai complete zsh)
# Or add to your .zshrc:
#   which openai > /dev/null && source <(openai complete zsh)

_openai() {
    local -a commands
    commands=(
        'api:Direct API calls'
        'tools:Client side tools for convenience'
        'complete:Generate shell completion scripts'
    )

    local -a global_opts
    global_opts=(
        '-v[Set verbosity]'
        '--verbose[Set verbosity]'
        '-b[What API base url to use]:api_base'
        '--api-base[What API base url to use]:api_base'
        '-k[What API key to use]:api_key'
        '--api-key[What API key to use]:api_key'
        '-p[What proxy to use]:proxy'
        '--proxy[What proxy to use]:proxy'
        '-o[Which organization to run as]:organization'
        '--organization[Which organization to run as]:organization'
        '-t[The backend API to use]:api_type:(openai azure)'
        '--api-type[The backend API to use]:api_type:(openai azure)'
        '--api-version[The Azure API version]:api_version'
        '--azure-endpoint[The Azure endpoint]:azure_endpoint'
        '--azure-ad-token[A token from Azure Active Directory]:azure_ad_token'
        '-V[Show version]'
        '--version[Show version]'
    )

    _arguments -C "${global_opts[@]}" \
        '1: :->cmds' \
        '*::arg:->args'

    case $state in
        cmds)
            _describe 'command' commands
            ;;
        args)
            case $line[1] in
                api)
                    local -a api_commands
                    api_commands=(
                        'chat:Chat completions API'
                        'completions:Completions API'
                        'models:Models API'
                        'files:Files API'
                        'fine-tuning:Fine-tuning API'
                        'embeddings:Embeddings API'
                        'audio:Audio API'
                        'images:Images API'
                        'moderations:Moderations API'
                        'assistants:Assistants API'
                        'threads:Threads API'
                        'runs:Runs API'
                        'messages:Messages API'
                    )
                    _describe 'api command' api_commands
                    ;;
                complete)
                    local -a shells
                    shells=(
                        'bash:Bash completion'
                        'zsh:Zsh completion'
                        'fish:Fish completion'
                        'powershell:PowerShell completion'
                    )
                    _describe 'shell' shells
                    ;;
            esac
            ;;
    esac
}

_openai
'''


# Fish completion script
FISH_COMPLETION = r'''# fish completion for openai
# To enable, run: openai complete fish | source
# Or add to your fish config:
#   which openai > /dev/null; and openai complete fish | source

# Main commands
complete -c openai -f

complete -c openai -n '__fish_use_subcommand' -a 'api' -d 'Direct API calls'
complete -c openai -n '__fish_use_subcommand' -a 'tools' -d 'Client side tools for convenience'
complete -c openai -n '__fish_use_subcommand' -a 'complete' -d 'Generate shell completion scripts'

# Global options
complete -c openai -s v -l verbose -d 'Set verbosity'
complete -c openai -s b -l api-base -d 'What API base url to use'
complete -c openai -s k -l api-key -d 'What API key to use'
complete -c openai -s p -l proxy -d 'What proxy to use'
complete -c openai -s o -l organization -d 'Which organization to run as'
complete -c openai -s t -l api-type -d 'The backend API to use' -xa 'openai azure'
complete -c openai -l api-version -d 'The Azure API version'
complete -c openai -l azure-endpoint -d 'The Azure endpoint'
complete -c openai -l azure-ad-token -d 'A token from Azure Active Directory'
complete -c openai -s V -l version -d 'Show version'

# complete subcommand
complete -c openai -n '__fish_seen_subcommand_from complete' -a 'bash' -d 'Bash completion'
complete -c openai -n '__fish_seen_subcommand_from complete' -a 'zsh' -d 'Zsh completion'
complete -c openai -n '__fish_seen_subcommand_from complete' -a 'fish' -d 'Fish completion'
complete -c openai -n '__fish_seen_subcommand_from complete' -a 'powershell' -d 'PowerShell completion'
'''


# PowerShell completion script
POWERSHELL_COMPLETION = r'''# PowerShell completion for openai
# To enable, run: openai complete powershell | Out-String | Invoke-Expression
# Or add to your PowerShell profile:
#   if (Get-Command openai -ErrorAction SilentlyContinue) {
#       openai complete powershell | Out-String | Invoke-Expression
#   }

using namespace System.Management.Automation
using namespace System.Management.Automation.Language

Register-ArgumentCompleter -Native -CommandName openai -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $commandElements = $commandAst.CommandElements
    $command = @(
        'complete'
        for ($i = 1; $i -lt $commandElements.Count; $i++) {
            $element = $commandElements[$i]
            if ($element -isnot [StringConstantExpressionAst]) {
                break
            }
            if ($element.Value.StartsWith('-')) {
                break
            }
            $element.Value
        }
    ) -join ';'

    $completions = @(
        # Main commands
        [CompletionResult]::new('api', 'api', [CompletionResultType]::Command, 'Direct API calls')
        [CompletionResult]::new('tools', 'tools', [CompletionResultType]::Command, 'Client side tools for convenience')
        [CompletionResult]::new('complete', 'complete', [CompletionResultType]::Command, 'Generate shell completion scripts')
    )

    if ($command -eq 'complete') {
        $completions = @(
            [CompletionResult]::new('bash', 'bash', [CompletionResultType]::ParameterValue, 'Bash completion')
            [CompletionResult]::new('zsh', 'zsh', [CompletionResultType]::ParameterValue, 'Zsh completion')
            [CompletionResult]::new('fish', 'fish', [CompletionResultType]::ParameterValue, 'Fish completion')
            [CompletionResult]::new('powershell', 'powershell', [CompletionResultType]::ParameterValue, 'PowerShell completion')
        )
    }

    $completions.Where{ $_.CompletionText -like "$wordToComplete*" } |
        Sort-Object -Property ListItemText
}
'''
