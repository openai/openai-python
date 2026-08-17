## Setting up the environment

The minimum supported runtime, contributor toolchain, CI matrix, and release
rules are documented in [PYTHON_VERSION_POLICY.md](./PYTHON_VERSION_POLICY.md).
Changes to the minimum Python version must keep those surfaces synchronized and
must include a release note naming the final compatible SDK release.

### With Rye

We use [Rye](https://rye.astral.sh/) to manage dependencies because it will automatically provision a Python environment with the expected Python version. To set it up, run:

```sh
$ ./scripts/bootstrap
```

Or [install Rye manually](https://rye.astral.sh/guide/installation/) and run:

```sh
$ rye sync --all-features
```

You can then run scripts using `rye run python script.py` or by activating the virtual environment:

```sh
# Activate the virtual environment - https://docs.python.org/3/library/venv.html#how-venvs-work
$ source .venv/bin/activate

# now you can omit the `rye run` prefix
$ python script.py
```

### Without Rye

Alternatively if you don't want to install `Rye`, you can stick with the standard `pip` setup by ensuring you have the Python version specified in `.python-version`, create a virtual environment however you desire and then install dependencies using this command:

```sh
$ pip install -r requirements-dev.lock
```

## Modifying/Adding code

Most of the SDK is generated code. Modifications to code will be persisted between generations, but may
result in merge conflicts between manual patches and changes from the generator. The generator will never
modify the contents of the `src/openai/lib/` and `examples/` directories.

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
  `requirements.lock`, `requirements-dev.lock`, and `uv.lock`.
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

#!/usr/bin/env -S rye run python
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
$ rye build
# or
$ python -m build
```

Then to install:

```sh
$ pip install ./path-to-wheel-file.whl
```

## Running tests

Most tests require you to [set up a mock server](https://github.com/dgellow/steady) against the OpenAPI spec to run the tests.

```sh
$ ./scripts/mock
```

```sh
$ ./scripts/test
```

## Linting and formatting

This repository uses [ruff](https://github.com/astral-sh/ruff) and
[black](https://github.com/psf/black) to format the code in the repository.

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
