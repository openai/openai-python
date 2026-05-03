"""Shell completion generation for openai CLI."""

from __future__ import annotations

import sys
import argparse
from typing import Optional


COMPLETION_SCRIPTS = {
    "bash": """\
# Bash completion for openai CLI
# Add to ~/.bashrc: source /path/to/openai.bash
# Or copy to /etc/bash_completion.d/openai

_openai_completions()
{
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="api tools"
    api_commands="chat image audio files models completions fine_tuning"
    tools_commands="fine_tunes"

    case ${COMP_CWORD} in
        1)
            COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            return 0
            ;;
        2)
            case ${prev} in
                api)
                    COMPREPLY=( $(compgen -W "${api_commands}" -- ${cur}) )
                    return 0
                    ;;
                tools)
                    COMPREPLY=( $(compgen -W "${tools_commands}" -- ${cur}) )
                    return 0
                    ;;
            esac
            ;;
        *)
            # Complete model names for --model option
            if [[ ${prev} == "--model" ]]; then
                local models="gpt-4o gpt-4o-mini gpt-4-turbo gpt-4 gpt-3.5-turbo o1 o1-mini o1-pro o3 o3-mini o4-mini dall-e-3 dall-e-2 whisper-1 tts-1 tts-1-hd"
                COMPREPLY=( $(compgen -W "${models}" -- ${cur}) )
                return 0
            fi

            # Complete voice options
            if [[ ${prev} == "--voice" ]]; then
                local voices="alloy echo fable onyx nova shimmer"
                COMPREPLY=( $(compgen -W "${voices}" -- ${cur}) )
                return 0
            fi

            # Complete size options
            if [[ ${prev} == "--size" ]]; then
                local sizes="256x256 512x512 1024x1024 1792x1024 1024x1792"
                COMPREPLY=( $(compgen -W "${sizes}" -- ${cur}) )
                return 0
            fi

            # Default: complete with files
            COMPREPLY=( $(compgen -f -- ${cur}) )
            ;;
    esac
}

complete -F _openai_completions openai
""",
    "zsh": """\
#compdef openai

# Zsh completion for openai CLI
# Add to ~/.zshrc: autoload -Uz compinit && compinit

_openai() {
    local -a commands api_commands tools_commands models voices sizes formats qualities styles purposes

    commands=(
        'api:Direct API calls'
        'tools:Client side tools for convenience'
    )

    api_commands=(
        'chat:Chat completions API'
        'image:Image generation API'
        'audio:Audio/speech API'
        'files:File management API'
        'models:Model management API'
        'completions:Text completions API'
        'fine_tuning:Fine-tuning jobs API'
    )

    tools_commands=(
        'fine_tunes:Fine-tuning tools'
    )

    models=(
        'gpt-4o:GPT-4o - Most capable model'
        'gpt-4o-mini:GPT-4o Mini - Fast and efficient'
        'gpt-4-turbo:GPT-4 Turbo - With vision'
        'gpt-4:GPT-4 - Original GPT-4'
        'gpt-3.5-turbo:GPT-3.5 Turbo - Fast and cheap'
        'o1:O1 - Reasoning model'
        'o1-mini:O1 Mini - Fast reasoning'
        'o1-pro:O1 Pro - Enhanced reasoning'
        'o3:O3 - Latest reasoning'
        'o3-mini:O3 Mini - Fast latest reasoning'
        'o4-mini:O4 Mini - Latest fast reasoning'
        'dall-e-3:DALL-E 3 - Image generation'
        'dall-e-2:DALL-E 2 - Image generation'
        'whisper-1:Whisper - Speech to text'
        'tts-1:TTS - Text to speech'
        'tts-1-hd:TTS HD - High quality speech'
    )

    voices=(alloy echo fable onyx nova shimmer)
    sizes=(256x256 512x512 1024x1024 1792x1024 1024x1792)
    formats=(json url b64 json_object text)
    qualities=(standard hd)
    styles=(vivid natural)
    purposes=(fine-tune assistants)

    _arguments -C \\
        '(-h --help)'{-h,--help}'[Show help]' \\
        '(-v --verbose)'{-v,--verbose}'[Set verbosity]' \\
        '(-b --api-base)'{-b,--api-base}'[API base URL]:url:_urls' \\
        '(-k --api-key)'{-k,--api-key}'[API key]:key:' \\
        '(-p --proxy)'{-p,--proxy}'[Proxy]:proxy:' \\
        '(-o --organization)'{-o,--organization}'[Organization]:org:' \\
        '(-V --version)'{-V,--version}'[Show version]' \\
        '1: :->cmd' \\
        '*:: :->args'

    case $state in
        cmd)
            _describe -t commands 'openai command' commands
            ;;
        args)
            case $words[1] in
                api)
                    _arguments '1: :->api_cmd' '*:: :->api_args'
                    case $state in
                        api_cmd)
                            _describe -t commands 'api command' api_commands
                            ;;
                        api_args)
                            case $words[1] in
                                chat)
                                    _arguments \\
                                        '--model[Model]:model:->models' \\
                                        '--messages[Messages JSON]:messages:' \\
                                        '--temperature[Temperature]:temperature:' \\
                                        '--top-p[Top P]:top_p:' \\
                                        '--n[Number]:n:' \\
                                        '--stream[Stream]' \\
                                        '--stop[Stop]:stop:' \\
                                        '--max-tokens[Max tokens]:max_tokens:' \\
                                        '--presence-penalty[Presence penalty]:penalty:' \\
                                        '--frequency-penalty[Frequency penalty]:penalty:' \\
                                        '--user[User ID]:user:' \\
                                        '--response-format[Format]:format:->formats' \\
                                        '--seed[Seed]:seed:' \\
                                        '--tools[Tools JSON]:tools:' \\
                                        '--tool-choice[Tool choice]:choice:'
                                    ;;
                                image)
                                    _arguments \\
                                        '--model[Model]:model:(dall-e-3 dall-e-2)' \\
                                        '--prompt[Prompt]:prompt:' \\
                                        '--size[Size]:size:->sizes' \\
                                        '--quality[Quality]:quality:->qualities' \\
                                        '--response-format[Format]:format:(url b64)' \\
                                        '--style[Style]:style:->styles' \\
                                        '--user[User ID]:user:' \\
                                        '--n[Number]:n:'
                                    ;;
                                audio)
                                    _arguments \\
                                        '--model[Model]:model:(whisper-1 tts-1 tts-1-hd)' \\
                                        '--voice[Voice]:voice:->voices' \\
                                        '--input[Input]:input:_files' \\
                                        '--response-format[Format]:format:(mp3 opus aac flac wav pcm)' \\
                                        '--speed[Speed]:speed:(0.25 0.5 1.0 2.0 4.0)'
                                    ;;
                                files)
                                    _arguments \\
                                        '--file[File]:file:_files' \\
                                        '--purpose[Purpose]:purpose:->purposes'
                                    ;;
                                models)
                                    _arguments \\
                                        '--list[List]' \\
                                        '--retrieve[Retrieve]:model:->models' \\
                                        '--delete[Delete]:model:->models'
                                    ;;
                                completions)
                                    _arguments \\
                                        '--model[Model]:model:->models' \\
                                        '--prompt[Prompt]:prompt:' \\
                                        '--temperature[Temperature]:temperature:' \\
                                        '--max-tokens[Max tokens]:max_tokens:' \\
                                        '--echo[Echo]' \\
                                        '--stream[Stream]' \\
                                        '--stop[Stop]:stop:' \\
                                        '--user[User ID]:user:' \\
                                        '--seed[Seed]:seed:'
                                    ;;
                                fine_tuning)
                                    _arguments \\
                                        '--model[Model]:model:->models' \\
                                        '--training-file[Training file]:file:_files' \\
                                        '--hyperparameters[Hyperparams JSON]:params:' \\
                                        '--suffix[Suffix]:suffix:' \\
                                        '--validation-file[Validation file]:file:_files'
                                    ;;
                            esac
                            ;;
                    esac
                    ;;
                tools)
                    _arguments '1: :->tools_cmd'
                    case $state in
                        tools_cmd)
                            _describe -t commands 'tools command' tools_commands
                            ;;
                    esac
                    ;;
            esac
            ;;
    esac

    case $words[-1] in
        --model|-m) _describe -t models 'model' models ;;
        --voice) _describe -t voices 'voice' voices ;;
        --size) _describe -t sizes 'size' sizes ;;
        --response-format) _describe -t formats 'format' formats ;;
        --quality) _describe -t qualities 'quality' qualities ;;
        --style) _describe -t styles 'style' styles ;;
        --purpose) _describe -t purposes 'purpose' purposes ;;
    esac
}

_openai "$@"
""",
    "fish": """\
# Fish completion for openai CLI
# Add to ~/.config/fish/completions/openai.fish

# Global options
complete -c openai -l verbose -d "Set verbosity" -f
complete -c openai -l api-base -d "API base URL" -f
complete -c openai -l api-key -d "API key" -f
complete -c openai -l proxy -d "Proxy" -f
complete -c openai -l organization -d "Organization" -f
complete -c openai -l api-type -d "API type" -a "openai azure" -f
complete -c openai -l api-version -d "API version" -f
complete -c openai -l azure-endpoint -d "Azure endpoint" -f
complete -c openai -l azure-ad-token -d "Azure AD token" -f
complete -c openai -l version -d "Show version" -f
complete -c openai -l help -d "Show help" -f

# Main commands
complete -c openai -n '__fish_use_subcommand' -a api -d "Direct API calls"
complete -c openai -n '__fish_use_subcommand' -a tools -d "Client side tools"

# API subcommands
complete -c openai -n '__fish_seen_subcommand_from api' -a chat -d "Chat completions"
complete -c openai -n '__fish_seen_subcommand_from api' -a image -d "Image generation"
complete -c openai -n '__fish_seen_subcommand_from api' -a audio -d "Audio/speech"
complete -c openai -n '__fish_seen_subcommand_from api' -a files -d "File management"
complete -c openai -n '__fish_seen_subcommand_from api' -a models -d "Model management"
complete -c openai -n '__fish_seen_subcommand_from api' -a completions -d "Text completions"
complete -c openai -n '__fish_seen_subcommand_from api' -a fine_tuning -d "Fine-tuning jobs"

# Tools subcommands
complete -c openai -n '__fish_seen_subcommand_from tools' -a fine_tunes -d "Fine-tuning tools"

# Model names
set -l models gpt-4o gpt-4o-mini gpt-4-turbo gpt-4 gpt-3.5-turbo o1 o1-mini o1-pro o3 o3-mini o4-mini dall-e-3 dall-e-2 whisper-1 tts-1 tts-1-hd

# Voice options
set -l voices alloy echo fable onyx nova shimmer

# Size options
set -l sizes 256x256 512x512 1024x1024 1792x1024 1024x1792

# Chat options
complete -c openai -n '__fish_seen_subcommand_from chat' -l model -d "Model" -a "$models" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l messages -d "Messages JSON" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l temperature -d "Temperature" -a "0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l top-p -d "Top P" -a "0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l n -d "Number" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l stream -d "Stream" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l stop -d "Stop" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l max-tokens -d "Max tokens" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l presence-penalty -d "Presence penalty" -a "-2.0 -1.0 0.0 1.0 2.0" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l frequency-penalty -d "Frequency penalty" -a "-2.0 -1.0 0.0 1.0 2.0" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l user -d "User ID" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l response-format -d "Format" -a "json json_object" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l seed -d "Seed" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l tools -d "Tools JSON" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l tool-choice -d "Tool choice" -f

# Image options
complete -c openai -n '__fish_seen_subcommand_from image' -l model -d "Model" -a "dall-e-3 dall-e-2" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l prompt -d "Prompt" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l size -d "Size" -a "$sizes" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l quality -d "Quality" -a "standard hd" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l response-format -d "Format" -a "url b64" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l style -d "Style" -a "vivid natural" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l user -d "User ID" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l n -d "Number" -f

# Audio options
complete -c openai -n '__fish_seen_subcommand_from audio' -l model -d "Model" -a "whisper-1 tts-1 tts-1-hd" -f
complete -c openai -n '__fish_seen_subcommand_from audio' -l voice -d "Voice" -a "$voices" -f
complete -c openai -n '__fish_seen_subcommand_from audio' -l input -d "Input" -f
complete -c openai -n '__fish_seen_subcommand_from audio' -l response-format -d "Format" -a "mp3 opus aac flac wav pcm" -f
complete -c openai -n '__fish_seen_subcommand_from audio' -l speed -d "Speed" -a "0.25 0.5 1.0 2.0 4.0" -f

# Files options
complete -c openai -n '__fish_seen_subcommand_from files' -l file -d "File" -f
complete -c openai -n '__fish_seen_subcommand_from files' -l purpose -d "Purpose" -a "fine-tune assistants" -f

# Models options
complete -c openai -n '__fish_seen_subcommand_from models' -l list -d "List" -f
complete -c openai -n '__fish_seen_subcommand_from models' -l retrieve -d "Retrieve" -a "$models" -f
complete -c openai -n '__fish_seen_subcommand_from models' -l delete -d "Delete" -a "$models" -f

# Completions options
complete -c openai -n '__fish_seen_subcommand_from completions' -l model -d "Model" -a "$models" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l prompt -d "Prompt" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l temperature -d "Temperature" -a "0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l max-tokens -d "Max tokens" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l echo -d "Echo" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l stream -d "Stream" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l stop -d "Stop" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l user -d "User ID" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l seed -d "Seed" -f

# Fine-tuning options
complete -c openai -n '__fish_seen_subcommand_from fine_tuning' -l model -d "Model" -a "$models" -f
complete -c openai -n '__fish_seen_subcommand_from fine_tuning' -l training-file -d "Training file" -f
complete -c openai -n '__fish_seen_subcommand_from fine_tuning' -l hyperparameters -d "Hyperparameters JSON" -f
complete -c openai -n '__fish_seen_subcommand_from fine_tuning' -l suffix -d "Suffix" -f
complete -c openai -n '__fish_seen_subcommand_from fine_tuning' -l validation-file -d "Validation file" -f
""",
}


def register(parser: argparse.ArgumentParser) -> None:
    """Register the completion command."""
    sub = parser.add_parser(
        "completion",
        help="Generate shell completion scripts",
    )
    sub.add_argument(
        "shell",
        choices=["bash", "zsh", "fish"],
        help="Shell to generate completion for",
    )
    sub.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    )
    sub.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    """Generate shell completion script."""
    script = COMPLETION_SCRIPTS.get(args.shell)
    if not script:
        print(f"Error: Unsupported shell '{args.shell}'", file=sys.stderr)
        return

    if args.output:
        with open(args.output, "w") as f:
            f.write(script)
        print(f"Completion script written to {args.output}")
        print(f"\nTo enable completions:")
        if args.shell == "bash":
            print(f"  Add to ~/.bashrc: source {args.output}")
        elif args.shell == "zsh":
            print(f"  Add to ~/.zshrc: source {args.output}")
        elif args.shell == "fish":
            print(f"  Fish completions are auto-loaded from ~/.config/fish/completions/")
    else:
        print(script)
