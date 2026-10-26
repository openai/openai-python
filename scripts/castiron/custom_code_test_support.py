# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
"""Small Git/checkpoint fixture shared by the offline Castiron tests."""

from __future__ import annotations

import base64
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any, cast

import custom_code_report as report

GENERATION = "550e8400-e29b-41d4-a716-446655440000"


class GitTestCase(unittest.TestCase):
    def setUp(self) -> None:  # pyright: ignore[reportImplicitOverride]
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Castiron test")
        self.git("config", "user.email", "castiron@example.test")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def write(self, path: str, body: str) -> None:
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)

    def commit(self, message: str = "fixture") -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self.git("rev-parse", "HEAD")

    def baseline(self) -> tuple[str, str]:
        self.write("generated.py", "generated\n")
        metadata = {
            "generation_id": GENERATION,
            "source_branch": "test",
            "target": "openai-python",
            "language": "python",
        }
        encoded = base64.b64encode(json.dumps(metadata).encode()).decode()
        generated = self.commit(f"codegen\n\nGeneration metadata: {encoded}")
        self.git("update-ref", "refs/remotes/origin/codegen/test", generated)
        self.write(
            ".castiron.stats.yml",
            f"schema_version: 1\ngeneration_id: {GENERATION}\ncodegen_sha: {generated}\ncodegen_hash: {report.hash_codegen_commit(self.repo, generated)}\n",
        )
        return generated, self.commit("integrated")


def source_run(head: str, event: str = "pull_request") -> dict[str, Any]:
    return {
        "id": 123,
        "workflow_id": 456,
        "event": event,
        "head_sha": head,
        "head_branch": "gh-readonly-queue/main/pr-7-example" if event == "merge_group" else "sdk",
        "repository": {"full_name": "openai/example"},
        "head_repository": {
            "id": 10,
            "full_name": "contributor/example",
            "owner": {"login": "contributor"},
        },
        "path": ".github/workflows/castiron-custom-code.yml",
        "status": "completed",
        "run_attempt": 1,
        "pull_requests": [{"number": 3}] if event == "pull_request" else [],
        "conclusion": "failure",  # The candidate's result is deliberately ignored.
    }


def source_head(sha: str) -> dict[str, Any]:
    return {"sha": sha, "ref": "sdk", "repo": source_run(sha)["head_repository"]}


WORKFLOW = (
    Path(__file__).resolve().parents[2] / ".github/workflows/castiron-custom-code-comment.yml"
)


def run_publisher(step: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    section = WORKFLOW.read_text().split(f"- name: {step}\n", 1)[1]
    script = section.split("          script: |\n", 1)[1]
    lines: list[str] = []
    for line in script.splitlines():
        if line and not line.startswith("            "):
            break
        lines.append(line[12:])
    return run_workflow_script("\n".join(lines), payload)


def run_workflow_script(script: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    output = subprocess.run(
        ["node", str(Path(__file__).with_name("fixtures") / "github_publisher.cjs")],
        input=json.dumps({**payload, "script": script}),
        text=True,
        capture_output=True,
        check=True,
    )
    return cast(list[dict[str, Any]], json.loads(output.stdout))
