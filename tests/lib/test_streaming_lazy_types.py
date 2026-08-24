from __future__ import annotations

import sys
import subprocess

import openai


def _modules_after_import_openai() -> set[str]:
    """Return the module names loaded by a bare `import openai` in a fresh interpreter."""
    output = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys\nimport openai\nprint('\\n'.join(sys.modules))\n",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return set(output.split())


def test_import_openai_does_not_load_beta_types() -> None:
    # `openai.lib.streaming` only needs `openai.types.beta` for annotations and for two
    # narrow runtime paths, so importing the package must not pull the namespace in.
    modules = _modules_after_import_openai()

    assert "openai" in modules
    assert not [module for module in modules if module.startswith("openai.types.beta")]


def test_assistant_event_handlers_are_still_eagerly_exported() -> None:
    assert openai.AssistantEventHandler.__name__ == "AssistantEventHandler"
    assert openai.AsyncAssistantEventHandler.__name__ == "AsyncAssistantEventHandler"
