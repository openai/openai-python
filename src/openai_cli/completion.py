"""Shell completion for OpenAI CLI."""
import sys
import argparse

def install_completion(shell: str):
    """Generate shell completion script for OpenAI CLI."""
    completions = {
        'bash': '''# openai bash completion
_openai() {
    local cur prev words cword
    _init_completion || return
    case $prev in
        openai)
            COMPREPLY=($(compgen -W "api chat models files embeddings completions --" -- "$cur"))
            return
            ;;
        --api-key|--api-key=)
            return
            ;;
        --model|--model=)
            _filedir
            return
            ;;
        -o|--organization)
            return
            ;;
    esac
    COMPREPLY=($(compgen -W "$(openai --help 2>&1 | grep -E '^  [a-z]' | awk '{print $1}' | tr '\\n' ' ')" -- "$cur"))
}
complete -F _openai openai''',
        'zsh': '''# openai zsh completion
autoload -U compinit
compdef _openai openai

_openai() {
    local -a commands
    commands=(
        'api:Direct API calls'
        'chat:Chat completions'
        'models:List models'
        'files:File operations'
        'embeddings:Embedding operations'
        'completions:Completion operations'
    )
    _describe -t commands 'openai command' commands
}
''',
    }
    print(completions.get(shell, f'Error: Unknown shell {shell}. Supported shells: bash, zsh'))
    return 0

def generate_completions() -> str:
    """Generate completion script dynamically based on available commands."""
    # Get subcommands from CLI
    commands = ["api", "chat", "models", "files", "embeddings", "completions", "fine_tuning"]
    options = ["--api-key", "--model", "--organization", "--verbose", "--help"]
    
    bash_completion = f'''# openai bash completion (auto-generated)
_openai() {{
    local cur prev words cword
    _init_completion || return
    case $prev in
        openai)
            COMPREPLY=($(compgen -W "{' '.join(commands)}" -- "$cur"))
            return
            ;;
        ${{words[0]}})
            COMPREPLY=($(compgen -W "{' '.join(options)}" -- "$cur"))
            return
            ;;
    esac
    _filedir
}} &&
complete -F _openai openai
'''
    return bash_completion

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate shell completion scripts for OpenAI CLI')
    parser.add_argument('--shell', choices=['bash', 'zsh'], default='bash', help='Shell type')
    parser.add_argument('--print', action='store_true', help='Print completions to stdout')
    args = parser.parse_args()
    
    if args.print:
        print(generate_completions())
    else:
        install_completion(args.shell)
