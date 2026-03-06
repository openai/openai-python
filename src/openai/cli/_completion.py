"""Shell completion support for the OpenAI CLI."""

from __future__ import annotations

import sys
import argparse
from typing import Optional

BASH_COMPLETION = '''
_openai_completion() {
    local cur prev words cword
    _init_completion || return

    local commands="api tools"
    local api_commands="chat completions models files audio fine_tuning"
    local tools_commands="migrate fine_tunes.prepare_data"

    case "${COMP_CWORD}" in
        1)
            COMPREPLY=($(compgen -W "${commands}" -- "${cur}"))
            ;;
        2)
            case "${prev}" in
                api)
                    COMPREPLY=($(compgen -W "${api_commands}" -- "${cur}"))
                    ;;
                tools)
                    COMPREPLY=($(compgen -W "${tools_commands}" -- "${cur}"))
                    ;;
            esac
            ;;
        3)
            case "${words[1]}" in
                api)
                    case "${prev}" in
                        chat)
                            COMPREPLY=($(compgen -W "completions" -- "${cur}"))
                            ;;
                        fine_tuning)
                            COMPREPLY=($(compgen -W "jobs" -- "${cur}"))
                            ;;
                    esac
                    ;;
            esac
            ;;
    esac

    # Global options
    if [[ "${cur}" == -* ]]; then
        COMPREPLY=($(compgen -W "-h --help -v --verbose -b --api-base -k --api-key -p --proxy -o --organization -t --api-type --api-version --azure-endpoint --azure-ad-token -V --version" -- "${cur}"))
    fi
}

complete -F _openai_completion openai
'''

ZSH_COMPLETION = '''
#compdef openai

_openai() {
    local -a commands api_commands tools_commands

    commands=(
        'api:Direct API calls'
        'tools:Client side tools for convenience'
    )

    api_commands=(
        'chat:Chat completions'
        'completions:Text completions'
        'models:List and manage models'
        'files:Upload and manage files'
        'audio:Audio transcription and translation'
        'fine_tuning:Fine-tuning jobs'
    )

    tools_commands=(
        'migrate:Migrate from older API versions'
        'fine_tunes.prepare_data:Prepare data for fine-tuning'
    )

    _arguments -C \\
        '-h[Show help]' \\
        '--help[Show help]' \\
        '-v[Set verbosity]' \\
        '--verbose[Set verbosity]' \\
        '-b[API base URL]:url:' \\
        '--api-base[API base URL]:url:' \\
        '-k[API key]:key:' \\
        '--api-key[API key]:key:' \\
        '-p[Proxy URL]:proxy:' \\
        '--proxy[Proxy URL]:proxy:' \\
        '-o[Organization]:org:' \\
        '--organization[Organization]:org:' \\
        '-t[API type]:type:(openai azure)' \\
        '--api-type[API type]:type:(openai azure)' \\
        '--api-version[Azure API version]:version:' \\
        '--azure-endpoint[Azure endpoint]:endpoint:' \\
        '--azure-ad-token[Azure AD token]:token:' \\
        '-V[Show version]' \\
        '--version[Show version]' \\
        '1: :->command' \\
        '2: :->subcommand' \\
        '3: :->action' \\
        '*::arg:->args'

    case "$state" in
        command)
            _describe -t commands 'openai commands' commands
            ;;
        subcommand)
            case "${words[2]}" in
                api)
                    _describe -t api_commands 'api commands' api_commands
                    ;;
                tools)
                    _describe -t tools_commands 'tools commands' tools_commands
                    ;;
            esac
            ;;
        action)
            case "${words[2]}" in
                api)
                    case "${words[3]}" in
                        chat)
                            _describe -t actions 'chat actions' '(completions:Create chat completion)'
                            ;;
                        fine_tuning)
                            _describe -t actions 'fine_tuning actions' '(jobs:Manage fine-tuning jobs)'
                            ;;
                    esac
                    ;;
            esac
            ;;
    esac
}

_openai "$@"
'''

FISH_COMPLETION = '''
# Fish shell completion for openai CLI

# Disable file completion by default
complete -c openai -f

# Main commands
complete -c openai -n "__fish_use_subcommand" -a "api" -d "Direct API calls"
complete -c openai -n "__fish_use_subcommand" -a "tools" -d "Client side tools for convenience"

# Global options
complete -c openai -s h -l help -d "Show help"
complete -c openai -s v -l verbose -d "Set verbosity"
complete -c openai -s b -l api-base -d "API base URL" -r
complete -c openai -s k -l api-key -d "API key" -r
complete -c openai -s p -l proxy -d "Proxy URL" -r
complete -c openai -s o -l organization -d "Organization" -r
complete -c openai -s t -l api-type -d "API type" -a "openai azure"
complete -c openai -l api-version -d "Azure API version" -r
complete -c openai -l azure-endpoint -d "Azure endpoint" -r
complete -c openai -l azure-ad-token -d "Azure AD token" -r
complete -c openai -s V -l version -d "Show version"

# API subcommands
complete -c openai -n "__fish_seen_subcommand_from api" -a "chat" -d "Chat completions"
complete -c openai -n "__fish_seen_subcommand_from api" -a "completions" -d "Text completions"
complete -c openai -n "__fish_seen_subcommand_from api" -a "models" -d "List and manage models"
complete -c openai -n "__fish_seen_subcommand_from api" -a "files" -d "Upload and manage files"
complete -c openai -n "__fish_seen_subcommand_from api" -a "audio" -d "Audio transcription and translation"
complete -c openai -n "__fish_seen_subcommand_from api" -a "fine_tuning" -d "Fine-tuning jobs"

# Tools subcommands
complete -c openai -n "__fish_seen_subcommand_from tools" -a "migrate" -d "Migrate from older API versions"
complete -c openai -n "__fish_seen_subcommand_from tools" -a "fine_tunes.prepare_data" -d "Prepare data for fine-tuning"

# Chat subcommands
complete -c openai -n "__fish_seen_subcommand_from chat" -a "completions" -d "Create chat completion"

# Fine-tuning subcommands
complete -c openai -n "__fish_seen_subcommand_from fine_tuning" -a "jobs" -d "Manage fine-tuning jobs"
'''

POWERSHELL_COMPLETION = '''
# PowerShell completion for openai CLI

$script:openaiCommands = @{
    'api' = @{
        'chat' = @('completions')
        'completions' = @()
        'models' = @('list', 'delete')
        'files' = @('create', 'list', 'delete')
        'audio' = @('transcriptions', 'translations')
        'fine_tuning' = @{
            'jobs' = @('create', 'list', 'cancel')
        }
    }
    'tools' = @('migrate', 'fine_tunes.prepare_data')
}

Register-ArgumentCompleter -Native -CommandName openai -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $commands = $commandAst.CommandElements
    $numCommands = $commands.Count

    # Global options
    $globalOptions = @(
        '-h', '--help',
        '-v', '--verbose',
        '-b', '--api-base',
        '-k', '--api-key',
        '-p', '--proxy',
        '-o', '--organization',
        '-t', '--api-type',
        '--api-version',
        '--azure-endpoint',
        '--azure-ad-token',
        '-V', '--version'
    )

    if ($wordToComplete -like '-*') {
        $globalOptions | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterName', $_)
        }
        return
    }

    switch ($numCommands) {
        1 {
            @('api', 'tools') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                [System.Management.Automation.CompletionResult]::new($_, $_, 'Command', $_)
            }
        }
        2 {
            $mainCmd = $commands[1].ToString()
            if ($script:openaiCommands.ContainsKey($mainCmd)) {
                $subCmds = $script:openaiCommands[$mainCmd]
                if ($subCmds -is [hashtable]) {
                    $subCmds.Keys | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                        [System.Management.Automation.CompletionResult]::new($_, $_, 'Command', $_)
                    }
                } else {
                    $subCmds | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                        [System.Management.Automation.CompletionResult]::new($_, $_, 'Command', $_)
                    }
                }
            }
        }
    }
}
'''


def get_completion_script(shell: str) -> str:
    """Get the completion script for the specified shell.

    Args:
        shell: The shell type ('bash', 'zsh', 'fish', or 'powershell')

    Returns:
        The completion script as a string

    Raises:
        ValueError: If the shell type is not supported
    """
    scripts = {
        'bash': BASH_COMPLETION,
        'zsh': ZSH_COMPLETION,
        'fish': FISH_COMPLETION,
        'powershell': POWERSHELL_COMPLETION,
    }

    if shell not in scripts:
        raise ValueError(
            f"Unsupported shell: {shell}. "
            f"Supported shells: {', '.join(scripts.keys())}"
        )

    return scripts[shell].strip()


def print_completion(shell: str) -> None:
    """Print the completion script for the specified shell.

    Args:
        shell: The shell type
    """
    print(get_completion_script(shell))


class CompletionArgs:
    """Arguments for the completion command."""

    shell: str


def register_completion_command(parser: argparse.ArgumentParser) -> None:
    """Register the completion subcommand.

    Args:
        parser: The argument parser to add the completion command to
    """
    completion_parser = parser.add_parser(
        'completion',
        help='Generate shell completion scripts'
    )
    completion_parser.add_argument(
        'shell',
        choices=['bash', 'zsh', 'fish', 'powershell'],
        help='Shell type for completion script'
    )
    completion_parser.set_defaults(func=lambda args: print_completion(args.shell))
