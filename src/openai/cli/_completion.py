"""
Shell autocomplete generation for openai CLI.

Generates completion scripts for bash, zsh, fish, and PowerShell.
"""

from __future__ import annotations

import sys
from typing import TextIO


BASH_COMPLETION = """
# openai completion script for bash

_openai_completion() {
    local cur prev opts base
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Top-level commands
    opts="api chat audio models files fine-tuning embeddings images completions completion --help --version"
    
    # API-related subcommands
    api_cmds="chat.completions.create audio.speech.create audio.transcriptions.create audio.translations.create"
    
    # Common flags
    flags="--api-key --organization --api-base --api-version --timeout --max-retries"
    
    case "${prev}" in
        openai)
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        api)
            COMPREPLY=( $(compgen -W "${api_cmds}" -- ${cur}) )
            return 0
            ;;
        --api-key|--organization|--api-base|--api-version|--timeout|--max-retries)
            # No completion for values
            return 0
            ;;
        *)
            ;;
    esac
    
    COMPREPLY=( $(compgen -W "${opts} ${flags}" -- ${cur}) )
    return 0
}

complete -F _openai_completion openai
"""

ZSH_COMPLETION = """
#compdef openai

# openai completion script for zsh

_openai() {
    local -a commands
    commands=(
        'api:Direct API access'
        'chat:Chat completions'
        'audio:Audio generation and transcription'
        'models:List and retrieve models'
        'files:File operations'
        'fine-tuning:Fine-tuning operations'
        'embeddings:Create embeddings'
        'images:Image generation and manipulation'
        'completions:Text completions'
        'completion:Generate shell completion scripts'
    )
    
    local -a options
    options=(
        '--help:Show help message'
        '--version:Show version'
        '--api-key:OpenAI API key'
        '--organization:Organization ID'
        '--api-base:API base URL'
        '--api-version:API version'
        '--timeout:Request timeout'
        '--max-retries:Maximum retry attempts'
    )
    
    _arguments -C \\
        '1: :->command' \\
        '*::arg:->args'
    
    case $state in
        command)
            _describe 'openai commands' commands
            _describe 'options' options
            ;;
        args)
            case ${words[1]} in
                api)
                    _values 'api operations' \\
                        'chat.completions.create' \\
                        'audio.speech.create' \\
                        'audio.transcriptions.create' \\
                        'audio.translations.create' \\
                        'models.list' \\
                        'files.create' \\
                        'files.list'
                    ;;
                completion)
                    _values 'shells' 'bash' 'zsh' 'fish' 'powershell'
                    ;;
            esac
            ;;
    esac
}

_openai "$@"
"""

FISH_COMPLETION = """
# openai completion script for fish

# Top-level commands
complete -c openai -n "__fish_use_subcommand" -a "api" -d "Direct API access"
complete -c openai -n "__fish_use_subcommand" -a "chat" -d "Chat completions"
complete -c openai -n "__fish_use_subcommand" -a "audio" -d "Audio operations"
complete -c openai -n "__fish_use_subcommand" -a "models" -d "Model operations"
complete -c openai -n "__fish_use_subcommand" -a "files" -d "File operations"
complete -c openai -n "__fish_use_subcommand" -a "fine-tuning" -d "Fine-tuning"
complete -c openai -n "__fish_use_subcommand" -a "embeddings" -d "Embeddings"
complete -c openai -n "__fish_use_subcommand" -a "images" -d "Image generation"
complete -c openai -n "__fish_use_subcommand" -a "completions" -d "Text completions"
complete -c openai -n "__fish_use_subcommand" -a "completion" -d "Generate completion script"

# Global options
complete -c openai -l help -d "Show help message"
complete -c openai -l version -d "Show version"
complete -c openai -l api-key -d "OpenAI API key"
complete -c openai -l organization -d "Organization ID"
complete -c openai -l api-base -d "API base URL"
complete -c openai -l api-version -d "API version"
complete -c openai -l timeout -d "Request timeout"
complete -c openai -l max-retries -d "Maximum retry attempts"

# Completion subcommand
complete -c openai -n "__fish_seen_subcommand_from completion" -a "bash zsh fish powershell" -d "Shell type"
"""

POWERSHELL_COMPLETION = """
# openai completion script for PowerShell

Register-ArgumentCompleter -Native -CommandName openai -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    
    $commands = @(
        [CompletionResult]::new('api', 'api', [CompletionResultType]::ParameterValue, 'Direct API access')
        [CompletionResult]::new('chat', 'chat', [CompletionResultType]::ParameterValue, 'Chat completions')
        [CompletionResult]::new('audio', 'audio', [CompletionResultType]::ParameterValue, 'Audio operations')
        [CompletionResult]::new('models', 'models', [CompletionResultType]::ParameterValue, 'Model operations')
        [CompletionResult]::new('files', 'files', [CompletionResultType]::ParameterValue, 'File operations')
        [CompletionResult]::new('fine-tuning', 'fine-tuning', [CompletionResultType]::ParameterValue, 'Fine-tuning')
        [CompletionResult]::new('embeddings', 'embeddings', [CompletionResultType]::ParameterValue, 'Embeddings')
        [CompletionResult]::new('images', 'images', [CompletionResultType]::ParameterValue, 'Image generation')
        [CompletionResult]::new('completions', 'completions', [CompletionResultType]::ParameterValue, 'Text completions')
        [CompletionResult]::new('completion', 'completion', [CompletionResultType]::ParameterValue, 'Generate completion script')
        [CompletionResult]::new('--help', '--help', [CompletionResultType]::ParameterName, 'Show help')
        [CompletionResult]::new('--version', '--version', [CompletionResultType]::ParameterName, 'Show version')
        [CompletionResult]::new('--api-key', '--api-key', [CompletionResultType]::ParameterName, 'API key')
        [CompletionResult]::new('--organization', '--organization', [CompletionResultType]::ParameterName, 'Organization')
    )
    
    $commands | Where-Object { $_.CompletionText -like "$wordToComplete*" }
}
"""


def generate_completion(shell: str, output: TextIO = sys.stdout) -> None:
    """Generate completion script for the specified shell."""
    shell = shell.lower()
    
    if shell == "bash":
        output.write(BASH_COMPLETION)
    elif shell == "zsh":
        output.write(ZSH_COMPLETION)
    elif shell == "fish":
        output.write(FISH_COMPLETION)
    elif shell == "powershell":
        output.write(POWERSHELL_COMPLETION)
    else:
        raise ValueError(f"Unsupported shell: {shell}. Supported: bash, zsh, fish, powershell")


def print_installation_instructions(shell: str) -> None:
    """Print installation instructions for the completion script."""
    shell = shell.lower()
    
    instructions = {
        "bash": """
To enable bash completion, add this to your ~/.bashrc:
    eval "$(openai completion bash)"

Or save the completion script:
    openai completion bash > ~/.openai-completion.bash
    echo 'source ~/.openai-completion.bash' >> ~/.bashrc
""",
        "zsh": """
To enable zsh completion, add this to your ~/.zshrc:
    eval "$(openai completion zsh)"

Or save the completion script to your fpath:
    openai completion zsh > ~/.zsh/completions/_openai
    # Add to ~/.zshrc: fpath=(~/.zsh/completions $fpath)
""",
        "fish": """
To enable fish completion:
    openai completion fish > ~/.config/fish/completions/openai.fish

The completion will be loaded automatically in new fish sessions.
""",
        "powershell": """
To enable PowerShell completion, add this to your profile:
    openai completion powershell | Out-String | Invoke-Expression

Or save and source it:
    openai completion powershell > ~\\Documents\\PowerShell\\openai-completion.ps1
    # Add to profile: . ~\\Documents\\PowerShell\\openai-completion.ps1
"""
    }
    
    sys.stderr.write(instructions.get(shell, ""))
