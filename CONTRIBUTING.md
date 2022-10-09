# Development
This section contains technical instructions & hints for the contributors.

## Git hooks
Each time new code is pushed to this repository, Github Actions (CI) run several checks on it. You can run these checks locally without waiting for the CI by following these steps:
1. Install `pre-commit` (https://pre-commit.com/#install)
2. Install the Git hooks by running `pre-commit install`

As soon as those two steps are completed, Git hooks will be executed automatically at every new commit. Alternatively, Git hooks can be run manually with `pre-commit run --all-files`, or skipped (which is not recommended) with `git commit --no-verify`.

Note: The following tools must be passed, failure output should have more information:
- Checks for hardcoded credentials (Gitleaks)
- Alphabetically sorting of the imports checks (isort)
- Style and quality checks (flake8 and black)
- Common misspelling checks codespell

```
$ git commit -m "test commit"
Detect hardcoded secrets.................................................Passed
isort....................................................................Passed
flake8...................................................................Passed
black....................................................................Passed
codespell................................................................Passed
[main 4b98c17] test commit
 1 files changed, 3 insertions(+), 2 deletions(-)
 create mode 100644 openai/api_requestor.py
```