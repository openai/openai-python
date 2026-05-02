# Bash completion for openai CLI
# Source this file or add to /etc/bash_completion.d/

_openai_completions()
{
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main commands
    commands="api tools"
    
    # API subcommands
    api_commands="chat image audio files models completions fine_tuning"
    
    # Tools subcommands
    tools_commands="fine_tunes"
    
    # Global options
    global_opts="--verbose --api-base --api-key --proxy --organization --api-type --api-version --azure-endpoint --azure-ad-token --version --help"
    
    # Chat options
    chat_opts="--model --messages --temperature --top-p --n --stream --stop --max-tokens --presence-penalty --frequency-penalty --logit-bias --user --response-format --seed --tools --tool-choice --function-call --functions"
    
    # Image options
    image_opts="--model --prompt --size --quality --response-format --style --user --n"
    
    # Audio options
    audio_opts="--model --voice --input --response-format --speed"
    
    # Files options
    files_opts="--file --purpose"
    
    # Models options
    models_opts="--list --retrieve --delete"
    
    # Completions options
    completions_opts="--model --prompt --suffix --temperature --top-p --n --stream --stop --max-tokens --logprobs --echo --presence-penalty --frequency-penalty --best-of --logit-bias --user --seed"
    
    # Fine-tuning options
    fine_tuning_opts="--model --training-file --hyperparameters --suffix --validation-file"
    
    case ${COMP_CWORD} in
        1)
            COMPREPLY=( $(compgen -W "${commands} ${global_opts}" -- ${cur}) )
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
                -k|--api-key)
                    # Don't complete API keys
                    return 0
                    ;;
                -b|--api-base)
                    COMPREPLY=( $(compgen -W "https://api.openai.com/v1 https://api.openai.com/v1/azure" -- ${cur}) )
                    return 0
                    ;;
                -o|--organization)
                    return 0
                    ;;
                *)
                    ;;
            esac
            ;;
        3)
            case ${COMP_WORDS[1]} in
                api)
                    case ${prev} in
                        chat)
                            COMPREPLY=( $(compgen -W "${chat_opts}" -- ${cur}) )
                            return 0
                            ;;
                        image)
                            COMPREPLY=( $(compgen -W "${image_opts}" -- ${cur}) )
                            return 0
                            ;;
                        audio)
                            COMPREPLY=( $(compgen -W "${audio_opts}" -- ${cur}) )
                            return 0
                            ;;
                        files)
                            COMPREPLY=( $(compgen -W "${files_opts}" -- ${cur}) )
                            return 0
                            ;;
                        models)
                            COMPREPLY=( $(compgen -W "${models_opts}" -- ${cur}) )
                            return 0
                            ;;
                        completions)
                            COMPREPLY=( $(compgen -W "${completions_opts}" -- ${cur}) )
                            return 0
                            ;;
                        fine_tuning)
                            COMPREPLY=( $(compgen -W "${fine_tuning_opts}" -- ${cur}) )
                            return 0
                            ;;
                        *)
                            ;;
                    esac
                    ;;
                *)
                    ;;
            esac
            ;;
        *)
            # Complete model names for --model option
            if [[ ${prev} == "--model" || ${prev} == "-m" ]]; then
                local models="gpt-4o gpt-4o-mini gpt-4-turbo gpt-4 gpt-3.5-turbo o1 o1-mini o1-pro o3 o3-mini o4-mini dall-e-3 dall-e-2 whisper-1 tts-1 tts-1-hd"
                COMPREPLY=( $(compgen -W "${models}" -- ${cur}) )
                return 0
            fi
            
            # Complete voice options for --voice
            if [[ ${prev} == "--voice" ]]; then
                local voices="alloy echo fable onyx nova shimmer"
                COMPREPLY=( $(compgen -W "${voices}" -- ${cur}) )
                return 0
            fi
            
            # Complete size options for --size
            if [[ ${prev} == "--size" ]]; then
                local sizes="256x256 512x512 1024x1024 1792x1024 1024x1792"
                COMPREPLY=( $(compgen -W "${sizes}" -- ${cur}) )
                return 0
            fi
            
            # Complete response format options
            if [[ ${prev} == "--response-format" ]]; then
                local formats="json url b64 json_object text"
                COMPREPLY=( $(compgen -W "${formats}" -- ${cur}) )
                return 0
            fi
            
            # Complete quality options
            if [[ ${prev} == "--quality" ]]; then
                local qualities="standard hd"
                COMPREPLY=( $(compgen -W "${qualities}" -- ${cur}) )
                return 0
            fi
            
            # Complete style options
            if [[ ${prev} == "--style" ]]; then
                local styles="vivid natural"
                COMPREPLY=( $(compgen -W "${styles}" -- ${cur}) )
                return 0
            fi
            
            # Complete purpose options for files
            if [[ ${prev} == "--purpose" ]]; then
                local purposes="fine-tune assistants"
                COMPREPLY=( $(compgen -W "${purposes}" -- ${cur}) )
                return 0
            fi
            
            # Default: complete with files
            COMPREPLY=( $(compgen -f -- ${cur}) )
            ;;
    esac
}

complete -F _openai_completions openai
