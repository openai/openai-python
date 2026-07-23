# Python Version Support Policy

The OpenAI Python SDK supports every fully released CPython version that has
not reached upstream end of life. The oldest supported version is declared by
`requires-python` in [`pyproject.toml`](pyproject.toml), documented in the
README, and tested on every pull request.

The SDK team may retain the most recently retired CPython version for up to six
months when the dependency graph, platform support, and security posture allow
it. This grace period is discretionary, is not an LTS commitment, and may end
early because of security, dependency, platform, or tooling requirements.
Active grace must be recorded below with an explicit end date and reason.

Minimum Python version increases:

- ship in an SDK minor release, not a normal patch release;
- are documented in the README and release notes;
- identify the final SDK release installable on the retired Python version;
- require approval from the SDK CODEOWNERS; and
- do not require a new SDK major version when documented APIs remain compatible
  on supported runtimes and `Requires-Python` prevents incompatible installs.

Removing a documented framework integration or public behavior is evaluated
separately. If supported users must change application code and no
compatibility layer preserves the contract, the change requires a major
release by default. Patch-level runtime removals are reserved for urgent
security exceptions and require unusually prominent communication.

The SDK team reviews this policy within 30 days of every October CPython
release and scheduled end of life. It does not normally raise the Python floor
more than once in a 12-month period. New stable CPython releases should be
added within 30 days of general availability when dependencies and CI images
are ready.

### Testing

- Pull requests run the high-value suite on the minimum and current stable
  CPython releases.
- A scheduled and manually dispatchable workflow tests every supported CPython
  release.
- The next CPython prerelease is allowed to fail until it becomes stable, with
  coverage beginning no later than its first release candidate.
- Built wheels and source distributions are checked for the authoritative
  `Requires-Python` value, and a resolver running on the retired interpreter
  must reject the new artifact.

### Automated review

The monthly Codex review snapshots the official Python release-cycle data and
public PyPI download distribution before the model runs. Codex compares that
data with package metadata, classifiers, CI, documentation, and this policy.
When a release, end of life, grace deadline, usage signal, or repository drift
requires a maintainer decision, a separate credential-free job opens or
refreshes one GitHub issue.

The review never edits `Requires-Python`, pushes a branch, or merges a change.
The normal SDK review and release process remains authoritative.

### Current compatibility

| SDK version | Python requirement |
| --- | --- |
| Next minor release (currently expected v2.49.0) | Python 3.10 or later |
| v2.48.0 | Final release installable on Python 3.9 |

The fully released upstream-supported matrix is currently Python 3.10 through
3.14. Python 3.15 is covered as an allowed-failure prerelease. There is no
active grace period.

Previously published SDK versions remain available. Unsupported Python
versions and older SDK releases receive no guaranteed fixes or security
backports. Users who need current SDK, dependency, and security fixes must use
a supported Python runtime.

For the upstream lifecycle and installer behavior, see the
[CPython version status](https://devguide.python.org/versions/),
[core metadata specification](https://packaging.python.org/en/latest/specifications/core-metadata/#requires-python),
and [PyPA guide to dropping old Python versions](https://packaging.python.org/en/latest/guides/dropping-older-python-versions/).
