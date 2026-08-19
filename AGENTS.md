# Repository Guidance

## Generated SDK

Most SDK source is generated from the OpenAI API schema. Follow `CONTRIBUTING.md` before
changing generated files. Handwritten policy, automation, tests, and examples
should remain small and should not alter exported SDK APIs unless the change
explicitly requires it.

## Security requirements for coding agents

- Never commit real API or admin keys, bearer tokens, webhook secrets, cloud
  credentials, X.509 private keys, release credentials, or `.env` files. Read
  `OPENAI_API_KEY`, `OPENAI_ADMIN_KEY`, `OPENAI_WEBHOOK_SECRET`, and other
  credentials from the environment; use clearly fake examples and fixtures.
- Redact credentials, `Authorization` and `api-key` headers, customer data, and
  sensitive request or response bodies from logs, exceptions, snapshots, and
  test output. Clearly fake or sanitized fixtures and safe `APIError.body`
  diagnostics may remain. Preserve existing sensitive-header filtering,
  including debug logging.
- Review direct and transitive dependency changes in `pyproject.toml`, optional
  extras, dependency groups, and `uv.lock`. Check
  package provenance, build backends, and install scripts before accepting or
  running them.
- Pin third-party GitHub Actions to reviewed full commit SHAs. Minimize
  job-level token permissions and never expose secrets or write-capable tokens
  to untrusted pull-request code.
- Preserve separate build and publish jobs, protected release credentials, and
  PyPI Trusted Publishing. Grant `id-token: write` only to the trusted,
  upload-only publishing job; do not introduce long-lived PyPI tokens.
- Obtain SDK CODEOWNER review and add focused synchronous and asynchronous
  security regression tests, as applicable, for changes to authentication,
  X.509 or webhook verification, HTTP destinations, redirects, proxies, TLS,
  cloud metadata, file uploads, serialization, dependencies, GitHub Actions,
  or release workflows.
- Report suspected vulnerabilities privately as described in `SECURITY.md`;
  never disclose them in public issues, pull requests, or logs.

## Python version policy

- `requires-python` in `pyproject.toml` is the authoritative technical minimum.
- `PYTHON_VERSION_POLICY.md` is the human-readable support and release policy.
- Support every fully released, non-EOL CPython line. A documented grace period
  may temporarily add the most recently retired line.
- Keep `requires-python`, classifiers, dependency markers, README requirements,
  static-analysis targets, `.python-version`, and CI synchronized.
- Do not combine a minimum-Python change with unrelated SDK or dependency
  upgrades.

## Changing the minimum Python version

1. Update `pyproject.toml`, `.python-version`, the lock files, README,
   `CONTRIBUTING.md`, and `PYTHON_VERSION_POLICY.md`.
2. Remove dependency branches that only served the retired runtime.
3. Update minimum/current and full-matrix CI coverage.
4. Build both distributions and validate their `Requires-Python` metadata and
   old-interpreter rejection behavior.
5. Add a `## Release note` section to the pull request description naming the
   new minimum and final compatible SDK release. Do not promise security
   backports for the old release.
6. Obtain SDK CODEOWNER approval.

The deterministic Python policy check proves repository surfaces agree. It
does not decide whether an EOL grace period or floor increase is appropriate.

## Automation map

- `.github/workflows/ci.yml`
  - On pull requests and branch pushes: lint, build, metadata validation, and
    tests on the minimum and current stable Python releases.
  - Nightly and manually: smoke-tests every supported Python release and the
    allowed-failure prerelease.
- `.github/workflows/python-version-review.yml`
  - Monthly on the default branch: snapshots official CPython lifecycle data
    plus the public PyPI Python-minor distribution and asks Codex for a policy
    review.
  - Runs a pinned Codex runtime as an unprivileged user with no command network
    access and read-only repository permissions.
  - Codex cannot edit the repository or call GitHub. A separate job with no
    OpenAI credential opens or refreshes one issue only when action is needed.
  - Never changes the Python floor or merges code automatically.

## Validation

Before publishing a Python-version change, run:

```sh
uv lock
uv lock --check
./scripts/build
uv run --locked --all-extras python scripts/check-python-version-policy.py
uv run --locked --all-extras python scripts/utils/validate-python-version-wheel.py
python3.9 scripts/utils/validate-python-version-wheel.py --check-python-39
uv run --locked --all-extras python scripts/utils/validate-bedrock-wheel.py
uv run --locked --all-extras python scripts/utils/validate-httpx2-wheel.py
./scripts/lint
./scripts/test
```

Also run the scheduled compatibility matrix before release.
