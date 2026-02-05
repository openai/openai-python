"""Shell completion for OpenAI CLI."""
import sys

def install_completion(shell: str):
    completions = {
        'bash': '''# openai bash completion
_openai() {
    local cur prev words cword
    _init_completion || return
    case $prev in
        --api-key|--model|--file) return ;;
    esac
    COMPREPLY=($(compgen -W "api-key models files completions chat embeddings --" -- "$cur"))
}
complete -F _openai openai''',
    }
    print(completions.get(shell, ''))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--shell', choices=['bash', 'zsh'], default='bash')
    install_completion(parser.parse_args().shell)
