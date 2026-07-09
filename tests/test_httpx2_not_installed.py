"""Graceful-degradation guard for when the `httpx2` extra is NOT installed.

Runs in a subprocess with `httpx2` forced absent (``sys.modules["httpx2"] = None``
makes ``import httpx2`` raise ``ImportError``), so it exercises the same path a
Python 3.9 / no-extra install hits -- regardless of whether httpx2 happens to be
installed in the current test environment. This is the one httpx2 test that is
meaningful when the extra is absent, so unlike ``test_httpx2_client.py`` it does
not ``importorskip`` it.
"""

from __future__ import annotations

import sys
import subprocess

_PROGRAM = """
import sys

# Simulate the httpx2 extra not being installed.
sys.modules["httpx2"] = None

import httpx
import openai
from openai import DefaultHttpx2Client, DefaultAsyncHttpx2Client

# 1. importing openai must still work with httpx2 absent (zero behaviour change)
assert openai.OpenAI is not None

# 2. the default httpx2 client factories must raise a helpful RuntimeError
for factory in (DefaultHttpx2Client, DefaultAsyncHttpx2Client):
    try:
        factory()
    except RuntimeError as exc:
        assert "httpx2" in str(exc), exc
    else:
        raise AssertionError(factory.__name__ + " did not raise RuntimeError when httpx2 is absent")

# 3. a plain classic-httpx client is still accepted
openai.OpenAI(api_key="sk-test", http_client=httpx.Client()).close()

print("OK")
"""


def test_import_and_stub_without_httpx2() -> None:
    result = subprocess.run(
        [sys.executable, "-c", _PROGRAM],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    assert result.stdout.strip().splitlines()[-1] == "OK"
