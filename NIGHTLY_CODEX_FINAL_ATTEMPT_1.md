Stopped without source changes because the exact fix is already covered by active upstream PRs:

- https://github.com/openai/openai-python/pull/2676
- https://github.com/openai/openai-python/pull/2873

I verified the local root cause is still present (`lru_cache(maxsize=None)` around `pydantic.TypeAdapter` in `src/openai/_models.py`) and wrote [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md) with the investigation, commands run, and remaining risk.

No formal pytest target was run because no source/test change was made. Pre-existing untracked files `.codex-nightly-prompt.md` and `uv.lock` were left untouched.