Added [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md) and left repository code unchanged.

I did not implement a fix because upstream PR `openai/openai-python#2909` is already open and directly addresses issue `#2830` with `retrieve_parsed()`. A new PR from this checkout would duplicate active maintainer review work.

Tests were not run because no code changed. Current untracked files are `.codex-nightly-prompt.md`, `uv.lock`, and `NIGHTLY_REPORT.md`.