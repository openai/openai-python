"""Check receipt verifier startup without executing vfkit or Docker."""

from __future__ import annotations

import os
import json
import stat
import tempfile
import subprocess
from typing import Any
from pathlib import Path
from unittest.mock import patch

from guest import Guest

from openai.lib.computer import ComputerUseError


def main() -> None:
    sentinels = {
        "OPENAI_API_KEY": "fixture-openai",
        "BROWSERBASE_API_KEY": "fixture-browserbase",
        "E2B_API_KEY": "fixture-e2b",
        "DAYTONA_API_KEY": "fixture-daytona",
        "PYTHONPATH": "fixture-python",
        "HTTP_PROXY": "fixture-proxy",
        "DOCKER_CONTEXT": "fixture-context",
    }
    with tempfile.TemporaryDirectory(prefix="sdk-guest-env-") as directory:
        root = Path(directory)
        root.chmod(stat.S_IRWXU)
        (root / "runs").mkdir(mode=0o700)
        launches: list[tuple[list[str], dict[str, str]]] = []

        def verifier(command: list[str], **options: Any) -> subprocess.Popen[bytes]:
            launches.append((command, options.get("env", {})))
            raise OSError("Synthetic receipt verifier refusal")

        with patch.dict(os.environ, sentinels), patch("guest.subprocess.Popen", verifier):
            try:
                Guest(root)
            except ComputerUseError:
                pass
            else:
                raise AssertionError("Fixture verifier must refuse before a guest starts")
        assert len(launches) == 1
        args, env = launches[0]
        assert args[1:3] == ["-I", "-S"]
        assert env["TMPDIR"] == str(root) and env["LANG"] == "C"
        assert set(env) == {"PATH", "LANG", "TMPDIR"}
        assert not (set(sentinels) & set(env))
        print(json.dumps({"checks": 1, "api_calls": 0, "vendor_calls": 0, "vm_starts": 0}))


if __name__ == "__main__":
    main()
