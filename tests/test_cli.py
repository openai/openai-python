from __future__ import annotations

import subprocess
import sys


def test_completion_help() -> None:
    """Test that the completion subcommand shows help."""
    result = subprocess.run(
        [sys.executable, "-m", "openai", "completion", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Generate shell completion scripts" in result.stdout


def test_completion_bash() -> None:
    """Test generating bash completion script."""
    result = subprocess.run(
        [sys.executable, "-m", "openai", "completion", "-s", "bash"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "complete -F _openai_completion openai" in result.stdout


def test_completion_zsh() -> None:
    """Test generating zsh completion script."""
    result = subprocess.run(
        [sys.executable, "-m", "openai", "completion", "-s", "zsh"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "#compdef openai" in result.stdout


def test_completion_fish() -> None:
    """Test generating fish completion script."""
    result = subprocess.run(
        [sys.executable, "-m", "openai", "completion", "-s", "fish"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "complete -f -c openai" in result.stdout


def test_completion_powershell() -> None:
    """Test generating PowerShell completion script."""
    result = subprocess.run(
        [sys.executable, "-m", "openai", "completion", "-s", "powershell"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Register-ArgumentCompleter" in result.stdout


def test_completion_missing_shell() -> None:
    """Test that completion requires --shell flag."""
    result = subprocess.run(
        [sys.executable, "-m", "openai", "completion"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_completion_bash_source() -> None:
    """Test bash completion source."""
    import os

    env = os.environ.copy()
    env["OPENAI_COMPLETE"] = "bash_source"
    result = subprocess.run(
        [sys.executable, "-m", "openai", ""],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "completion" in result.stdout
