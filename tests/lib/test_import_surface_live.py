from __future__ import annotations

import os
import sys
import importlib

import pytest


def _openai_modules() -> dict[str, object]:
    return {name: mod for name, mod in sys.modules.items() if name == "openai" or name.startswith("openai.")}


def _restore_openai_modules(original_modules: dict[str, object]) -> None:
    for name in list(sys.modules):
        if name == "openai" or name.startswith("openai."):
            sys.modules.pop(name, None)
    sys.modules.update(original_modules)


@pytest.mark.skipif(os.environ.get("OPENAI_LIVE") != "1", reason="requires OPENAI_LIVE=1")
@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="requires OPENAI_API_KEY")
def test_eager_import_with_live_token_allows_real_request(monkeypatch) -> None:
    # Exercise eager mode in a real SDK flow behind explicit live-test flags.
    monkeypatch.setenv("OPENAI_EAGER_IMPORT", "1")
    original_modules = _openai_modules()

    for name in original_modules:
        sys.modules.pop(name, None)

    client = None
    try:
        openai = importlib.import_module("openai")

        assert "openai.types" in sys.modules
        assert "openai.lib.azure" in sys.modules
        assert "AzureOpenAI" in openai.__dict__

        client = openai.OpenAI(timeout=20.0)
        page = client.models.list()
        assert page.data is not None
    finally:
        if client is not None:
            client.close()
        _restore_openai_modules(original_modules)
