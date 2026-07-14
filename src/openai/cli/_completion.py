"""Shell completion support for the OpenAI CLI.

Provides shell completion scripts for bash, zsh, fish, and powershell.
"""

import sys
from typing import Optional


def get_bash_completion() -> str:
    """Generate bash completion script for the openai command."""
    return '''#!/bin/bash
_openai_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="--help --version --api-key --api-base --organization --proxy api tools"
    
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}

complete -o bashdefault -o default -o nospace -F _openai_completion openai
'''


def get_zsh_completion() -> str:
    """Generate zsh completion script for the openai command."""
    return '''#compdef openai

_openai() {
  local -a subcmds
  subcmds=(
    "api:Direct API calls"
    "tools:Client side tools for convenience"
  )

  local -a opts
  opts=(
    "-v --verbose:Set verbosity level"
    "-k --api-key:API key for authentication"
    "-b --api-base:Base URL for API"
    "-o --organization:Organization to run as"
    "-t --api-type:Backend API type (openai or azure)"
    "--api-version:Azure API version"
    "--azure-endpoint:Azure endpoint URL"
    "--azure-ad-token:Azure AD token"
    "-V --version:Show version and exit"
    "-h --help:Show help message"
  )

  _arguments -s -S $opts "*::subcmd:($subcmds)"
}

_openai
'''


def get_fish_completion() -> str:
    """Generate fish completion script for the openai command."""
    return '''complete -c openai -f
complete -c openai -n "__fish_use_subcommand_from_list api tools" -a api -d "Direct API calls"
complete -c openai -n "__fish_use_subcommand_from_list api tools" -a tools -d "Client side tools"

complete -c openai -s v -l verbose -d "Set verbosity"
complete -c openai -s k -l api-key -d "API key"
complete -c openai -s b -l api-base -d "Base URL"
complete -c openai -s o -l organization -d "Organization"
complete -c openai -s t -l api-type -d "Backend API type"
complete -c openai -l api-version -d "Azure API version"
complete -c openai -l azure-endpoint -d "Azure endpoint"
complete -c openai -l azure-ad-token -d "Azure AD token"
complete -c openai -s V -l version -d "Show version"
complete -c openai -s h -l help -d "Show help"
'''


def get_powershell_completion() -> str:
    """Generate PowerShell completion script for the openai command."""
    return '''$openaiCompleter = {
    param($wordToComplete, $commandAst, $cursorPosition)
    
    $opts = @(
        '--help', '--version', '--api-key', '--api-base', 
        '--organization', '--proxy', 'api', 'tools',
        '--api-type', '--api-version', '--azure-endpoint', '--azure-ad-token'
    )
    
    $opts | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}

Register-ArgumentCompleter -CommandName openai -ScriptBlock $openaiCompleter
'''


def install_completion(shell: str) -> None:
    """Install shell completion for the specified shell.
    
    Args:
        shell: The shell type ('bash', 'zsh', 'fish', 'powershell')
    """
    shell_lower = shell.lower()
    
    if shell_lower == 'bash':
        completion_script = get_bash_completion()
        print(f"# Add the following to your ~/.bashrc or ~/.bash_profile:")
        print(completion_script)
    elif shell_lower == 'zsh':
        completion_script = get_zsh_completion()
        print(f"# Add the following to your ~/.zshrc:")
        print(completion_script)
    elif shell_lower == 'fish':
        completion_script = get_fish_completion()
        print(f"# Add the following to ~/.config/fish/conf.d/openai.fish:")
        print(completion_script)
    elif shell_lower == 'powershell':
        completion_script = get_powershell_completion()
        print(f"# Add the following to your PowerShell profile:")
        print(completion_script)
    else:
        raise ValueError(f"Unsupported shell: {shell}. Supported shells: bash, zsh, fish, powershell")
