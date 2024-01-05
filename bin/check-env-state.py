"""Script that exits 1 if the current environment is not
in sync with the `requirements-dev.lock` file.
"""

from pathlib import Path

import importlib_metadata


def should_run_sync() -> bool:
    dev_lock = Path(__file__).parent.parent.joinpath("requirements-dev.lock")

    for line in dev_lock.read_text().splitlines():
        if not line or line.startswith("#") or line.startswith("-e"):
            continue

        dep, lock_version = line.split("==")

        try:
            version = importlib_metadata.version(dep)

            if lock_version != version:
                print(f"mismatch for {dep} current={version} lock={lock_version}")
                return True
        except Exception:
            print(f"could not import {dep}")
            return True

    return False


def main() -> None:
    if should_run_sync():
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()
