# Security Policy

## Reporting a vulnerability

Please report potential security vulnerabilities privately through OpenAI's
[coordinated vulnerability disclosure process](https://openai.com/policies/coordinated-vulnerability-disclosure-policy).
For questions about that process, contact disclosure@openai.com.

This policy applies to the source code in this repository and the official
[`openai` Python package](https://pypi.org/project/openai/), including its
published source distributions and wheels.

## Threat model authority

This file governs coordinated disclosure and what reporters should include. The
canonical repository threat model, trust boundaries, reportability guidance,
and severity calibration for Codex Security scans are maintained in
[`docs/architecture/security-model.md`](docs/architecture/security-model.md).
Follow that document's own trusted-revision resolution rule for security
analysis; do not duplicate or infer a competing threat model from this
disclosure policy.

Do not report security vulnerabilities through public GitHub issues, pull requests, or discussions.

## What to include

- The affected package or product and version, or the relevant source commit.
- A clear description of the security impact.
- Sanitized steps to reproduce the issue.

For the `openai` Python package, include the Python version, operating system,
and affected source distribution or wheel when relevant.

Do not include live credentials, API keys, customer data, or unredacted sensitive logs.

Redact authentication headers and private keys, and replace other secrets with
clearly fake values.

## Coordinated disclosure

Follow the linked coordinated-disclosure terms, and keep vulnerability details
confidential until their release is coordinated with or authorized by OpenAI.

Thank you for helping us keep this SDK and the systems it interacts with secure.
