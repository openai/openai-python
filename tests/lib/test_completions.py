"""Tests for shell completion scripts in openai.cli._completions."""

from __future__ import annotations

import argparse
import pathlib

import pytest

from openai.cli._completions import COMPLETION_SCRIPTS, register, run


# ---------------------------------------------------------------------------
# Expected constants
# ---------------------------------------------------------------------------

EXPECTED_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
    "o1",
    "o1-mini",
    "o1-pro",
    "o3",
    "o3-mini",
    "o4-mini",
    "dall-e-3",
    "dall-e-2",
    "whisper-1",
    "tts-1",
    "tts-1-hd",
]

EXPECTED_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

EXPECTED_SIZES = [
    "256x256",
    "512x512",
    "1024x1024",
    "1792x1024",
    "1024x1792",
]

EXPECTED_QUALITIES = ["standard", "hd"]

EXPECTED_STYLES = ["vivid", "natural"]

EXPECTED_FORMATS = ["json", "url", "b64", "json_object", "text"]

EXPECTED_PURPOSES = ["fine-tune", "assistants"]

EXPECTED_SUBCOMMANDS = {
    "main": ["api", "tools"],
    "api": [
        "chat",
        "image",
        "audio",
        "files",
        "models",
        "completions",
        "fine_tuning",
    ],
    "tools": ["fine_tunes"],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_completion_env() -> tuple[argparse.ArgumentParser, argparse._SubParsersAction]:
    """Return (parent_parser, subparsers) as the real CLI builds them."""
    parser = argparse.ArgumentParser(prog="openai")
    subparsers = parser.add_subparsers(dest="command")
    return parser, subparsers


# ---------------------------------------------------------------------------
# Tests: COMPLETION_SCRIPTS dict
# ---------------------------------------------------------------------------


class TestCompletionScriptsDict:
    """Verify the COMPLETION_SCRIPTS dictionary structure."""

    def test_supported_shells(self) -> None:
        assert set(COMPLETION_SCRIPTS.keys()) == {"bash", "zsh", "fish"}

    def test_all_scripts_are_strings(self) -> None:
        for shell, script in COMPLETION_SCRIPTS.items():
            assert isinstance(script, str), f"{shell} script is not a string"

    def test_all_scripts_are_non_empty(self) -> None:
        for shell, script in COMPLETION_SCRIPTS.items():
            assert len(script) > 0, f"{shell} script is empty"


# ---------------------------------------------------------------------------
# Tests: Bash completion script
# ---------------------------------------------------------------------------


class TestBashCompletion:
    """Verify the bash completion script content."""

    @pytest.fixture()
    def script(self) -> str:
        return COMPLETION_SCRIPTS["bash"]

    def test_contains_completion_function(self, script: str) -> None:
        assert "_openai_completions()" in script

    def test_contains_complete_registration(self, script: str) -> None:
        assert "complete -F _openai_completions openai" in script

    def test_contains_main_subcommands(self, script: str) -> None:
        for cmd in EXPECTED_SUBCOMMANDS["main"]:
            assert cmd in script, f"Bash script missing main subcommand: {cmd}"

    def test_contains_api_subcommands(self, script: str) -> None:
        for cmd in EXPECTED_SUBCOMMANDS["api"]:
            assert cmd in script, f"Bash script missing api subcommand: {cmd}"

    def test_contains_tools_subcommands(self, script: str) -> None:
        for cmd in EXPECTED_SUBCOMMANDS["tools"]:
            assert cmd in script, f"Bash script missing tools subcommand: {cmd}"

    @pytest.mark.parametrize("model", EXPECTED_MODELS)
    def test_contains_model(self, script: str, model: str) -> None:
        assert model in script, f"Bash script missing model: {model}"

    @pytest.mark.parametrize("voice", EXPECTED_VOICES)
    def test_contains_voice(self, script: str, voice: str) -> None:
        assert voice in script, f"Bash script missing voice: {voice}"

    @pytest.mark.parametrize("size", EXPECTED_SIZES)
    def test_contains_size(self, script: str, size: str) -> None:
        assert size in script, f"Bash script missing size: {size}"

    def test_contains_voice_flag(self, script: str) -> None:
        assert '"--voice"' in script or "--voice" in script

    def test_contains_model_flag(self, script: str) -> None:
        assert "--model" in script

    def test_contains_size_flag(self, script: str) -> None:
        assert "--size" in script

    def test_uses_compgen(self, script: str) -> None:
        """Bash completions should use compgen."""
        assert "compgen" in script

    def test_uses_compreply(self, script: str) -> None:
        assert "COMPREPLY" in script


# ---------------------------------------------------------------------------
# Tests: Zsh completion script
# ---------------------------------------------------------------------------


class TestZshCompletion:
    """Verify the zsh completion script content."""

    @pytest.fixture()
    def script(self) -> str:
        return COMPLETION_SCRIPTS["zsh"]

    def test_contains_compdef(self, script: str) -> None:
        assert "#compdef openai" in script

    def test_contains_openai_function(self, script: str) -> None:
        assert "_openai()" in script

    def test_contains_main_subcommands(self, script: str) -> None:
        for cmd in EXPECTED_SUBCOMMANDS["main"]:
            assert cmd in script, f"Zsh script missing main subcommand: {cmd}"

    def test_contains_api_subcommands(self, script: str) -> None:
        for cmd in EXPECTED_SUBCOMMANDS["api"]:
            assert cmd in script, f"Zsh script missing api subcommand: {cmd}"

    def test_contains_tools_subcommands(self, script: str) -> None:
        for cmd in EXPECTED_SUBCOMMANDS["tools"]:
            assert cmd in script, f"Zsh script missing tools subcommand: {cmd}"

    @pytest.mark.parametrize("model", EXPECTED_MODELS)
    def test_contains_model(self, script: str, model: str) -> None:
        assert model in script, f"Zsh script missing model: {model}"

    @pytest.mark.parametrize("voice", EXPECTED_VOICES)
    def test_contains_voice(self, script: str, voice: str) -> None:
        assert voice in script, f"Zsh script missing voice: {voice}"

    @pytest.mark.parametrize("size", EXPECTED_SIZES)
    def test_contains_size(self, script: str, size: str) -> None:
        assert size in script, f"Zsh script missing size: {size}"

    @pytest.mark.parametrize("quality", EXPECTED_QUALITIES)
    def test_contains_quality(self, script: str, quality: str) -> None:
        assert quality in script, f"Zsh script missing quality: {quality}"

    @pytest.mark.parametrize("style", EXPECTED_STYLES)
    def test_contains_style(self, script: str, style: str) -> None:
        assert style in script, f"Zsh script missing style: {style}"

    @pytest.mark.parametrize("fmt", EXPECTED_FORMATS)
    def test_contains_format(self, script: str, fmt: str) -> None:
        assert fmt in script, f"Zsh script missing format: {fmt}"

    @pytest.mark.parametrize("purpose", EXPECTED_PURPOSES)
    def test_contains_purpose(self, script: str, purpose: str) -> None:
        assert purpose in script, f"Zsh script missing purpose: {purpose}"

    def test_uses_arguments(self, script: str) -> None:
        assert "_arguments" in script

    def test_uses_describe(self, script: str) -> None:
        assert "_describe" in script

    def test_contains_help_flag(self, script: str) -> None:
        assert "--help" in script

    def test_contains_version_flag(self, script: str) -> None:
        assert "--version" in script

    def test_contains_api_key_flag(self, script: str) -> None:
        assert "--api-key" in script

    def test_model_descriptions_present(self, script: str) -> None:
        """Zsh script should have descriptions for models."""
        assert "GPT-4o" in script
        assert "DALL-E 3" in script or "dall-e-3" in script

    def test_contains_chat_options(self, script: str) -> None:
        """Verify chat subcommand options are present."""
        assert "--temperature" in script
        assert "--max-tokens" in script
        assert "--stream" in script
        assert "--messages" in script

    def test_contains_image_options(self, script: str) -> None:
        """Verify image subcommand options are present."""
        assert "--prompt" in script
        assert "--quality" in script
        assert "--style" in script

    def test_contains_audio_options(self, script: str) -> None:
        """Verify audio subcommand options are present."""
        assert "--voice" in script
        assert "--input" in script
        assert "--speed" in script


# ---------------------------------------------------------------------------
# Tests: Fish completion script
# ---------------------------------------------------------------------------


class TestFishCompletion:
    """Verify the fish completion script content."""

    @pytest.fixture()
    def script(self) -> str:
        return COMPLETION_SCRIPTS["fish"]

    def test_contains_complete_commands(self, script: str) -> None:
        assert "complete -c openai" in script

    def test_contains_main_subcommands(self, script: str) -> None:
        for cmd in EXPECTED_SUBCOMMANDS["main"]:
            assert cmd in script, f"Fish script missing main subcommand: {cmd}"

    def test_contains_api_subcommands(self, script: str) -> None:
        for cmd in EXPECTED_SUBCOMMANDS["api"]:
            assert cmd in script, f"Fish script missing api subcommand: {cmd}"

    def test_contains_tools_subcommands(self, script: str) -> None:
        for cmd in EXPECTED_SUBCOMMANDS["tools"]:
            assert cmd in script, f"Fish script missing tools subcommand: {cmd}"

    @pytest.mark.parametrize("model", EXPECTED_MODELS)
    def test_contains_model(self, script: str, model: str) -> None:
        assert model in script, f"Fish script missing model: {model}"

    @pytest.mark.parametrize("voice", EXPECTED_VOICES)
    def test_contains_voice(self, script: str, voice: str) -> None:
        assert voice in script, f"Fish script missing voice: {voice}"

    @pytest.mark.parametrize("size", EXPECTED_SIZES)
    def test_contains_size(self, script: str, size: str) -> None:
        assert size in script, f"Fish script missing size: {size}"

    @pytest.mark.parametrize("quality", EXPECTED_QUALITIES)
    def test_contains_quality(self, script: str, quality: str) -> None:
        assert quality in script, f"Fish script missing quality: {quality}"

    @pytest.mark.parametrize("style", EXPECTED_STYLES)
    def test_contains_style(self, script: str, style: str) -> None:
        assert style in script, f"Fish script missing style: {style}"

    def test_uses_fish_subcommand_detection(self, script: str) -> None:
        assert "__fish_use_subcommand" in script

    def test_uses_fish_seen_subcommand(self, script: str) -> None:
        assert "__fish_seen_subcommand_from" in script

    def test_contains_global_options(self, script: str) -> None:
        """Fish uses `-l` syntax for long options, not `--`."""
        assert "-l verbose" in script
        assert "-l api-base" in script
        assert "-l api-key" in script
        assert "-l proxy" in script
        assert "-l organization" in script
        assert "-l version" in script
        assert "-l help" in script

    def test_contains_azure_options(self, script: str) -> None:
        """Fish script includes Azure-related options."""
        assert "-l api-type" in script
        assert "openai azure" in script
        assert "-l api-version" in script
        assert "-l azure-endpoint" in script
        assert "-l azure-ad-token" in script

    def test_contains_chat_options(self, script: str) -> None:
        """Fish uses `-l` for long option names."""
        assert "-l model" in script
        assert "-l temperature" in script
        assert "-l max-tokens" in script
        assert "-l stream" in script
        assert "-l messages" in script

    def test_contains_image_options(self, script: str) -> None:
        assert "-l prompt" in script
        assert "-l quality" in script
        assert "-l style" in script

    def test_contains_audio_options(self, script: str) -> None:
        assert "-l voice" in script
        assert "-l input" in script
        assert "-l speed" in script

    def test_contains_file_options(self, script: str) -> None:
        assert "-l file" in script
        assert "-l purpose" in script

    def test_contains_models_subcommand_options(self, script: str) -> None:
        assert "-l list" in script
        assert "-l retrieve" in script
        assert "-l delete" in script


# ---------------------------------------------------------------------------
# Tests: Script consistency across shells
# ---------------------------------------------------------------------------


class TestCrossShellConsistency:
    """Verify that all three shell scripts expose the same models/options."""

    def test_all_scripts_contain_same_models(self) -> None:
        for model in EXPECTED_MODELS:
            for shell, script in COMPLETION_SCRIPTS.items():
                assert model in script, f"{shell} script missing model: {model}"

    def test_all_scripts_contain_same_voices(self) -> None:
        for voice in EXPECTED_VOICES:
            for shell, script in COMPLETION_SCRIPTS.items():
                assert voice in script, f"{shell} script missing voice: {voice}"

    def test_all_scripts_contain_same_sizes(self) -> None:
        for size in EXPECTED_SIZES:
            for shell, script in COMPLETION_SCRIPTS.items():
                assert size in script, f"{shell} script missing size: {size}"

    def test_all_scripts_contain_main_subcommands(self) -> None:
        for cmd in EXPECTED_SUBCOMMANDS["main"]:
            for shell, script in COMPLETION_SCRIPTS.items():
                assert cmd in script, (
                    f"{shell} script missing main subcommand: {cmd}"
                )


# ---------------------------------------------------------------------------
# Tests: register() and run()
# ---------------------------------------------------------------------------


class TestRegister:
    """Test the CLI argument registration."""

    def test_register_adds_completion_subparser(self) -> None:
        parent, subparsers = _make_completion_env()
        register(subparsers)
        # Parse a valid completion command — should not raise
        args = parent.parse_args(["completion", "bash"])
        assert args.shell == "bash"

    def test_register_accepts_all_shells(self) -> None:
        parent, subparsers = _make_completion_env()
        register(subparsers)
        for shell in ("bash", "zsh", "fish"):
            args = parent.parse_args(["completion", shell])
            assert args.shell == shell

    def test_register_rejects_invalid_shell(self) -> None:
        parent, subparsers = _make_completion_env()
        register(subparsers)
        with pytest.raises(SystemExit):
            parent.parse_args(["completion", "powershell"])

    def test_register_accepts_output_flag(self) -> None:
        parent, subparsers = _make_completion_env()
        register(subparsers)
        args = parent.parse_args(["completion", "bash", "--output", "/tmp/out.sh"])
        assert args.output == "/tmp/out.sh"

    def test_register_accepts_short_output_flag(self) -> None:
        parent, subparsers = _make_completion_env()
        register(subparsers)
        args = parent.parse_args(["completion", "bash", "-o", "/tmp/out.sh"])
        assert args.output == "/tmp/out.sh"

    def test_register_sets_func_default(self) -> None:
        parent, subparsers = _make_completion_env()
        register(subparsers)
        args = parent.parse_args(["completion", "zsh"])
        assert args.func is run


class TestRun:
    """Test the run() function that outputs scripts."""

    def test_run_bash_prints_to_stdout(self, capsys: pytest.CaptureFixture[str]) -> None:
        args = argparse.Namespace(shell="bash", output=None)
        run(args)
        captured = capsys.readouterr()
        assert "_openai_completions()" in captured.out
        assert "complete -F _openai_completions openai" in captured.out

    def test_run_zsh_prints_to_stdout(self, capsys: pytest.CaptureFixture[str]) -> None:
        args = argparse.Namespace(shell="zsh", output=None)
        run(args)
        captured = capsys.readouterr()
        assert "#compdef openai" in captured.out
        assert "_openai()" in captured.out

    def test_run_fish_prints_to_stdout(self, capsys: pytest.CaptureFixture[str]) -> None:
        args = argparse.Namespace(shell="fish", output=None)
        run(args)
        captured = capsys.readouterr()
        assert "complete -c openai" in captured.out

    def test_run_bash_writes_to_file(self, tmp_path: pathlib.Path) -> None:
        out_file = tmp_path / "openai.bash"
        args = argparse.Namespace(shell="bash", output=str(out_file))
        run(args)
        assert out_file.exists()
        content = out_file.read_text()
        assert "_openai_completions()" in content

    def test_run_zsh_writes_to_file(self, tmp_path: pathlib.Path) -> None:
        out_file = tmp_path / "openai.zsh"
        args = argparse.Namespace(shell="zsh", output=str(out_file))
        run(args)
        assert out_file.exists()
        content = out_file.read_text()
        assert "#compdef openai" in content

    def test_run_fish_writes_to_file(self, tmp_path: pathlib.Path) -> None:
        out_file = tmp_path / "openai.fish"
        args = argparse.Namespace(shell="fish", output=str(out_file))
        run(args)
        assert out_file.exists()
        content = out_file.read_text()
        assert "complete -c openai" in content

    def test_run_file_output_prints_instructions(
        self, capsys: pytest.CaptureFixture[str], tmp_path: pathlib.Path
    ) -> None:
        out_file = tmp_path / "openai.bash"
        args = argparse.Namespace(shell="bash", output=str(out_file))
        run(args)
        captured = capsys.readouterr()
        assert "To enable completions" in captured.out
        assert "~/.bashrc" in captured.out

    def test_run_zsh_file_output_mentions_zshrc(
        self, capsys: pytest.CaptureFixture[str], tmp_path: pathlib.Path
    ) -> None:
        out_file = tmp_path / "openai.zsh"
        args = argparse.Namespace(shell="zsh", output=str(out_file))
        run(args)
        captured = capsys.readouterr()
        assert "To enable completions" in captured.out
        assert "~/.zshrc" in captured.out

    def test_run_fish_file_output_mentions_fish_completions_path(
        self, capsys: pytest.CaptureFixture[str], tmp_path: pathlib.Path
    ) -> None:
        out_file = tmp_path / "openai.fish"
        args = argparse.Namespace(shell="fish", output=str(out_file))
        run(args)
        captured = capsys.readouterr()
        assert "fish/completions" in captured.out

    def test_run_output_file_contains_full_script(self, tmp_path: pathlib.Path) -> None:
        """Written file should contain the full script content."""
        for shell in ("bash", "zsh", "fish"):
            out_file = tmp_path / f"openai.{shell}"
            args = argparse.Namespace(shell=shell, output=str(out_file))
            run(args)
            content = out_file.read_text()
            assert content == COMPLETION_SCRIPTS[shell]


# ---------------------------------------------------------------------------
# Tests: Model list completeness
# ---------------------------------------------------------------------------


class TestModelLists:
    """Verify the model lists are comprehensive and up-to-date."""

    def test_gpt4_models_present(self) -> None:
        for shell, script in COMPLETION_SCRIPTS.items():
            assert "gpt-4o" in script, f"{shell}: missing gpt-4o"
            assert "gpt-4o-mini" in script, f"{shell}: missing gpt-4o-mini"
            assert "gpt-4-turbo" in script, f"{shell}: missing gpt-4-turbo"
            assert "gpt-4" in script, f"{shell}: missing gpt-4"

    def test_reasoning_models_present(self) -> None:
        for shell, script in COMPLETION_SCRIPTS.items():
            assert "o1" in script, f"{shell}: missing o1"
            assert "o1-mini" in script, f"{shell}: missing o1-mini"
            assert "o1-pro" in script, f"{shell}: missing o1-pro"
            assert "o3" in script, f"{shell}: missing o3"
            assert "o3-mini" in script, f"{shell}: missing o3-mini"
            assert "o4-mini" in script, f"{shell}: missing o4-mini"

    def test_image_models_present(self) -> None:
        for shell, script in COMPLETION_SCRIPTS.items():
            assert "dall-e-3" in script, f"{shell}: missing dall-e-3"
            assert "dall-e-2" in script, f"{shell}: missing dall-e-2"

    def test_audio_models_present(self) -> None:
        for shell, script in COMPLETION_SCRIPTS.items():
            assert "whisper-1" in script, f"{shell}: missing whisper-1"
            assert "tts-1" in script, f"{shell}: missing tts-1"
            assert "tts-1-hd" in script, f"{shell}: missing tts-1-hd"

    def test_gpt35_present(self) -> None:
        for shell, script in COMPLETION_SCRIPTS.items():
            assert "gpt-3.5-turbo" in script

    def test_expected_model_count(self) -> None:
        """Each shell script should reference all expected models."""
        for shell, script in COMPLETION_SCRIPTS.items():
            for model in EXPECTED_MODELS:
                assert model in script, f"{shell}: missing model {model}"


# ---------------------------------------------------------------------------
# Tests: Script syntactic sanity
# ---------------------------------------------------------------------------


class TestScriptSyntax:
    """Quick sanity checks that scripts look structurally valid."""

    def test_bash_script_has_matching_braces(self) -> None:
        script = COMPLETION_SCRIPTS["bash"]
        assert script.count("{") == script.count("}")

    def test_zsh_script_has_matching_braces(self) -> None:
        script = COMPLETION_SCRIPTS["zsh"]
        assert script.count("{") == script.count("}")

    def test_bash_no_trailing_whitespace_on_code_lines(self) -> None:
        script = COMPLETION_SCRIPTS["bash"]
        for line in script.splitlines():
            assert line == line.rstrip() or line.startswith("#"), (
                f"Trailing whitespace: {line!r}"
            )

    def test_fish_comments_no_trailing_whitespace(self) -> None:
        script = COMPLETION_SCRIPTS["fish"]
        for line in script.splitlines():
            if line.startswith("#"):
                assert line == line.rstrip(), (
                    f"Trailing whitespace in comment: {line!r}"
                )

    def test_scripts_end_with_newline(self) -> None:
        for shell, script in COMPLETION_SCRIPTS.items():
            assert script.endswith("\n"), f"{shell} script should end with newline"


# ---------------------------------------------------------------------------
# Tests: Option flag presence across shells
# ---------------------------------------------------------------------------


class TestOptionPresence:
    """Verify key CLI options are represented in detailed (zsh/fish) scripts."""

    def test_stream_option_in_detailed_scripts(self) -> None:
        """Bash script is minimal (model/voice/size only); zsh and fish have all options."""
        for shell in ("zsh", "fish"):
            assert "stream" in COMPLETION_SCRIPTS[shell], f"{shell}: missing stream option"

    def test_temperature_option_in_detailed_scripts(self) -> None:
        for shell in ("zsh", "fish"):
            assert "temperature" in COMPLETION_SCRIPTS[shell], f"{shell}: missing temperature option"

    def test_max_tokens_option_in_detailed_scripts(self) -> None:
        for shell in ("zsh", "fish"):
            assert "max-tokens" in COMPLETION_SCRIPTS[shell], f"{shell}: missing max-tokens option"

    def test_prompt_option_in_detailed_scripts(self) -> None:
        for shell in ("zsh", "fish"):
            assert "prompt" in COMPLETION_SCRIPTS[shell], f"{shell}: missing prompt option"
