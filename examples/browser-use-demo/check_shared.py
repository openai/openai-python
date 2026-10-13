"""Compare the private fixture spec and dashboard assets in two SDK source archives."""

import hashlib
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("node_sdk", type=Path, help="Root of the Node SDK source archive or checkout")
args = parser.parse_args()
here = Path(__file__).resolve().parent
node = args.node_sdk / "examples" / "browser-use-demo"
for name in ("index.html", "fixture.html", "notes.html", "tasks.json"):
    python_bytes = (here / name).read_bytes()
    node_bytes = (node / name).read_bytes()
    if python_bytes != node_bytes:
        raise SystemExit(f"Different Fieldwork asset: {name}")
    print(f"{hashlib.sha256(python_bytes).hexdigest()}  {name}")
