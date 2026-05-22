#compdef openai

# Zsh completion for openai CLI
# Add to ~/.zshrc: autoload -Uz compinit && compinit

_openai() {
    local -a commands
    local -a api_commands
    local -a tools_commands
    local -a models
    local -a voices
    local -a sizes
    local -a formats
    local -a qualities
    local -a styles
    local -a purposes
    
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
    
    _arguments -C \
        '(-h --help)'{-h,--help}'[Show help]' \
        '(-v --verbose)'{-v,--verbose}'[Set verbosity]' \
        '(-b --api-base)'{-b,--api-base}'[API base URL]:url:_urls' \
        '(-k --api-key)'{-k,--api-key}'[API key]:key:' \
        '(-p --proxy)'{-p,--proxy}'[Proxy]:proxy:' \
        '(-o --organization)'{-o,--organization}'[Organization]:org:' \
        '--api-type[API type]:type:(openai azure)' \
        '--api-version[API version]:version:' \
        '--azure-endpoint[Azure endpoint]:endpoint:_urls' \
        '--azure-ad-token[Azure AD token]:token:' \
        '(-V --version)'{-V,--version}'[Show version]' \
        '1: :->cmd' \
        '*:: :->args'
    
    case $state in
        cmd)
            _describe -t commands 'openai command' commands
            ;;
        args)
            case $words[1] in
                api)
                    _arguments \
                        '1: :->api_cmd' \
                        '*:: :->api_args'
                    
                    case $state in
                        api_cmd)
                            _describe -t commands 'api command' api_commands
                            ;;
                        api_args)
                            case $words[1] in
                                chat)
                                    _arguments \
                                        '--model[Model to use]:model:->models' \
                                        '--messages[Messages JSON]:messages:' \
                                        '--temperature[Temperature]:temperature:(0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0)' \
                                        '--top-p[Top P]:top_p:(0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0)' \
                                        '--n[Number of completions]:n:' \
                                        '--stream[Stream responses]' \
                                        '--stop[Stop sequences]:stop:' \
                                        '--max-tokens[Max tokens]:max_tokens:' \
                                        '--presence-penalty[Presence penalty]:penalty:(-2.0 -1.0 0.0 1.0 2.0)' \
                                        '--frequency-penalty[Frequency penalty]:penalty:(-2.0 -1.0 0.0 1.0 2.0)' \
                                        '--logit-bias[Logit bias JSON]:bias:' \
                                        '--user[User ID]:user:' \
                                        '--response-format[Response format]:format:->formats' \
                                        '--seed[Seed]:seed:' \
                                        '--tools[Tools JSON]:tools:' \
                                        '--tool-choice[Tool choice]:choice:' \
                                        '--function-call[Function call]:call:' \
                                        '--functions[Functions JSON]:functions:'
                                    ;;
                                image)
                                    _arguments \
                                        '--model[Model]:model:(dall-e-3 dall-e-2)' \
                                        '--prompt[Prompt]:prompt:' \
                                        '--size[Size]:size:->sizes' \
                                        '--quality[Quality]:quality:->qualities' \
                                        '--response-format[Format]:format:(url b64)' \
                                        '--style[Style]:style:->styles' \
                                        '--user[User ID]:user:' \
                                        '--n[Number of images]:n:'
                                    ;;
                                audio)
                                    _arguments \
                                        '--model[Model]:model:(whisper-1 tts-1 tts-1-hd)' \
                                        '--voice[Voice]:voice:->voices' \
                                        '--input[Input text/file]:input:_files' \
                                        '--response-format[Format]:format:(mp3 opus aac flac wav pcm)' \
                                        '--speed[Speed]:speed:(0.25 0.5 1.0 2.0 4.0)'
                                    ;;
                                files)
                                    _arguments \
                                        '--file[File path]:file:_files' \
                                        '--purpose[Purpose]:purpose:->purposes'
                                    ;;
                                models)
                                    _arguments \
                                        '--list[List models]' \
                                        '--retrieve[Retrieve model]:model:->models' \
                                        '--delete[Delete model]:model:->models'
                                    ;;
                                completions)
                                    _arguments \
                                        '--model[Model]:model:->models' \
                                        '--prompt[Prompt]:prompt:' \
                                        '--suffix[Suffix]:suffix:' \
                                        '--temperature[Temperature]:temperature:(0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0)' \
                                        '--top-p[Top P]:top_p:(0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0)' \
                                        '--n[Number]:n:' \
                                        '--stream[Stream]' \
                                        '--stop[Stop]:stop:' \
                                        '--max-tokens[Max tokens]:max_tokens:' \
                                        '--logprobs[Log probs]:logprobs:' \
                                        '--echo[Echo prompt]' \
                                        '--presence-penalty[Presence penalty]:penalty:(-2.0 -1.0 0.0 1.0 2.0)' \
                                        '--frequency-penalty[Frequency penalty]:penalty:(-2.0 -1.0 0.0 1.0 2.0)' \
                                        '--best-of[Best of]:n:' \
                                        '--logit-bias[Logit bias JSON]:bias:' \
                                        '--user[User ID]:user:' \
                                        '--seed[Seed]:seed:'
                                    ;;
                                fine_tuning)
                                    _arguments \
                                        '--model[Model]:model:->models' \
                                        '--training-file[Training file]:file:_files' \
                                        '--hyperparameters[Hyperparameters JSON]:params:' \
                                        '--suffix[Suffix]:suffix:' \
                                        '--validation-file[Validation file]:file:_files'
                                    ;;
                            esac
                            ;;
                    esac
                    ;;
                tools)
                    _arguments \
                        '1: :->tools_cmd'
                    
                    case $state in
                        tools_cmd)
                            _describe -t commands 'tools command' tools_commands
                            ;;
                    esac
                    ;;
            esac
            ;;
    esac
    
    # Handle completions for specific options
    case $words[-1] in
        --model|-m)
            _describe -t models 'model' models
            ;;
        --voice)
            _describe -t voices 'voice' voices
            ;;
        --size)
            _describe -t sizes 'size' sizes
            ;;
        --response-format)
            _describe -t formats 'format' formats
            ;;
        --quality)
            _describe -t qualities 'quality' qualities
            ;;
        --style)
            _describe -t styles 'style' styles
            ;;
        --purpose)
            _describe -t purposes 'purpose' purposes
            ;;
    esac
}

_openai "$@"
