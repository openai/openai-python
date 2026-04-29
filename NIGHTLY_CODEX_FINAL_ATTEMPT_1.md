Completed the nightly run.

I did not leave a code diff because upstream already has an open duplicate PR for this exact issue: openai/openai-python#2792. Creating another PR would be misleading under the task rules.

I wrote [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md) with the duplicate finding, checks performed, and remaining risk. Final tracked change is only that report; existing untracked `.codex-nightly-prompt.md` and `uv.lock` were left untouched.