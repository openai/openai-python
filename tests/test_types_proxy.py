from __future__ import annotations

import sys
import subprocess


def test_import_openai_does_not_eagerly_import_types() -> None:
    # Run in a clean subprocess to ensure isolated module import state
    code = """
import sys
import openai

# openai.types.batch should NOT be eagerly loaded during `import openai`
assert "openai.types.batch" not in sys.modules, "openai.types.batch was eagerly imported"
assert "openai.types.skill" not in sys.modules, "openai.types.skill was eagerly imported"
assert "openai.types.video" not in sys.modules, "openai.types.video was eagerly imported"

# Accessing a type attribute resolves correctly on demand via lazy loader
batch_cls = openai.types.Batch
assert batch_cls.__name__ == "Batch"
assert "openai.types.batch" in sys.modules

# Accessing a submodule resolves correctly on demand
from openai.types.chat import ChatCompletion
assert ChatCompletion.__name__ == "ChatCompletion"

print("OK")
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert "OK" in result.stdout


def test_types_proxy_attribute_access() -> None:
    import openai
    from openai import types

    assert hasattr(openai.types, "Batch")
    assert hasattr(openai.types, "Model")
    assert hasattr(types, "ChatModel")

    # Verify representations and dir
    assert "Batch" in dir(openai.types)
    assert "ChatModel" in dir(types)
