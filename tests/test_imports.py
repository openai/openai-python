from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path


def run_python(script: str) -> list[str]:
    env = os.environ.copy()
    src = str(Path(__file__).parents[1] / "src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")

    output = subprocess.check_output([sys.executable, "-c", script], env=env, text=True)
    return output.strip().splitlines()


def test_import_openai_does_not_import_types() -> None:
    assert run_python(
        """
import sys
import openai
print("openai.types" in sys.modules)
print(type(openai.types).__name__)
print("openai.types" in sys.modules)
print(openai.types.ChatModel is not None)
print("openai.types" in sys.modules)
"""
    ) == ["False", "TypesProxy", "False", "True", "True"]
