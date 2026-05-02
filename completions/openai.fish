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

# Response format options
set -l formats json url b64 json_object text

# Quality options
set -l qualities standard hd

# Style options
set -l styles vivid natural

# Purpose options
set -l purposes fine-tune assistants

# Chat options
complete -c openai -n '__fish_seen_subcommand_from chat' -l model -d "Model to use" -a "$models" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l messages -d "Messages JSON" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l temperature -d "Temperature" -a "0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l top-p -d "Top P" -a "0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l n -d "Number of completions" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l stream -d "Stream responses" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l stop -d "Stop sequences" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l max-tokens -d "Max tokens" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l presence-penalty -d "Presence penalty" -a "-2.0 -1.0 0.0 1.0 2.0" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l frequency-penalty -d "Frequency penalty" -a "-2.0 -1.0 0.0 1.0 2.0" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l logit-bias -d "Logit bias JSON" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l user -d "User ID" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l response-format -d "Response format" -a "$formats" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l seed -d "Seed" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l tools -d "Tools JSON" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l tool-choice -d "Tool choice" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l function-call -d "Function call" -f
complete -c openai -n '__fish_seen_subcommand_from chat' -l functions -d "Functions JSON" -f

# Image options
complete -c openai -n '__fish_seen_subcommand_from image' -l model -d "Model" -a "dall-e-3 dall-e-2" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l prompt -d "Prompt" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l size -d "Size" -a "$sizes" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l quality -d "Quality" -a "$qualities" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l response-format -d "Format" -a "url b64" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l style -d "Style" -a "$styles" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l user -d "User ID" -f
complete -c openai -n '__fish_seen_subcommand_from image' -l n -d "Number of images" -f

# Audio options
complete -c openai -n '__fish_seen_subcommand_from audio' -l model -d "Model" -a "whisper-1 tts-1 tts-1-hd" -f
complete -c openai -n '__fish_seen_subcommand_from audio' -l voice -d "Voice" -a "$voices" -f
complete -c openai -n '__fish_seen_subcommand_from audio' -l input -d "Input text/file" -f
complete -c openai -n '__fish_seen_subcommand_from audio' -l response-format -d "Format" -a "mp3 opus aac flac wav pcm" -f
complete -c openai -n '__fish_seen_subcommand_from audio' -l speed -d "Speed" -a "0.25 0.5 1.0 2.0 4.0" -f

# Files options
complete -c openai -n '__fish_seen_subcommand_from files' -l file -d "File path" -f
complete -c openai -n '__fish_seen_subcommand_from files' -l purpose -d "Purpose" -a "$purposes" -f

# Models options
complete -c openai -n '__fish_seen_subcommand_from models' -l list -d "List models" -f
complete -c openai -n '__fish_seen_subcommand_from models' -l retrieve -d "Retrieve model" -a "$models" -f
complete -c openai -n '__fish_seen_subcommand_from models' -l delete -d "Delete model" -a "$models" -f

# Completions options
complete -c openai -n '__fish_seen_subcommand_from completions' -l model -d "Model" -a "$models" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l prompt -d "Prompt" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l suffix -d "Suffix" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l temperature -d "Temperature" -a "0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l top-p -d "Top P" -a "0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l n -d "Number" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l stream -d "Stream" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l stop -d "Stop" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l max-tokens -d "Max tokens" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l logprobs -d "Log probs" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l echo -d "Echo prompt" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l presence-penalty -d "Presence penalty" -a "-2.0 -1.0 0.0 1.0 2.0" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l frequency-penalty -d "Frequency penalty" -a "-2.0 -1.0 0.0 1.0 2.0" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l best-of -d "Best of" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l logit-bias -d "Logit bias JSON" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l user -d "User ID" -f
complete -c openai -n '__fish_seen_subcommand_from completions' -l seed -d "Seed" -f

# Fine-tuning options
complete -c openai -n '__fish_seen_subcommand_from fine_tuning' -l model -d "Model" -a "$models" -f
complete -c openai -n '__fish_seen_subcommand_from fine_tuning' -l training-file -d "Training file" -f
complete -c openai -n '__fish_seen_subcommand_from fine_tuning' -l hyperparameters -d "Hyperparameters JSON" -f
complete -c openai -n '__fish_seen_subcommand_from fine_tuning' -l suffix -d "Suffix" -f
complete -c openai -n '__fish_seen_subcommand_from fine_tuning' -l validation-file -d "Validation file" -f
