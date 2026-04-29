# Shell Autocomplete for OpenAI CLI

This implementation adds shell autocomplete support for the `openai` CLI tool, making it faster and easier to use.

## Supported Shells

- **Bash** (Linux, macOS, WSL)
- **Zsh** (macOS default, Linux)
- **Fish** (cross-platform)
- **PowerShell** (Windows, cross-platform)

## Usage

### Generate Completion Script

```bash
# For bash
openai completion bash

# For zsh
openai completion zsh

# For fish
openai completion fish

# For PowerShell
openai completion powershell
```

### Show Installation Instructions

```bash
openai completion bash --instructions
```

## Installation

### Bash

```bash
# Quick setup (add to ~/.bashrc)
eval "$(openai completion bash)"

# Or save permanently
openai completion bash > ~/.openai-completion.bash
echo 'source ~/.openai-completion.bash' >> ~/.bashrc
```

### Zsh

```bash
# Quick setup (add to ~/.zshrc)
eval "$(openai completion zsh)"

# Or install to fpath
mkdir -p ~/.zsh/completions
openai completion zsh > ~/.zsh/completions/_openai
# Add to ~/.zshrc: fpath=(~/.zsh/completions $fpath)
```

### Fish

```bash
openai completion fish > ~/.config/fish/completions/openai.fish
```

### PowerShell

```powershell
# Add to PowerShell profile
openai completion powershell | Out-String | Invoke-Expression

# Or save and source
openai completion powershell > ~\Documents\PowerShell\openai-completion.ps1
# Add to profile: . ~\Documents\PowerShell\openai-completion.ps1
```

## What Gets Autocompleted

- **Commands**: `api`, `chat`, `audio`, `models`, `files`, `fine-tuning`, etc.
- **Flags**: `--api-key`, `--organization`, `--api-base`, `--help`, etc.
- **Subcommands**: Context-aware completions for nested commands

## Examples

```bash
# Type "openai " and press TAB to see all commands
$ openai <TAB>
api  chat  audio  models  files  fine-tuning  embeddings  images  completions

# Type "openai --" and press TAB for flags
$ openai --<TAB>
--api-key  --organization  --api-base  --help  --version

# Context-aware completions
$ openai completion <TAB>
bash  zsh  fish  powershell
```

## Implementation Details

- Built using native shell completion frameworks
- No external dependencies
- Lightweight and fast
- Works with existing CLI structure
- Easy to extend for new commands

## Testing

```bash
# Test completion generation
python3 -m openai.cli completion bash | head -20

# Verify syntax
python3 -m py_compile src/openai/cli/_completion.py
```
