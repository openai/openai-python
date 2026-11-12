# Repository Guidance

<a id="generated-file-ownership"></a>

## Generated SDK

Most SDK source is generated from the OpenAI API schema. Before editing, follow [Modifying/Adding code](CONTRIBUTING.md#modifyingadding-code) to identify schema/generator/handwritten ownership. Keep handwritten policy, automation, tests, and examples small; alter exported APIs only when explicitly required.

## Security requirements for coding agents

Read and apply [contributor security requirements](CONTRIBUTING.md#security-requirements-for-contributions) for credentials, synthetic fixtures, redaction, dependency provenance/hooks, pinned actions, CI isolation, and publishing. Follow [SECURITY.md](SECURITY.md) for private reporting; never disclose vulnerabilities in public issues, PRs, or logs.

- Redact sensitive data from test output; preserve sensitive-header filtering, including debug logs. Clearly fake/sanitized fixtures and safe `APIError.body` diagnostics may remain.
- Review all dependency groups, direct/transitive packages, extras, `uv.lock`, build backends, and install hooks before accepting or executing them.
- Keep build/publish jobs separate; grant `id-token: write` only to the trusted upload-only job with protected credentials and PyPI Trusted Publishing. No long-lived PyPI tokens.
- Obtain SDK CODEOWNER review and focused sync/async security regressions, as applicable, for the contributor guide's sensitive-change categories, including proxies.

## Python version policy

Read [PYTHON_VERSION_POLICY.md](PYTHON_VERSION_POLICY.md) for support, grace periods, release rules, and testing. `pyproject.toml#requires-python` owns the technical minimum. Keep classifiers, dependency markers, README requirements, analysis targets, `.python-version`, and CI synchronized; separate floor changes from unrelated SDK/dependency upgrades.

## Changing the minimum Python version

1. Update `pyproject.toml`, `.python-version`, locks, README, `CONTRIBUTING.md`, and `PYTHON_VERSION_POLICY.md`; remove dependency branches serving only the retired runtime.
2. Update minimum/current and full-matrix CI; build both distributions and validate `Requires-Python` metadata and old-interpreter rejection.
3. Add a `## Release note` PR section naming the new minimum and final compatible SDK release; do not promise security backports.
4. Obtain SDK CODEOWNER approval.

The deterministic policy check proves consistency, not whether grace or a floor increase is appropriate.

## Automation map

- [ci.yml](.github/workflows/ci.yml): PR/branch-push lint, build, metadata, and minimum/current tests; nightly/manual supported-version smoke matrix plus allowed-failure prerelease.
- [python-version-review.yml](.github/workflows/python-version-review.yml): monthly default-branch review of official CPython lifecycle and public PyPI minor-version usage snapshots. Pinned Codex runs unprivileged, without command network access, with read-only repo permissions and no repository edits/GitHub calls. A separate job without OpenAI credentials opens/refreshes one issue only when needed. Never change the floor or merge automatically.

## Validation

Before publishing Python-version changes, run:

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

Run the scheduled compatibility matrix before release.

## Large-payload compatibility

Large JSON bodies and streaming events are legitimate Responses, Chat Completions, and other API payloads, not inherently malformed/hostile. No arbitrary body/event/line caps: prefer incremental processing, amortized-linear buffering, cleanup, and caller cancellation. New rejection limits require an explicit owner-approved API contract and review of supported payloads/transports.

Use deterministic public-entrypoint tests with large synthetic in-memory payloads, not committed captures or live image generation. High memory use is intentional: do not shrink payloads or raise client limits to pass. Cover main JSON/streaming categories and run large cases sequentially. Fixture size is a regression probe, not an API maximum.
