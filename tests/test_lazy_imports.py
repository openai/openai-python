from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import openai


def _run_fresh_import(source: str) -> dict[str, object]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-c", source],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return json.loads(result.stdout)


def test_top_level_import_defers_optional_subtrees() -> None:
    # `import openai` should no longer eagerly build the Assistants ``beta`` type
    # tree (the largest unused subtree) or the streaming helpers. They must load
    # only on first use.
    imported = _run_fresh_import(
        """
import json
import sys
import openai

print(json.dumps({
    "beta": "openai.types.beta" in sys.modules,
    "streaming": "openai.lib.streaming" in sys.modules,
}))
"""
    )

    assert imported == {"beta": False, "streaming": False}


def test_lazy_top_level_exports_preserve_public_objects() -> None:
    from openai.lib import pydantic_function_tool
    from openai.lib.streaming import AssistantEventHandler, AsyncAssistantEventHandler

    assert openai.pydantic_function_tool is pydantic_function_tool
    assert openai.AssistantEventHandler is AssistantEventHandler
    assert openai.AsyncAssistantEventHandler is AsyncAssistantEventHandler


def test_types_proxy_loads_real_module_on_access() -> None:
    imported = _run_fresh_import(
        """
import json
import sys
import openai

batch = openai.types.Batch
print(json.dumps({
    "name": batch.__name__,
    "types": "openai.types" in sys.modules,
}))
"""
    )

    assert imported == {"name": "Batch", "types": True}
