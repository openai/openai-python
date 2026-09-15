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
    assert "batch" in dir(openai.types)
    assert "chat_model" in dir(types)


def test_types_wildcard_import_compatibility() -> None:
    # Run in a clean subprocess to test `from openai.types import *`
    code = """
from openai.types import *

# Verify type classes are imported
assert Batch is not None
assert Image is not None
assert ChatModel is not None
assert Model is not None

# Verify submodules are also exposed in wildcard import
assert batch is not None
assert image is not None
assert chat_model is not None
assert chat is not None

# Verify submodule contents and identity
assert batch.Batch is Batch
assert image.Image is Image

print("OK")
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert "OK" in result.stdout


def test_types_dir_includes_globals_and_lazy_exports() -> None:
    import openai.types

    dir_names = dir(openai.types)

    # Standard module attributes
    assert "__name__" in dir_names
    assert "__package__" in dir_names
    assert "__all__" in dir_names

    # Lazy type classes
    assert "Batch" in dir_names
    assert "Model" in dir_names
    assert "ChatModel" in dir_names

    # Submodules
    assert "batch" in dir_names
    assert "image" in dir_names
    assert "chat_model" in dir_names
    assert "chat" in dir_names

    # Repeated lazy access identity
    assert openai.types.Batch is openai.types.Batch
    assert openai.types.batch is openai.types.batch
