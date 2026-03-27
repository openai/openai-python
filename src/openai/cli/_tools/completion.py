from __future__ import annotations

import sys
from typing import TYPE_CHECKING, List

from .._models import BaseModel

if TYPE_CHECKING:
    from argparse import ArgumentParser, _SubParsersAction


def register(subparser: _SubParsersAction[ArgumentParser]) -> None:
    sub = subparser.add_parser(
        "completion",
        help="Generate shell completion scripts",
    )
    sub.add_argument(
        "shell",
        choices=["bash", "zsh", "fish", "powershell"],
        help="Shell type to generate completion for",
    )
    sub.set_defaults(func=completion, args_model=CompletionArgs)


class CompletionArgs(BaseModel):
    shell: str
    unknown_args: List[str] = []


def completion(args: CompletionArgs) -> None:
    """Generate and print shell completion script."""
    shell = args.shell

    if shell == "bash":
        sys.stdout.write(_bash_completion())
    elif shell == "zsh":
        sys.stdout.write(_zsh_completion())
    elif shell == "fish":
        sys.stdout.write(_fish_completion())
    elif shell == "powershell":
        sys.stdout.write(_powershell_completion())


def _bash_completion() -> str:
    return '''\
_openai_completion() {
    local cur prev words cword
    _init_completion || return

    local commands="api tools"
    local api_commands="chat.completions.create completions.create embeddings.create images.generate images.edit images.variation audio.transcriptions.create audio.translations.create files.create files.list files.retrieve files.delete files.content models.list models.retrieve models.delete fine_tuning.jobs.create fine_tuning.jobs.list fine_tuning.jobs.retrieve fine_tuning.jobs.cancel fine_tuning.jobs.list_events moderations.create"
    local tools_commands="migrate grit fine_tunes.prepare_data completion"
    local global_opts="-v --verbose -b --api-base -k --api-key -p --proxy -o --organization -t --api-type --api-version --azure-endpoint --azure-ad-token -V --version -h --help"

    case "${prev}" in
        openai)
            COMPREPLY=($(compgen -W "${commands} ${global_opts}" -- "${cur}"))
            return
            ;;
        api)
            COMPREPLY=($(compgen -W "${api_commands}" -- "${cur}"))
            return
            ;;
        tools)
            COMPREPLY=($(compgen -W "${tools_commands}" -- "${cur}"))
            return
            ;;
        completion)
            COMPREPLY=($(compgen -W "bash zsh fish powershell" -- "${cur}"))
            return
            ;;
        -t|--api-type)
            COMPREPLY=($(compgen -W "openai azure" -- "${cur}"))
            return
            ;;
        -b|--api-base|-k|--api-key|-p|--proxy|-o|--organization|--api-version|--azure-endpoint|--azure-ad-token)
            # These options require a value, no completion
            return
            ;;
    esac

    if [[ "${cur}" == -* ]]; then
        COMPREPLY=($(compgen -W "${global_opts}" -- "${cur}"))
    fi
}

complete -F _openai_completion openai
'''


def _zsh_completion() -> str:
    return '''\
#compdef openai

_openai() {
    local -a commands api_commands tools_commands global_opts shells

    commands=(
        'api:Direct API calls'
        'tools:Client side tools for convenience'
    )

    api_commands=(
        'chat.completions.create:Create a chat completion'
        'completions.create:Create a completion'
        'embeddings.create:Create embeddings'
        'images.generate:Generate images'
        'images.edit:Edit images'
        'images.variation:Create image variations'
        'audio.transcriptions.create:Transcribe audio'
        'audio.translations.create:Translate audio'
        'files.create:Upload a file'
        'files.list:List files'
        'files.retrieve:Retrieve a file'
        'files.delete:Delete a file'
        'files.content:Get file content'
        'models.list:List models'
        'models.retrieve:Retrieve a model'
        'models.delete:Delete a model'
        'fine_tuning.jobs.create:Create a fine-tuning job'
        'fine_tuning.jobs.list:List fine-tuning jobs'
        'fine_tuning.jobs.retrieve:Retrieve a fine-tuning job'
        'fine_tuning.jobs.cancel:Cancel a fine-tuning job'
        'fine_tuning.jobs.list_events:List fine-tuning events'
        'moderations.create:Create a moderation'
    )

    tools_commands=(
        'migrate:Migrate code to the new API'
        'grit:Run grit commands'
        'fine_tunes.prepare_data:Prepare data for fine-tuning'
        'completion:Generate shell completion scripts'
    )

    shells=(bash zsh fish powershell)

    global_opts=(
        '(-v --verbose)'{-v,--verbose}'[Set verbosity]'
        '(-b --api-base)'{-b,--api-base}'[API base URL]:url:'
        '(-k --api-key)'{-k,--api-key}'[API key]:key:'
        '(-p --proxy)'{-p,--proxy}'[Proxy URL]:proxy:'
        '(-o --organization)'{-o,--organization}'[Organization ID]:org:'
        '(-t --api-type)'{-t,--api-type}'[API type]:type:(openai azure)'
        '--api-version[Azure API version]:version:'
        '--azure-endpoint[Azure endpoint URL]:url:'
        '--azure-ad-token[Azure AD token]:token:'
        '(-V --version)'{-V,--version}'[Show version]'
        '(-h --help)'{-h,--help}'[Show help]'
    )

    local curcontext="$curcontext" state line
    typeset -A opt_args

    _arguments -C \\
        $global_opts \\
        '1: :->command' \\
        '*:: :->args'

    case $state in
        command)
            _describe -t commands 'openai command' commands
            ;;
        args)
            case $line[1] in
                api)
                    _describe -t api_commands 'api command' api_commands
                    ;;
                tools)
                    if [[ $line[2] == completion ]]; then
                        _describe -t shells 'shell' shells
                    else
                        _describe -t tools_commands 'tools command' tools_commands
                    fi
                    ;;
            esac
            ;;
    esac
}

_openai "$@"
'''


def _fish_completion() -> str:
    return '''\
# Disable file completion by default
complete -c openai -f

# Global options
complete -c openai -s v -l verbose -d "Set verbosity"
complete -c openai -s b -l api-base -d "API base URL" -r
complete -c openai -s k -l api-key -d "API key" -r
complete -c openai -s p -l proxy -d "Proxy URL" -r
complete -c openai -s o -l organization -d "Organization ID" -r
complete -c openai -s t -l api-type -d "API type" -r -a "openai azure"
complete -c openai -l api-version -d "Azure API version" -r
complete -c openai -l azure-endpoint -d "Azure endpoint URL" -r
complete -c openai -l azure-ad-token -d "Azure AD token" -r
complete -c openai -s V -l version -d "Show version"
complete -c openai -s h -l help -d "Show help"

# Main commands
complete -c openai -n "__fish_use_subcommand" -a "api" -d "Direct API calls"
complete -c openai -n "__fish_use_subcommand" -a "tools" -d "Client side tools"

# API subcommands
complete -c openai -n "__fish_seen_subcommand_from api" -a "chat.completions.create" -d "Create a chat completion"
complete -c openai -n "__fish_seen_subcommand_from api" -a "completions.create" -d "Create a completion"
complete -c openai -n "__fish_seen_subcommand_from api" -a "embeddings.create" -d "Create embeddings"
complete -c openai -n "__fish_seen_subcommand_from api" -a "images.generate" -d "Generate images"
complete -c openai -n "__fish_seen_subcommand_from api" -a "images.edit" -d "Edit images"
complete -c openai -n "__fish_seen_subcommand_from api" -a "images.variation" -d "Create image variations"
complete -c openai -n "__fish_seen_subcommand_from api" -a "audio.transcriptions.create" -d "Transcribe audio"
complete -c openai -n "__fish_seen_subcommand_from api" -a "audio.translations.create" -d "Translate audio"
complete -c openai -n "__fish_seen_subcommand_from api" -a "files.create" -d "Upload a file"
complete -c openai -n "__fish_seen_subcommand_from api" -a "files.list" -d "List files"
complete -c openai -n "__fish_seen_subcommand_from api" -a "files.retrieve" -d "Retrieve a file"
complete -c openai -n "__fish_seen_subcommand_from api" -a "files.delete" -d "Delete a file"
complete -c openai -n "__fish_seen_subcommand_from api" -a "files.content" -d "Get file content"
complete -c openai -n "__fish_seen_subcommand_from api" -a "models.list" -d "List models"
complete -c openai -n "__fish_seen_subcommand_from api" -a "models.retrieve" -d "Retrieve a model"
complete -c openai -n "__fish_seen_subcommand_from api" -a "models.delete" -d "Delete a model"
complete -c openai -n "__fish_seen_subcommand_from api" -a "fine_tuning.jobs.create" -d "Create a fine-tuning job"
complete -c openai -n "__fish_seen_subcommand_from api" -a "fine_tuning.jobs.list" -d "List fine-tuning jobs"
complete -c openai -n "__fish_seen_subcommand_from api" -a "fine_tuning.jobs.retrieve" -d "Retrieve a fine-tuning job"
complete -c openai -n "__fish_seen_subcommand_from api" -a "fine_tuning.jobs.cancel" -d "Cancel a fine-tuning job"
complete -c openai -n "__fish_seen_subcommand_from api" -a "fine_tuning.jobs.list_events" -d "List fine-tuning events"
complete -c openai -n "__fish_seen_subcommand_from api" -a "moderations.create" -d "Create a moderation"

# Tools subcommands
complete -c openai -n "__fish_seen_subcommand_from tools" -a "migrate" -d "Migrate code to the new API"
complete -c openai -n "__fish_seen_subcommand_from tools" -a "grit" -d "Run grit commands"
complete -c openai -n "__fish_seen_subcommand_from tools" -a "fine_tunes.prepare_data" -d "Prepare data for fine-tuning"
complete -c openai -n "__fish_seen_subcommand_from tools" -a "completion" -d "Generate shell completion scripts"

# Shell completion options
complete -c openai -n "__fish_seen_subcommand_from completion" -a "bash" -d "Bash completion"
complete -c openai -n "__fish_seen_subcommand_from completion" -a "zsh" -d "Zsh completion"
complete -c openai -n "__fish_seen_subcommand_from completion" -a "fish" -d "Fish completion"
complete -c openai -n "__fish_seen_subcommand_from completion" -a "powershell" -d "PowerShell completion"
'''


def _powershell_completion() -> str:
    return '''\
$scriptblock = {
    param($wordToComplete, $commandAst, $cursorPosition)

    $commands = @{
        'openai' = @('api', 'tools', '-v', '--verbose', '-b', '--api-base', '-k', '--api-key', '-p', '--proxy', '-o', '--organization', '-t', '--api-type', '--api-version', '--azure-endpoint', '--azure-ad-token', '-V', '--version', '-h', '--help')
        'api' = @('chat.completions.create', 'completions.create', 'embeddings.create', 'images.generate', 'images.edit', 'images.variation', 'audio.transcriptions.create', 'audio.translations.create', 'files.create', 'files.list', 'files.retrieve', 'files.delete', 'files.content', 'models.list', 'models.retrieve', 'models.delete', 'fine_tuning.jobs.create', 'fine_tuning.jobs.list', 'fine_tuning.jobs.retrieve', 'fine_tuning.jobs.cancel', 'fine_tuning.jobs.list_events', 'moderations.create')
        'tools' = @('migrate', 'grit', 'fine_tunes.prepare_data', 'completion')
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

Register-ArgumentCompleter -Native -CommandName openai -ScriptBlock $scriptblock
'''
