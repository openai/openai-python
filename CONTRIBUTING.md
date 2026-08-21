## Setting up the environment

The minimum supported runtime, contributor toolchain, CI matrix, and release
rules are documented in [PYTHON_VERSION_POLICY.md](./PYTHON_VERSION_POLICY.md).
Changes to the minimum Python version must keep those surfaces synchronized and
must include a release note naming the final compatible SDK release.

### With uv

We use [uv](https://docs.astral.sh/uv/) to manage Python, dependencies, and builds.
Install uv 0.12.1 or newer, Node.js at the version in `.node-version`, and
the exact pnpm version in `package.json` (`npm install --global pnpm@11.19.0`).
The Node toolchain is for repository development only, not SDK users or builds.
Then run:

```sh
$ ./scripts/bootstrap
```

This installs all SDK extras and Python development tools from `uv.lock`, plus
the contributor tools from `pnpm-lock.yaml`. Bootstrap requires an already
installed Node.js and pnpm; it does not download or switch those tools for you.
Run a
command with `uv run --locked --all-extras`, or activate `.venv` in your shell.
Use `uv lock` after changing dependencies, and commit the updated `uv.lock`.
It is the authoritative lockfile; `uv export` can produce a requirements file
for tools that need one.

For Node tooling updates, edit `package.json`, run
`pnpm install --lockfile-only --ignore-scripts`, review the dependency and
integrity changes, and commit `pnpm-lock.yaml`. Normal bootstrap uses a frozen
lockfile. pnpm rejects releases that have not cleared the eight-day cooldown,
including packages whose registry metadata omits their publication date.
Pyright runs the local Microsoft package and never invokes npm or
downloads a runtime. Do not use `npx`, `pnpm dlx`, or Corepack auto-downloads.

The default environment uses Pydantic v2. `./scripts/test` also runs the
Pydantic-v1 suite in a separate, locked environment. To run that lane alone,
use `./scripts/test-pydantic-v1`.

### Dependency update policy

Routine Python, Node-tooling, and GitHub Actions updates have an eight-day cooldown. uv also
excludes Python distribution artifacts uploaded within the last eight days.
Dependabot security updates remain enabled and are exempt from Dependabot's
version-update cooldown.

The committed `uv.lock` must remain usable outside a contributor's environment:
registry sources use `https://pypi.org/simple`, and distribution artifacts use
hashed `https://files.pythonhosted.org/packages/` URLs. If a managed registry
rewrites those locations, keep its required local security checks enabled. Use
dependency-update automation or an approved public-lockfile repair that matches
each exact filename and SHA-256 against upstream metadata; do not substitute
hosts blindly or commit private registry URLs. The public-source regression test
in `tests/test_uv_workflows.py` checks this without making network requests.

Do not lower a security-fixed minimum or downgrade a patched lock entry to make
the cooldown pass. If an urgent fix is too new for uv, request SDK CODEOWNER
review of the advisory, exact fixed version, upstream provenance, artifact
hashes, and affected dependency paths. The reviewed PR may add a temporary,
package-specific `tool.uv.exclude-newer-package` cutoff using a fixed UTC
timestamp just after the approved artifacts were uploaded. Update only the
approved package (for example, `uv lock --upgrade-package 'package==version'`),
retain the security floor in published metadata where applicable, and review
the resulting lock diff. Record the advisory and an expiry/removal date in the
PR and remove the exception once those artifacts are eight days old. Do not
disable the global cutoff or exempt unrelated packages.

For an urgent Node-tooling security fix, obtain the same CODEOWNER review and
use a temporary, exact `package@version` entry in pnpm's
`minimumReleaseAgeExclude`. Record the public advisory, integrity/provenance,
and removal date in the PR. Do not lower an existing security-fixed version,
disable the global age policy, or enable lifecycle scripts globally.

See [uv's package-specific cutoff documentation](https://docs.astral.sh/uv/reference/settings/#exclude-newer-package)
and [Dependabot's cooldown policy](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference#cooldown).

## Modifying/Adding code

Most of the SDK is generated code. Modifications to code will be persisted between generations, but may
result in merge conflicts between manual patches and changes from the generator. The generator will never
modify the contents of the `src/openai/lib/` and `examples/` directories.

## Custom-code budget

The custom-code budget counts additions plus deletions in the remaining patch
against verified generated output. `.castiron-ratchet.json` defines this repository's
ceiling. CI uses the checker and budget on main, not the PR's proposed versions.

Budget changes must be in a separate PR modifying **only `.castiron-ratchet.json`**.
Justify the current usage, proposed ceiling, and why fixing generation is not
appropriate in the PR description. Increases require a **human approving review**
and must merge before an SDK change relies on them. Agents may draft proposals,
but must not approve increases or bypass the gate. Keep default CODEOWNERS.
Lower the ceiling after cleanup while retaining headroom; decreases must still
fit the measured usage.

See [custom-code technical details](scripts/castiron/CUSTOM_CODE.md) for accounting,
local checks, trusted CI, and activation instructions.

## Security requirements for contributions

- Never commit API or admin keys, bearer tokens, webhook secrets, cloud
  credentials, private keys, publishing credentials, or `.env` files. Load real
  credentials from environment variables such as `OPENAI_API_KEY`,
  `OPENAI_ADMIN_KEY`, and `OPENAI_WEBHOOK_SECRET`; use clearly fake values and
  sanitized data in examples, tests, fixtures, and recorded responses.
- Redact `Authorization` and `api-key` headers, other credentials, and customer
  request or response data from logs, exceptions, snapshots, and debug output.
  Prefer the mock server or mocked HTTP transport over live credentials in tests.
- Review direct and transitive dependency changes, package provenance, build or
  install hooks, and diffs to `pyproject.toml`, optional extras,
  `uv.lock`, and the build dependency group.
- Pin third-party GitHub Actions to reviewed full commit SHAs, minimize job
  permissions, and keep secrets and write-capable tokens away from untrusted
  pull-request code. Protect release-app credentials and preserve the separate
  build and upload jobs, protected publishing environment, and PyPI Trusted
  Publishing. Limit OIDC access to the trusted publishing job.
- Request SDK CODEOWNER review for authentication, X.509, webhook verification,
  network destinations, redirects, TLS, cloud metadata, file handling,
  serialization, dependency, CI, and release changes. Add synchronous and
  asynchronous regression tests as applicable, including credential redaction
  and invalid signatures.
- Report suspected vulnerabilities privately through the process in
  [SECURITY.md](./SECURITY.md), never through public issues or pull requests.

## Adding and running examples

All files in the `examples/` directory are not modified by the generator and can be freely edited or added to.

```py
# add an example to examples/<your-example>.py

#!/usr/bin/env -S uv run python
…
```

```sh
$ chmod +x examples/<your-example>.py
# run the example against your api
$ ./examples/<your-example>.py
```

## Using the repository from source

If you’d like to use the repository from source, you can either install from git or link to a cloned repository:

To install via git:

```sh
$ pip install git+ssh://git@github.com/openai/openai-python.git
```

Alternatively, you can build from source and install the wheel file:

Building this package will create two files in the `dist/` directory, a `.tar.gz` containing the source files and a `.whl` that can be used to install the package efficiently.

To create a distributable version of the library, all you have to do is run this command:

```sh
$ ./scripts/build
```

The build script exports hash-checked build requirements from `uv.lock` before
building the sdist and wheel. It does not install the development toolchain.

Then to install:

```sh
$ pip install ./path-to-wheel-file.whl
```

## Running tests

Most tests require you to [set up a mock server](https://github.com/dgellow/steady) against the OpenAPI spec to run the tests.

`./scripts/bootstrap` installs the locked Steady package and its platform
binary. `./scripts/test` starts it automatically when no mock server is running.
Neither `./scripts/test` nor `./scripts/mock` downloads Node tools. If the local
tool is missing, rerun bootstrap. `TEST_API_BASE_URL` and an already-running
mock server remain supported. To start the server yourself:

```sh
$ ./scripts/mock
```

```sh
$ ./scripts/test
```

## Linting and formatting

This repository uses [Ruff](https://github.com/astral-sh/ruff) to lint and format Python code.

To lint:

```sh
$ ./scripts/lint
```

To format and fix all ruff issues automatically:

```sh
$ ./scripts/format
```

## Publishing and releases

Changes made to this repository via the automated release PR pipeline should publish to PyPI automatically. If
the changes aren't made through the automated pipeline, you may want to make releases manually.

### Publish with a GitHub workflow

You can release to package managers by using [the `Publish PyPI` GitHub action](https://www.github.com/openai/openai-python/actions/workflows/publish-pypi.yml). PyPI publishing uses Trusted Publishing, so the PyPI project must trust this repository's GitHub Actions workflow and the `publish` environment.

### Publish manually

If you need to retry a PyPI release, use the `Publish PyPI` GitHub action. Local manual publishing is not the standard release path because the GitHub workflow uses OIDC instead of a long-lived PyPI token.
