"""Verify compiler-owned files against their generated inventory."""

from __future__ import annotations

import sys
import json
import hashlib
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    inventory = json.loads((root / "scripts/castiron/generated-files.json").read_text())
    if inventory["schema_version"] != 1 or not inventory["files"]:
        sys.stderr.write("Unsupported or empty generated-file inventory.\n")
        return 1

    changed: list[str] = []
    for name, expected in inventory["files"].items():
        relative = Path(name)
        path = root / relative
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or any(root.joinpath(*relative.parts[:i]).is_symlink() for i in range(1, len(relative.parts) + 1))
            or not path.is_file()
        ):
            changed.append(name)
            continue
        mode = "100755" if path.stat().st_mode & 0o111 else "100644"
        if mode != expected["mode"] or hashlib.sha256(path.read_bytes()).hexdigest() != expected["sha256"]:
            changed.append(name)

    if changed:
        sys.stderr.write("Generated files differ from their inventory:\n")
        for name in sorted(changed):
            sys.stderr.write(f"  {name!r}\n")
        sys.stderr.write("Change the inputs/compiler and regenerate; do not hand-edit generated files or hashes.\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
