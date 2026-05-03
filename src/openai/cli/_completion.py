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
            # API subcommands - use full command names as registered in CLI
            local api_commands="chat.completions.create completions.create models.list models.retrieve models.delete files.create files.list files.retrieve files.delete images.generate images.edit images.create_variation audio.transcriptions.create audio.translations.create fine_tuning.jobs.create fine_tuning.jobs.list fine_tuning.jobs.retrieve fine_tuning.jobs.cancel fine_tuning.jobs.list_events"
            COMPREPLY=($(compgen -W "${api_commands}" -- "${cur}"))
            ;;
        tools)
            # Tools subcommands
            local tools_commands="fine_tunes.prepare_data migrate grit"
            COMPREPLY=($(compgen -W "${tools_commands}" -- "${cur}"))
            ;;
        complete)
            # Complete subcommand - shell names
            local shells="bash zsh fish powershell"
            COMPREPLY=($(compgen -W "${shells}" -- "${cur}"))
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
                        'chat.completions.create:Create chat completion'
                        'completions.create:Create completion'
                        'models.list:List models'
                        'models.retrieve:Retrieve model'
                        'models.delete:Delete model'
                        'files.create:Create file'
                        'files.list:List files'
                        'files.retrieve:Retrieve file'
                        'files.delete:Delete file'
                        'images.generate:Generate image'
                        'images.edit:Edit image'
                        'images.create_variation:Create image variation'
                        'audio.transcriptions.create:Create transcription'
                        'audio.translations.create:Create translation'
                        'fine_tuning.jobs.create:Create fine-tuning job'
                        'fine_tuning.jobs.list:List fine-tuning jobs'
                        'fine_tuning.jobs.retrieve:Retrieve fine-tuning job'
                        'fine_tuning.jobs.cancel:Cancel fine-tuning job'
                        'fine_tuning.jobs.list_events:List fine-tuning job events'
                    )
                    _describe 'api command' api_commands
                    ;;
                tools)
                    local -a tools_commands
                    tools_commands=(
                        'fine_tunes.prepare_data:Prepare data for fine-tuning'
                        'migrate:Migrate to new API version'
                        'grit:Run grit'
                    )
                    _describe 'tools command' tools_commands
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

# api subcommands
complete -c openai -n '__fish_seen_subcommand_from api' -a 'chat.completions.create' -d 'Create chat completion'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'completions.create' -d 'Create completion'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'models.list' -d 'List models'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'models.retrieve' -d 'Retrieve model'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'models.delete' -d 'Delete model'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'files.create' -d 'Create file'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'files.list' -d 'List files'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'files.retrieve' -d 'Retrieve file'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'files.delete' -d 'Delete file'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'images.generate' -d 'Generate image'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'images.edit' -d 'Edit image'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'images.create_variation' -d 'Create image variation'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'audio.transcriptions.create' -d 'Create transcription'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'audio.translations.create' -d 'Create translation'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'fine_tuning.jobs.create' -d 'Create fine-tuning job'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'fine_tuning.jobs.list' -d 'List fine-tuning jobs'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'fine_tuning.jobs.retrieve' -d 'Retrieve fine-tuning job'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'fine_tuning.jobs.cancel' -d 'Cancel fine-tuning job'
complete -c openai -n '__fish_seen_subcommand_from api' -a 'fine_tuning.jobs.list_events' -d 'List fine-tuning job events'

# tools subcommands
complete -c openai -n '__fish_seen_subcommand_from tools' -a 'fine_tunes.prepare_data' -d 'Prepare data for fine-tuning'
complete -c openai -n '__fish_seen_subcommand_from tools' -a 'migrate' -d 'Migrate to new API version'
complete -c openai -n '__fish_seen_subcommand_from tools' -a 'grit' -d 'Run grit'

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

    # Get the subcommand (second element if present)
    $subcommand = if ($commandElements.Count -ge 2) { $commandElements[1].Value } else { '' }

    $completions = @(
        # Main commands
        [CompletionResult]::new('api', 'api', [CompletionResultType]::Command, 'Direct API calls')
        [CompletionResult]::new('tools', 'tools', [CompletionResultType]::Command, 'Client side tools for convenience')
        [CompletionResult]::new('complete', 'complete', [CompletionResultType]::Command, 'Generate shell completion scripts')
    )

    if ($subcommand -eq 'api') {
        $completions = @(
            [CompletionResult]::new('chat.completions.create', 'chat.completions.create', [CompletionResultType]::ParameterValue, 'Create chat completion')
            [CompletionResult]::new('completions.create', 'completions.create', [CompletionResultType]::ParameterValue, 'Create completion')
            [CompletionResult]::new('models.list', 'models.list', [CompletionResultType]::ParameterValue, 'List models')
            [CompletionResult]::new('models.retrieve', 'models.retrieve', [CompletionResultType]::ParameterValue, 'Retrieve model')
            [CompletionResult]::new('models.delete', 'models.delete', [CompletionResultType]::ParameterValue, 'Delete model')
            [CompletionResult]::new('files.create', 'files.create', [CompletionResultType]::ParameterValue, 'Create file')
            [CompletionResult]::new('files.list', 'files.list', [CompletionResultType]::ParameterValue, 'List files')
            [CompletionResult]::new('files.retrieve', 'files.retrieve', [CompletionResultType]::ParameterValue, 'Retrieve file')
            [CompletionResult]::new('files.delete', 'files.delete', [CompletionResultType]::ParameterValue, 'Delete file')
            [CompletionResult]::new('images.generate', 'images.generate', [CompletionResultType]::ParameterValue, 'Generate image')
            [CompletionResult]::new('images.edit', 'images.edit', [CompletionResultType]::ParameterValue, 'Edit image')
            [CompletionResult]::new('images.create_variation', 'images.create_variation', [CompletionResultType]::ParameterValue, 'Create image variation')
            [CompletionResult]::new('audio.transcriptions.create', 'audio.transcriptions.create', [CompletionResultType]::ParameterValue, 'Create transcription')
            [CompletionResult]::new('audio.translations.create', 'audio.translations.create', [CompletionResultType]::ParameterValue, 'Create translation')
            [CompletionResult]::new('fine_tuning.jobs.create', 'fine_tuning.jobs.create', [CompletionResultType]::ParameterValue, 'Create fine-tuning job')
            [CompletionResult]::new('fine_tuning.jobs.list', 'fine_tuning.jobs.list', [CompletionResultType]::ParameterValue, 'List fine-tuning jobs')
            [CompletionResult]::new('fine_tuning.jobs.retrieve', 'fine_tuning.jobs.retrieve', [CompletionResultType]::ParameterValue, 'Retrieve fine-tuning job')
            [CompletionResult]::new('fine_tuning.jobs.cancel', 'fine_tuning.jobs.cancel', [CompletionResultType]::ParameterValue, 'Cancel fine-tuning job')
            [CompletionResult]::new('fine_tuning.jobs.list_events', 'fine_tuning.jobs.list_events', [CompletionResultType]::ParameterValue, 'List fine-tuning job events')
        )
    } elseif ($subcommand -eq 'tools') {
        $completions = @(
            [CompletionResult]::new('fine_tunes.prepare_data', 'fine_tunes.prepare_data', [CompletionResultType]::ParameterValue, 'Prepare data for fine-tuning')
            [CompletionResult]::new('migrate', 'migrate', [CompletionResultType]::ParameterValue, 'Migrate to new API version')
            [CompletionResult]::new('grit', 'grit', [CompletionResultType]::ParameterValue, 'Run grit')
        )
    } elseif ($subcommand -eq 'complete') {
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
