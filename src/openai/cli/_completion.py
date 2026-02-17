"""Shell completion script generator for OpenAI CLI.

Generates completion scripts for bash, zsh, fish, and PowerShell.
Usage: openai completion <shell>

Author: Ahmed Adel Bakr Alderai
"""

from __future__ import annotations

import sys
import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


BASH_COMPLETION = '''# OpenAI CLI Bash Completion
# Add to ~/.bashrc: eval "$(openai completion bash)"

_openai_completions() {
    local cur prev words cword
    _init_completion || return

    local commands="api tools completion"
    local api_commands="chat.completions.create models.list models.retrieve files.create files.list files.retrieve files.delete files.content audio.transcriptions.create audio.translations.create images.generate images.edit images.create_variation embeddings.create moderations.create"
    local tools_commands="fine_tunes.prepare_data"
    local global_opts="-v --verbose -b --api-base -k --api-key -p --proxy -o --organization -t --api-type --api-version --azure-endpoint --azure-ad-token -V --version -h --help"

    case "${prev}" in
        openai)
            COMPREPLY=($(compgen -W "${commands} ${global_opts}" -- "${cur}"))
            return 0
            ;;
        api)
            COMPREPLY=($(compgen -W "${api_commands}" -- "${cur}"))
            return 0
            ;;
        tools)
            COMPREPLY=($(compgen -W "${tools_commands}" -- "${cur}"))
            return 0
            ;;
        completion)
            COMPREPLY=($(compgen -W "bash zsh fish powershell" -- "${cur}"))
            return 0
            ;;
        -t|--api-type)
            COMPREPLY=($(compgen -W "openai azure" -- "${cur}"))
            return 0
            ;;
        -k|--api-key|-b|--api-base|-o|--organization|--api-version|--azure-endpoint|--azure-ad-token|-p|--proxy)
            # These require user input, no completion
            return 0
            ;;
    esac

    if [[ "${cur}" == -* ]]; then
        COMPREPLY=($(compgen -W "${global_opts}" -- "${cur}"))
        return 0
    fi

    COMPREPLY=($(compgen -W "${commands}" -- "${cur}"))
}

complete -F _openai_completions openai
'''

ZSH_COMPLETION = '''#compdef openai
# OpenAI CLI Zsh Completion
# Add to ~/.zshrc: eval "$(openai completion zsh)"

_openai() {
    local -a commands api_commands tools_commands shells

    commands=(
        'api:Direct API calls'
        'tools:Client side tools for convenience'
        'completion:Generate shell completion scripts'
    )

    api_commands=(
        'chat.completions.create:Create a chat completion'
        'models.list:List available models'
        'models.retrieve:Retrieve a model'
        'files.create:Upload a file'
        'files.list:List files'
        'files.retrieve:Retrieve a file'
        'files.delete:Delete a file'
        'files.content:Get file content'
        'audio.transcriptions.create:Transcribe audio'
        'audio.translations.create:Translate audio'
        'images.generate:Generate images'
        'images.edit:Edit images'
        'images.create_variation:Create image variations'
        'embeddings.create:Create embeddings'
        'moderations.create:Create moderation'
    )

    tools_commands=(
        'fine_tunes.prepare_data:Prepare data for fine-tuning'
    )

    shells=(
        'bash:Generate Bash completion script'
        'zsh:Generate Zsh completion script'
        'fish:Generate Fish completion script'
        'powershell:Generate PowerShell completion script'
    )

    _arguments -C \\
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
        '*::arg:->args'

    case "$state" in
        command)
            _describe -t commands 'openai commands' commands
            ;;
        subcommand)
            case "$words[2]" in
                api)
                    _describe -t api_commands 'api commands' api_commands
                    ;;
                tools)
                    _describe -t tools_commands 'tools commands' tools_commands
                    ;;
                completion)
                    _describe -t shells 'shells' shells
                    ;;
            esac
            ;;
    esac
}

_openai "$@"
'''

FISH_COMPLETION = '''# OpenAI CLI Fish Completion
# Save to ~/.config/fish/completions/openai.fish

# Disable file completion by default
complete -c openai -f

# Global options
complete -c openai -s v -l verbose -d "Set verbosity"
complete -c openai -s b -l api-base -d "API base URL" -r
complete -c openai -s k -l api-key -d "API key" -r
complete -c openai -s p -l proxy -d "Proxy URL" -r
complete -c openai -s o -l organization -d "Organization" -r
complete -c openai -s t -l api-type -d "API type" -ra "openai azure"
complete -c openai -l api-version -d "Azure API version" -r
complete -c openai -l azure-endpoint -d "Azure endpoint" -r
complete -c openai -l azure-ad-token -d "Azure AD token" -r
complete -c openai -s V -l version -d "Show version"
complete -c openai -s h -l help -d "Show help"

# Main commands
complete -c openai -n "__fish_use_subcommand" -a "api" -d "Direct API calls"
complete -c openai -n "__fish_use_subcommand" -a "tools" -d "Client side tools"
complete -c openai -n "__fish_use_subcommand" -a "completion" -d "Generate shell completion"

# API subcommands
complete -c openai -n "__fish_seen_subcommand_from api" -a "chat.completions.create" -d "Create chat completion"
complete -c openai -n "__fish_seen_subcommand_from api" -a "models.list" -d "List models"
complete -c openai -n "__fish_seen_subcommand_from api" -a "models.retrieve" -d "Retrieve model"
complete -c openai -n "__fish_seen_subcommand_from api" -a "files.create" -d "Upload file"
complete -c openai -n "__fish_seen_subcommand_from api" -a "files.list" -d "List files"
complete -c openai -n "__fish_seen_subcommand_from api" -a "files.retrieve" -d "Retrieve file"
complete -c openai -n "__fish_seen_subcommand_from api" -a "files.delete" -d "Delete file"
complete -c openai -n "__fish_seen_subcommand_from api" -a "files.content" -d "Get file content"
complete -c openai -n "__fish_seen_subcommand_from api" -a "audio.transcriptions.create" -d "Transcribe audio"
complete -c openai -n "__fish_seen_subcommand_from api" -a "audio.translations.create" -d "Translate audio"
complete -c openai -n "__fish_seen_subcommand_from api" -a "images.generate" -d "Generate images"
complete -c openai -n "__fish_seen_subcommand_from api" -a "images.edit" -d "Edit images"
complete -c openai -n "__fish_seen_subcommand_from api" -a "images.create_variation" -d "Create variations"
complete -c openai -n "__fish_seen_subcommand_from api" -a "embeddings.create" -d "Create embeddings"
complete -c openai -n "__fish_seen_subcommand_from api" -a "moderations.create" -d "Create moderation"

# Tools subcommands
complete -c openai -n "__fish_seen_subcommand_from tools" -a "fine_tunes.prepare_data" -d "Prepare fine-tuning data"

# Completion subcommands
complete -c openai -n "__fish_seen_subcommand_from completion" -a "bash" -d "Bash completion"
complete -c openai -n "__fish_seen_subcommand_from completion" -a "zsh" -d "Zsh completion"
complete -c openai -n "__fish_seen_subcommand_from completion" -a "fish" -d "Fish completion"
complete -c openai -n "__fish_seen_subcommand_from completion" -a "powershell" -d "PowerShell completion"
'''

POWERSHELL_COMPLETION = '''# OpenAI CLI PowerShell Completion
# Add to $PROFILE: . (openai completion powershell | Out-String)

Register-ArgumentCompleter -Native -CommandName openai -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $commands = @{
        'openai' = @('api', 'tools', 'completion', '-v', '--verbose', '-b', '--api-base', '-k', '--api-key', '-p', '--proxy', '-o', '--organization', '-t', '--api-type', '--api-version', '--azure-endpoint', '--azure-ad-token', '-V', '--version', '-h', '--help')
        'api' = @('chat.completions.create', 'models.list', 'models.retrieve', 'files.create', 'files.list', 'files.retrieve', 'files.delete', 'files.content', 'audio.transcriptions.create', 'audio.translations.create', 'images.generate', 'images.edit', 'images.create_variation', 'embeddings.create', 'moderations.create')
        'tools' = @('fine_tunes.prepare_data')
        'completion' = @('bash', 'zsh', 'fish', 'powershell')
    }

    $elements = $commandAst.CommandElements
    $command = 'openai'

    for ($i = 1; $i -lt $elements.Count; $i++) {
        $element = $elements[$i].Extent.Text
        if ($commands.ContainsKey($element)) {
            $command = $element
        }
    }

    $completions = $commands[$command]

    $completions | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}
'''


def get_completion_script(shell: str) -> str:
    """Get the completion script for the specified shell."""
    scripts = {
        "bash": BASH_COMPLETION,
        "zsh": ZSH_COMPLETION,
        "fish": FISH_COMPLETION,
        "powershell": POWERSHELL_COMPLETION,
    }

    if shell not in scripts:
        raise ValueError(f"Unsupported shell: {shell}. Supported: {', '.join(scripts.keys())}")

    return scripts[shell]


def completion_command(args: argparse.Namespace) -> None:
    """Handle the completion subcommand."""
    script = get_completion_script(args.shell)
    sys.stdout.write(script)


def register_completion_command(subparsers: argparse._SubParsersAction) -> None:
    """Register the completion subcommand."""
    parser = subparsers.add_parser(
        "completion",
        help="Generate shell completion scripts",
        description="Generate shell completion scripts for bash, zsh, fish, or powershell.",
    )
    parser.add_argument(
        "shell",
        choices=["bash", "zsh", "fish", "powershell"],
        help="The shell to generate completion for",
    )

    parser.set_defaults(func=completion_command)
