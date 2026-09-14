from __future__ import annotations

import sys
import typing
import subprocess

import pytest

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
    # `openai.lib.streaming` is only needed by callers using the Assistants API,
    # and it reaches `openai.types.beta`, so importing the package must not pull
    # the namespace in.
    modules = _modules_after_import_openai()

    assert "openai" in modules
    assert not [module for module in modules if module.startswith("openai.types.beta")]


def test_assistant_event_handlers_are_still_exported() -> None:
    assert openai.AssistantEventHandler.__name__ == "AssistantEventHandler"
    assert openai.AsyncAssistantEventHandler.__name__ == "AsyncAssistantEventHandler"


def test_handler_annotations_stay_resolvable() -> None:
    # Deferring the module must not make the handlers' postponed annotations
    # unresolvable: `get_type_hints` has to keep working for annotation-aware
    # integrations and documentation tooling.
    for name in ("on_event", "on_run_step_delta", "on_tool_call_delta"):
        hints = typing.get_type_hints(getattr(openai.AssistantEventHandler, name))
        assert "return" in hints


def test_unknown_attribute_still_raises_attribute_error() -> None:
    with pytest.raises(AttributeError, match="definitely_not_an_export"):
        openai.definitely_not_an_export  # type: ignore[attr-defined]  # noqa: B018
