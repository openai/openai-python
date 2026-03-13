from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from argparse import ArgumentParser

from .._errors import CLIError
from .._models import BaseModel

if TYPE_CHECKING:
    from argparse import _SubParsersAction


class CompletionArgs(BaseModel):
    shell: str


BASH_COMPLETION_SCRIPT = """\
# OpenAI CLI bash completion
# Add this to your ~/.bashrc or ~/.bash_profile:
#   eval "$(openai tools completion bash)"

_openai_completion() {
    local IFS=$'\\n'
    COMPREPLY=( $(env COMP_WORDS="${COMP_WORDS[*]}" \\
                  COMP_CWORD=$COMP_CWORD \\
                  _OPENAI_COMPLETE=bash_complete $1) )
    return 0
}

complete -o default -F _openai_completion openai
"""

ZSH_COMPLETION_SCRIPT = """\
# OpenAI CLI zsh completion
# Add this to your ~/.zshrc:
#   eval "$(openai tools completion zsh)"

_openai_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[openai] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" \\
                       COMP_CWORD=$((CURRENT-1)) \\
                       _OPENAI_COMPLETE=zsh_complete openai)}")

    for key descr in ${(kv)response}; do
      if [[ "$descr" == "_" ]]; then
        completions+=("$key")
      else
        completions_with_descriptions+=("$key":"$descr")
      fi
    done

    if [ -n "$completions_with_descriptions" ]; then
        _describe -V unsorted completions_with_descriptions -U
    fi

    if [ -n "$completions" ]; then
        compadd -U -V unsorted -a completions
    fi
}

compdef _openai_completion openai
"""

FISH_COMPLETION_SCRIPT = """\
# OpenAI CLI fish completion
# Add this to your ~/.config/fish/completions/openai.fish:
#   openai tools completion fish > ~/.config/fish/completions/openai.fish

function _openai_completion
    set -l response (env _OPENAI_COMPLETE=fish_complete COMP_WORDS=(commandline -cp) COMP_CWORD=(commandline -t) openai)

    for completion in $response
        echo -e $completion
    end
end

complete -f -c openai -a "(_openai_completion)"
"""


def register(subparser: _SubParsersAction[ArgumentParser]) -> None:
    sub = subparser.add_parser(
        "completion",
        help="Generate shell completion scripts",
    )
    sub.add_argument(
        "shell",
        choices=["bash", "zsh", "fish"],
        help="Shell type to generate completion for",
    )
    sub.set_defaults(func=_completion, args_model=CompletionArgs)


def _completion(args: CompletionArgs) -> None:
    """Generate shell completion script."""
    try:
        import argcomplete  # noqa: F401
    except ImportError:
        raise CLIError(
            "Shell completion requires the 'argcomplete' package.\n"
            "Install it with: pip install 'openai[completion]'"
        )

    scripts = {
        "bash": BASH_COMPLETION_SCRIPT,
        "zsh": ZSH_COMPLETION_SCRIPT,
        "fish": FISH_COMPLETION_SCRIPT,
    }

    if args.shell not in scripts:
        raise CLIError(f"Unsupported shell: {args.shell}")

    sys.stdout.write(scripts[args.shell])
