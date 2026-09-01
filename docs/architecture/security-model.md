# Security Model

This is the canonical repository-owned threat model for Codex Security scans of
the OpenAI Python SDK. Use this document from the scanned revision as the
authority for trust boundaries, attacker capabilities, reportability, and
severity calibration. [`SECURITY.md`](../../SECURITY.md) remains the authority
for coordinated disclosure instructions.

## Overview

The repository publishes the official `openai` Python library. It is a
caller-owned client library, not a hosted multi-tenant service: application
code constructs synchronous or asynchronous clients, supplies credentials and
request data, sends HTTPS or WebSocket requests to an API endpoint, and parses
JSON, SSE, or WebSocket responses into SDK types. The package requires Python
3.10+ and has optional Realtime, voice, aiohttp, and Bedrock dependencies
([README.md:6](../../README.md), [pyproject.toml:11](../../pyproject.toml),
[pyproject.toml:42](../../pyproject.toml)).

Most API resources and types are generated from the OpenAPI schema. The
security-relevant handwritten surfaces are the shared transport and parsing
code, authentication providers, webhook verification, provider integrations,
local helpers, dependency/build policy, and release automation
([AGENTS.md:3](../../AGENTS.md), [src/openai/_client.py:157](../../src/openai/_client.py),
[src/openai/_base_client.py:517](../../src/openai/_base_client.py)).

| Component | Role | Evidence |
| --- | --- | --- |
| `OpenAI` / `AsyncOpenAI` clients | Resolve credentials, endpoint configuration, headers, retries, and transports. | [src/openai/_client.py:157](../../src/openai/_client.py), [src/openai/_client.py:247](../../src/openai/_client.py) |
| Shared base client | Serializes caller data, builds HTTP requests, processes responses, and manages retries. | [src/openai/_base_client.py:517](../../src/openai/_base_client.py), [src/openai/_base_client.py:672](../../src/openai/_base_client.py) |
| Streaming and Realtime | Incrementally decode SSE and exchange WebSocket messages with remote endpoints. | [src/openai/_streaming.py:53](../../src/openai/_streaming.py), [src/openai/resources/realtime/realtime.py:683](../../src/openai/resources/realtime/realtime.py) |
| Webhooks | Verify raw inbound webhook bytes before parsing a typed event. | [src/openai/resources/webhooks/webhooks.py:18](../../src/openai/resources/webhooks/webhooks.py), [src/openai/lib/_webhooks.py:13](../../src/openai/lib/_webhooks.py) |
| Workload identity | Obtain local or metadata subject tokens and exchange them for OpenAI bearer tokens. | [src/openai/auth/_workload.py:78](../../src/openai/auth/_workload.py), [src/openai/auth/_x509.py:25](../../src/openai/auth/_x509.py) |
| CI and publication | Test PR and branch code, run CodeQL, perform the privileged monthly policy assessment, build distributions, and publish through protected release paths. | [.github/workflows/ci.yml:18](../../.github/workflows/ci.yml), [.github/workflows/codeql.yml:15](../../.github/workflows/codeql.yml), [.github/workflows/python-version-review.yml:15](../../.github/workflows/python-version-review.yml), [.github/workflows/publish-pypi.yml:8](../../.github/workflows/publish-pypi.yml) |

```mermaid
flowchart LR
  app[Caller-owned Python process] -->|credentials, request data, files| sdk[OpenAI Python SDK]
  sdk -->|HTTPS / WSS| api[OpenAI, Azure, or Bedrock API]
  api -->|JSON, SSE, WebSocket frames| sdk
  webhook[Webhook sender] -->|raw payload and headers| verify[Webhook verifier]
  host[Local file or cloud metadata identity] -->|subject token| auth[Token exchange]
  pr[PR checkout code] -->|workflow-specific permissions| ci[CI runner]
  main[Protected main/release workflow] -->|artifact boundary| publish[PyPI publish job]
```

| Deployment or workflow | Resource or capability | Configuration and precedence | Safe effective value or location | Readers, writers, or recipients | Enforcing control | Evidence or unknowns |
| --- | --- | --- | --- | --- | --- | --- |
| Default OpenAI client | API or admin credential | Explicit argument, then `OPENAI_API_KEY` / `OPENAI_ADMIN_KEY`. | Secret value is held in process memory and emitted as bearer auth. | Selected API destination. | Missing credentials fail; per-operation security flags select ordinary versus admin auth. | [src/openai/_client.py:247](../../src/openai/_client.py), [src/openai/_client.py:589](../../src/openai/_client.py) |
| Default routing | API origin | Explicit `base_url`, then `OPENAI_BASE_URL`, then default. | `https://api.openai.com/v1` by default. | HTTP transport and remote API. | Caller controls non-X.509 overrides; relative resource paths merge into the configured base URL. | [src/openai/_client.py:299](../../src/openai/_client.py), [src/openai/_base_client.py:501](../../src/openai/_base_client.py) |
| Data residency | Regional API origin | `data_residency` selects a fixed mapping and cannot combine with explicit endpoint/provider modes. | Regional HTTPS endpoint selected by SDK mapping. | Remote API. | Conflicting routing modes raise before request construction. | [src/openai/_data_residency.py:12](../../src/openai/_data_residency.py) |
| X.509 workload identity | mTLS API and token exchange | X.509 identity selects mTLS default; caller supplies certificate through its HTTP transport. | API defaults to `https://mtls.api.openai.com/v1`; exchange is pinned to `https://mtls.auth.openai.com/oauth/token`. | OpenAI mTLS API and auth service. | HTTPS, origin, Host, TLS authority, credential, and authorization checks; token-exchange redirects are disabled. | [src/openai/auth/_x509.py:25](../../src/openai/auth/_x509.py), [src/openai/auth/_x509.py:49](../../src/openai/auth/_x509.py), [src/openai/auth/_x509.py:97](../../src/openai/auth/_x509.py) |
| Subject-token workload identity | Local or metadata subject token | Provider callback; built-ins read Kubernetes token file or call Azure/GCP metadata endpoints. | Kubernetes defaults to `/var/run/secrets/kubernetes.io/serviceaccount/token`; metadata hosts are fixed by helper. | Local host identity source and OpenAI token exchange. | Fixed metadata headers, bounded timeout, token-response validation, and in-memory token cache. | [src/openai/auth/_workload.py:78](../../src/openai/auth/_workload.py), [src/openai/auth/_workload.py:128](../../src/openai/auth/_workload.py), [src/openai/auth/_workload.py:181](../../src/openai/auth/_workload.py), [src/openai/auth/_workload.py:220](../../src/openai/auth/_workload.py) |
| Webhook consumer | Webhook secret and raw inbound bytes | Explicit secret, then client `webhook_secret`, which may come from `OPENAI_WEBHOOK_SECRET`. | Secret remains in process memory; payload and headers are caller-supplied bytes. | SDK verifier and caller application. | Timestamp tolerance, HMAC-SHA256, constant-time comparison; `unwrap` verifies before JSON parsing. | [src/openai/_client.py:281](../../src/openai/_client.py), [src/openai/resources/webhooks/webhooks.py:18](../../src/openai/resources/webhooks/webhooks.py), [src/openai/lib/_webhooks.py:20](../../src/openai/lib/_webhooks.py) |
| File upload | Caller filesystem read | Caller passes bytes, streams, or `PathLike` values. | Caller-selected path or already-opened stream. | Local OS and remote API. | Local OS permissions and explicit caller invocation; SDK does not discover files automatically. | [src/openai/_files.py:25](../../src/openai/_files.py), [src/openai/_files.py:65](../../src/openai/_files.py) |
| HTTP/SSE response | Remote response bytes | Remote endpoint selected by caller configuration; streaming uses incremental decoders. | Remote JSON, SSE lines, or events in process memory. | SDK model parser and caller application. | Incremental SSE handling and `finally` response cleanup; large legitimate payloads are supported without arbitrary fixed rejection limits. | [src/openai/_streaming.py:53](../../src/openai/_streaming.py), [src/openai/_streaming.py:109](../../src/openai/_streaming.py), [AGENTS.md:112](../../AGENTS.md) |
| Realtime | WebSocket destination and auth headers | Explicit `websocket_base_url`, otherwise HTTP base transformed to a WebSocket scheme. | Caller-selected WebSocket origin and `/realtime` path. | WebSocket peer. | Caller owns custom options; async path uses a same-origin redirect wrapper. | [src/openai/resources/realtime/realtime.py:683](../../src/openai/resources/realtime/realtime.py), [src/openai/lib/_websocket.py:12](../../src/openai/lib/_websocket.py) |
| Package build and PyPI publish | Executable checkout code, artifacts, and OIDC publication | `scripts/build` invokes the locked build; artifacts pass from build job to upload-only job. | Build artifact; no long-lived PyPI token. | CI runner, artifact store, PyPI. | Locked/provenance-checked build requirements; no OIDC in build; `id-token: write` only in the publish job. | [scripts/build:1](../../scripts/build), [pyproject.toml:71](../../pyproject.toml), [.github/workflows/publish-pypi.yml:8](../../.github/workflows/publish-pypi.yml), [.github/workflows/publish-pypi.yml:40](../../.github/workflows/publish-pypi.yml) |
| `ci.yml` pull-request jobs | PR checkout execution | PR code and config are checked out and run in CI. | Tracked executable files from the PR checkout. | Read-only CI runner. | Workflow permissions are read-only, checkout credentials are not persisted, and dependency/build provenance is checked before installation. | [.github/workflows/ci.yml:18](../../.github/workflows/ci.yml), [.github/workflows/ci.yml:33](../../.github/workflows/ci.yml), [.github/workflows/ci.yml:37](../../.github/workflows/ci.yml) |
| CodeQL on a same-repository PR | Candidate source plus security-result write token | `pull_request` against `main` checks out candidate source, which pinned CodeQL actions process without a repository `run` or build step. | `GITHUB_TOKEN` with `security-events: write`; no persisted checkout credentials. | CodeQL analyzer/upload path and GitHub security-events API. | This is not the read-only `ci.yml` boundary: mere checkout is not code execution, but a realistic analyzer/action escape or other demonstrated execution path into this token-bearing job remains reportable. | [.github/workflows/codeql.yml:7](../../.github/workflows/codeql.yml), [.github/workflows/codeql.yml:15](../../.github/workflows/codeql.yml), [.github/workflows/codeql.yml:27](../../.github/workflows/codeql.yml), [.github/workflows/codeql.yml:32](../../.github/workflows/codeql.yml) |
| Monthly Python version assessment | External lifecycle data, OpenAI key, agent output, and issue publication | Scheduled workflow downloads CPython/PyPI data, passes `OPENAI_API_KEY` to the pinned assessment action, runs Codex as an unprivileged user through the action's isolation boundary, marker/size-checks output, appends it to the step summary, and copies action-required output for a separate issue publisher. | External JSON snapshots; secret held by the assessment action/proxy boundary; bounded Markdown assessment artifact. | Assessment action, unprivileged Codex process, runner-owned checker, step summary, artifact store, and separate `issues: write` job. | Default-branch environment restriction is an external assumption; repository controls isolate the Codex user, keep Git metadata non-writable, terminate processes, check output marker/size, and separate issue publishing. Those checks do not establish semantic safety or redaction. | [.github/workflows/python-version-review.yml:19](../../.github/workflows/python-version-review.yml), [.github/workflows/python-version-review.yml:32](../../.github/workflows/python-version-review.yml), [.github/workflows/python-version-review.yml:58](../../.github/workflows/python-version-review.yml), [.github/workflows/python-version-review.yml:94](../../.github/workflows/python-version-review.yml), [.github/workflows/python-version-review.yml:104](../../.github/workflows/python-version-review.yml), [.github/workflows/python-version-review.yml:125](../../.github/workflows/python-version-review.yml), [.github/workflows/python-version-review.yml:160](../../.github/workflows/python-version-review.yml), [.github/workflows/python-version-review.yml:171](../../.github/workflows/python-version-review.yml) |
| Protected release workflows | Release and publication authority | Main/release workflows and protected environments. | GitHub App/release authority and PyPI Trusted Publishing identity are external protected configuration. | GitHub and PyPI. | Repository workflows request bounded permissions and separate privileged jobs; host-side branch/environment protections are not proven by this repository. | [.github/workflows/create-releases.yml:8](../../.github/workflows/create-releases.yml), [.github/workflows/publish-pypi.yml:40](../../.github/workflows/publish-pypi.yml) |

## Threat Model, Trust Boundaries, and Assumptions

### Protected assets and objectives

- Keep API keys, admin keys, webhook secrets, subject tokens, exchanged bearer
  tokens, provider credentials, and release credentials from reaching unintended
  recipients ([src/openai/_client.py:247](../../src/openai/_client.py),
  [src/openai/auth/_workload.py:220](../../src/openai/auth/_workload.py)).
- Preserve correct destination and credential binding, including distinct
  ordinary/admin auth selection, residency routing, X.509 authority checks, and
  provider-specific signing ([src/openai/_client.py:589](../../src/openai/_client.py),
  [src/openai/_data_residency.py:12](../../src/openai/_data_residency.py),
  [src/openai/auth/_x509.py:49](../../src/openai/auth/_x509.py)).
- Verify webhook authenticity and replay freshness before a payload is treated
  as an OpenAI event ([src/openai/resources/webhooks/webhooks.py:18](../../src/openai/resources/webhooks/webhooks.py),
  [src/openai/lib/_webhooks.py:20](../../src/openai/lib/_webhooks.py)).
- Preserve confidentiality and integrity of caller prompts, uploads, audio,
  responses, and streaming events as they cross caller-selected transports.
- Keep credentials, authentication headers, customer data, and unredacted
  sensitive request or response bodies out of logs, snapshots, test output,
  and exceptions; those are independently readable
  recipients, not harmless diagnostics. Safe or sanitized caller-visible
  `APIError.body` diagnostics may remain
  ([AGENTS.md:26](../../AGENTS.md),
  [src/openai/_utils/_logs.py:10](../../src/openai/_utils/_logs.py),
  [src/openai/_exceptions.py:46](../../src/openai/_exceptions.py)).
- Preserve package and release integrity: untrusted PR execution must not reach
  protected release credentials or publication authority
  ([.github/workflows/ci.yml:18](../../.github/workflows/ci.yml),
  [.github/workflows/publish-pypi.yml:40](../../.github/workflows/publish-pypi.yml)).
- Preserve large-payload compatibility through incremental processing, timely
  cleanup, and caller cancellation rather than arbitrary SDK body/event/line
  limits ([AGENTS.md:112](../../AGENTS.md), [src/openai/_streaming.py:109](../../src/openai/_streaming.py)).

### Actors, authority, and boundaries

- The caller application owns its process, explicit client arguments,
  environment, filesystem authority, credential callbacks, custom transports,
  headers, and endpoint configuration. A caller that already controls
  `base_url`, `websocket_base_url`, a file path, or an HTTP client does not
  gain a new SDK privilege merely because the SDK uses that value
  ([src/openai/_client.py:157](../../src/openai/_client.py),
  [src/openai/_client.py:299](../../src/openai/_client.py)).
- Remote HTTP, SSE, and WebSocket data is independently mutable lower-trust
  input when it enters parsers and remains lower-trust for sensitive-sink
  analysis after syntactic parsing or schema validation. Those steps establish
  structure, not safe semantics; continue tracing to credential use, local-file
  access, code execution, and caller security decisions unless a
  boundary-specific semantic validation or authorization step establishes the
  needed property ([src/openai/_base_client.py:672](../../src/openai/_base_client.py),
  [src/openai/_streaming.py:166](../../src/openai/_streaming.py)).
- Webhook payloads and headers are lower-trust input when they enter signature
  verification. A successful HMAC and timestamp check establishes provenance
  and freshness, not that payload fields are safe for a sensitive sink; keep
  tracing those fields unless a boundary-specific semantic validation or
  authorization step establishes the needed property. Application behavior
  after verified delivery remains caller-owned
  ([src/openai/resources/webhooks/webhooks.py:18](../../src/openai/resources/webhooks/webhooks.py)).
- Local token files and cloud metadata services are host-identity boundaries:
  an attacker who can independently read or invoke them may gain a token the
  SDK exchanges for OpenAI authority ([src/openai/auth/_workload.py:78](../../src/openai/auth/_workload.py),
  [src/openai/auth/_workload.py:128](../../src/openai/auth/_workload.py)).
- PR authors control their checkout contents and therefore the tracked source,
  examples, tests, fixtures, build scripts, and other executable files that CI
  intentionally runs. Those files execute with
  repository-code authority. A contributor who can change such tracked
  executable code does not gain a new privilege merely because a test, example,
  build, or lint step runs it. The real boundary is whether that PR-controlled
  execution can reach independently protected credentials, tokens, write
  permissions, release environments, or publication authority
  ([.github/workflows/ci.yml:18](../../.github/workflows/ci.yml),
  [.github/workflows/ci.yml:33](../../.github/workflows/ci.yml),
  [.github/workflows/publish-pypi.yml:40](../../.github/workflows/publish-pypi.yml)).
- Workflow-definition changes remain security-sensitive whenever they can alter
  permissions, secrets, protected environments, artifact provenance, or
  publication paths.
- The read-only statement above is specific to `ci.yml`. CodeQL is a distinct
  same-repository PR boundary because pinned analyzer actions process candidate
  source while the job token has `security-events: write`. The workflow does
  not run repository scripts merely by checking out the source; scans must
  investigate a realistic analyzer/action escape or another demonstrated
  execution path before treating token misuse as reportable
  ([.github/workflows/codeql.yml:7](../../.github/workflows/codeql.yml),
  [.github/workflows/codeql.yml:15](../../.github/workflows/codeql.yml),
  [.github/workflows/codeql.yml:27](../../.github/workflows/codeql.yml),
  [.github/workflows/codeql.yml:32](../../.github/workflows/codeql.yml)).
- The monthly Python-version review is a separate privileged workflow:
  independently mutable CPython/PyPI data reaches an unprivileged Codex process
  through the pinned assessment action's isolation boundary, while the action
  receives `OPENAI_API_KEY`. Marker/size-checked output is appended to the
  step summary, and action-required output becomes the intended issue body for
  a separate `issues: write` publisher. Those checks do not prove semantic
  safety or redaction. Regressions that expose the key, weaken workspace
  ownership, leak sensitive output to the summary, escape the intended issue
  body into publisher commands/metadata/targets, obtain broader issue-write
  authority, or collapse job separation remain reportable boundaries
  ([.github/workflows/python-version-review.yml:58](../../.github/workflows/python-version-review.yml),
  [.github/workflows/python-version-review.yml:94](../../.github/workflows/python-version-review.yml),
  [.github/workflows/python-version-review.yml:104](../../.github/workflows/python-version-review.yml),
  [.github/workflows/python-version-review.yml:125](../../.github/workflows/python-version-review.yml),
  [.github/workflows/python-version-review.yml:160](../../.github/workflows/python-version-review.yml),
  [.github/workflows/python-version-review.yml:171](../../.github/workflows/python-version-review.yml)).
- Main/release workflows and PyPI publication are conditional privileged
  surfaces. Repository YAML shows requested permissions and job separation;
  external branch, environment, GitHub App, and Trusted Publishing bindings are
  deployment assumptions, not facts proven by the checkout.

### Reportability and assumptions

A reportable SDK finding requires a realistic new capability across an actual
boundary: independently mutable lower-trust input crossing a parser/evaluator
boundary into a sensitive sink; untrusted runtime, API, network, webhook, or
metadata data reaching credentials, local files, code execution, or caller
security decisions; unredacted sensitive material reaching logs, exceptions,
snapshots, or test output; or PR-controlled code reaching
protected CI/release credentials,
write-capable tokens, or publication authority. Ordinary authorized SDK behavior,
self-only effects within authority the caller or PR author already has, and
keyword matches in tracked executable repository code are not findings by
themselves. Safe or sanitized caller-visible `APIError.body` diagnostics are not
findings by themselves.

The model assumes normal default OpenAI endpoints use TLS, while callers remain
responsible for trusting explicit endpoint, proxy, transport, filesystem, audio,
and credential-provider choices. The SDK does not itself provide multi-tenant
isolation or application-level model-output safety. Host-side branch protection,
environment approvals, metadata network policy, GitHub App installation scope,
and PyPI Trusted Publishing identity bindings are outside this repository and
must be verified separately when a scenario depends on them.

## Attack Surface, Mitigations, and Attacker Stories

These are reusable hypotheses and review guidance, not confirmed
vulnerabilities.

| Priority | Scenario and capability gain | Prerequisites | Impact | Existing controls | Mitigation | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| High | Credential misrouting sends API, admin, provider, or WebSocket auth to an unintended origin. | Independently mutable lower-trust input must influence a destination after the caller chose trusted configuration, or a protected mode must lose its binding. | Credential or caller-data disclosure. | Default OpenAI origin; residency conflict checks; X.509 origin/Host/TLS/auth checks; provider-specific controls. | Keep destination configuration privileged; preserve and test binding checks in protected auth modes. | [src/openai/_client.py:299](../../src/openai/_client.py), [src/openai/_data_residency.py:12](../../src/openai/_data_residency.py), [src/openai/auth/_x509.py:49](../../src/openai/auth/_x509.py) |
| High | PR-controlled execution reaches protected release or publication authority. | A PR path must receive write-capable token, protected environment secret, OIDC publication capability, or mutable artifact path beyond its intended authority. | Malicious package release or repository compromise. | Read-only CI permissions, no persisted checkout credentials, provenance checks, separate build/publish jobs, upload-only OIDC. | Preserve job separation, pinned actions, least privilege, protected environments, and artifact integrity. | [.github/workflows/ci.yml:18](../../.github/workflows/ci.yml), [.github/workflows/ci.yml:37](../../.github/workflows/ci.yml), [.github/workflows/publish-pypi.yml:8](../../.github/workflows/publish-pypi.yml) |
| High | Same-repository PR source causes an analyzer/action escape that repurposes CodeQL's `security-events: write` token. | Candidate source reaches the pinned CodeQL analyzer and a realistic escape or separately demonstrated execution path reaches the token-bearing job; mere checkout is insufficient. | Unauthorized security-event writes or any broader capability exposed by a regression in token use. | Narrow declared permissions, no persisted checkout credentials, pinned CodeQL actions, and no repository `run` step. | Preserve least privilege and ensure analyzer/action processing cannot exfiltrate or reuse the token outside intended security-result publication. | [.github/workflows/codeql.yml:7](../../.github/workflows/codeql.yml), [.github/workflows/codeql.yml:15](../../.github/workflows/codeql.yml), [.github/workflows/codeql.yml:27](../../.github/workflows/codeql.yml), [.github/workflows/codeql.yml:32](../../.github/workflows/codeql.yml) |
| Medium | Forged or replayed webhook is accepted as authentic. | Attacker controls payload/headers but not the secret; verifier is bypassed, weakened, or called after sensitive parsing/action. | Unauthorized downstream action in caller application. | HMAC-SHA256, timestamp tolerance, constant-time comparison, verify-before-parse `unwrap`. | Keep verification on raw bytes before application logic and protect/rotate secrets. | [src/openai/resources/webhooks/webhooks.py:18](../../src/openai/resources/webhooks/webhooks.py), [src/openai/lib/_webhooks.py:20](../../src/openai/lib/_webhooks.py) |
| Medium | Malicious remote JSON, SSE, or WebSocket input causes parser confusion, availability pressure, or unsafe caller-visible state. | Hostile or compromised endpoint, or an application deliberately routes to one; impact must exceed ordinary malformed-response errors. | Process availability or downstream security decision impact. | JSON-only parsing, incremental SSE decoder, response cleanup, caller-configurable timeout/cancellation. | Preserve incremental handling and cleanup; validate before sensitive application sinks. | [src/openai/_base_client.py:672](../../src/openai/_base_client.py), [src/openai/_streaming.py:166](../../src/openai/_streaming.py), [AGENTS.md:112](../../AGENTS.md) |
| Medium | Sensitive data is emitted through diagnostics. | Runtime/API/network data or secret-bearing state reaches logs, exceptions, snapshots, or test output without redaction. Safe or sanitized caller-visible `APIError.body` diagnostics alone are insufficient. | Credentials, customer data, or unredacted sensitive bodies become readable to unintended diagnostic recipients. | Sensitive-header log filter, repository redaction requirements, and the safe/sanitized `APIError.body` carve-out. | Preserve redaction at every diagnostic boundary and avoid copying unredacted sensitive bodies into logs, exceptions, snapshots, and test output. | [AGENTS.md:26](../../AGENTS.md), [src/openai/_utils/_logs.py:10](../../src/openai/_utils/_logs.py), [src/openai/_exceptions.py:46](../../src/openai/_exceptions.py) |
| Medium | Monthly review input or output escapes its intended isolation or publication boundary. | A regression lets independently mutable lifecycle/PyPI data expose the action-held key, mutate protected workspace state, leak sensitive output to the step summary, escape the bounded issue body into publisher commands/metadata/target selection, or obtain broader `issues: write` use. Normal publication of the marker/size-checked issue body is not itself a finding. | OpenAI key exposure or unauthorized issue content/write behavior. | Unprivileged Codex user, non-writable Git metadata, process termination, output marker/size checks, and separate issue publisher. | Preserve environment restriction, action/process isolation, output checks, redaction, and the job boundary. | [.github/workflows/python-version-review.yml:19](../../.github/workflows/python-version-review.yml), [.github/workflows/python-version-review.yml:58](../../.github/workflows/python-version-review.yml), [.github/workflows/python-version-review.yml:94](../../.github/workflows/python-version-review.yml), [.github/workflows/python-version-review.yml:104](../../.github/workflows/python-version-review.yml), [.github/workflows/python-version-review.yml:125](../../.github/workflows/python-version-review.yml), [.github/workflows/python-version-review.yml:160](../../.github/workflows/python-version-review.yml), [.github/workflows/python-version-review.yml:171](../../.github/workflows/python-version-review.yml) |
| Medium | Host identity token misuse mints OpenAI bearer authority. | Attacker independently reads the mounted token or reaches metadata from a process that should not have that authority. | Unauthorized API calls as the workload identity. | Fixed helper endpoints/headers, bounded timeouts, token response validation, in-memory cache. | Restrict pod/file/metadata access and use workload identity only in intended runtimes. | [src/openai/auth/_workload.py:78](../../src/openai/auth/_workload.py), [src/openai/auth/_workload.py:128](../../src/openai/auth/_workload.py), [src/openai/auth/_workload.py:283](../../src/openai/auth/_workload.py) |
| Low | Attacker-controlled application input becomes a local file upload. | Consuming application passes an attacker-chosen path while the process already has local read authority. | Local data disclosure to the configured API. | Explicit caller invocation and OS file permissions; no automatic discovery. | Validate/allowlist paths at the application boundary or pass opened streams/bytes. | [src/openai/_files.py:25](../../src/openai/_files.py), [src/openai/_files.py:65](../../src/openai/_files.py) |
| Low | Local audio is captured or played unexpectedly. | Application explicitly invokes optional helpers with device permission. | Self-only local privacy or nuisance effect unless a distinct application boundary is shown. | Optional dependency, explicit helper path, OS permissions. | Gate helpers behind user intent and OS permission UX. | [pyproject.toml:46](../../pyproject.toml), [src/openai/helpers/microphone.py:81](../../src/openai/helpers/microphone.py) |
| Not a finding by itself | A PR changes a checked-in test, fixture, example, build script, or other tracked executable file and CI runs it. | PR author already controls that checkout code. | No new capability without a separate protected sink. | Repository-code authority is explicit; CI boundary is evaluated at credentials and permissions. | Investigate only if execution crosses into protected authority. | [.github/workflows/ci.yml:18](../../.github/workflows/ci.yml), [.github/workflows/ci.yml:69](../../.github/workflows/ci.yml) |

## Severity Calibration (Critical, High, Medium, Low)

- **Critical:** unauthorized PyPI publication, broadly trusted distribution
  compromise, or release-token compromise that affects package consumers.
  Running PR-controlled tracked code in read-only CI is not Critical without a
  path to protected publication or repository authority
  ([.github/workflows/publish-pypi.yml:40](../../.github/workflows/publish-pypi.yml),
  [.github/workflows/ci.yml:18](../../.github/workflows/ci.yml)).
- **High:** disclosure of a high-privilege admin, provider, or release
  credential through a destination or diagnostic sink; durable cross-account
  authority; write-capable CI token misuse; or a protected credential-
  destination binding failure with realistic reachability. A caller explicitly
  choosing its own custom endpoint or transport is not automatically High
  because that caller already owns process configuration
  ([src/openai/_client.py:157](../../src/openai/_client.py),
  [src/openai/_client.py:589](../../src/openai/_client.py)).
- **Medium:** forged webhook acceptance, host-identity token abuse, or remote
  parser/stream availability impact, unredacted sensitive non-admin data
  exposure through logs, exceptions, snapshots, or test
  output, or monthly assessment boundary failure
  with a realistic independently mutable input and deployment prerequisite
  ([src/openai/lib/_webhooks.py:20](../../src/openai/lib/_webhooks.py),
  [src/openai/auth/_workload.py:78](../../src/openai/auth/_workload.py)).
- **Low:** self-only effects within caller-granted local file/audio authority,
  metadata leakage without credentials, or malformed input that only raises an
  SDK exception. Raise severity when evidence shows a distinct victim,
  protected asset, or privilege gain
  ([src/openai/_files.py:65](../../src/openai/_files.py),
  [src/openai/helpers/microphone.py:81](../../src/openai/helpers/microphone.py)).

Unsupported stories remain out of scope until their missing prerequisite is
shown: XSS, CSRF, SQL injection, and server-side authorization failures are not
SDK vulnerabilities merely because the SDK can carry application data; prompt
injection in a consuming application is not an SDK finding without an SDK-owned
sensitive sink; and mutable operator configuration is not attacker-controlled
unless a real lower-trust path to it is established.
