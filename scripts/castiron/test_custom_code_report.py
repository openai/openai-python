# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import struct
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import custom_code_report as report

GENERATION = "550e8400-e29b-41d4-a716-446655440000"


class CustomCodeTests(unittest.TestCase):
    # Keep the vendored test stdlib-only on Python 3.10 (no typing.override yet).
    def setUp(self) -> None:  # pyright: ignore[reportImplicitOverride]
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Castiron test")
        self.git("config", "user.email", "castiron@example.test")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args], check=True, capture_output=True, text=True
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

    def test_git_preserves_authentication_without_inherited_repository_routing(self) -> None:
        environment = {
            "GIT_CONFIG_GLOBAL": "/ordinary/gitconfig",
            "GIT_ASKPASS": "/ordinary/askpass",
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "credential.helper",
            "GIT_CONFIG_VALUE_0": "example",
            "GIT_DIR": "/wrong/repository",
            "GIT_COMMON_DIR": "/wrong/common",
            "GIT_INDEX_FILE": "/wrong/index",
        }
        with (
            mock.patch.dict(os.environ, environment),
            mock.patch.object(
                report.subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 0, stdout=b"ok"),
            ) as run,
        ):
            self.assertEqual(report.git(self.repo, "status"), b"ok")
        actual = run.call_args.kwargs["env"]
        for name, value in environment.items():
            if name in {"GIT_DIR", "GIT_COMMON_DIR", "GIT_INDEX_FILE"}:
                self.assertNotIn(name, actual)
            else:
                self.assertEqual(actual[name], value)
        self.assertEqual(actual["GIT_NO_REPLACE_OBJECTS"], "1")

    @unittest.skipUnless(os.environ.get("CASTIRON_TEST_BIN"), "Castiron compiler contract test")
    def test_rust_and_python_hashes_match(self) -> None:
        self.write("a", "first\n")
        self.write("nested/b", "second\n")
        self.write(".github/workflows/ignored.yml", "ignored\n")
        for change in ("initial", "mode", "bytes"):
            if change == "mode":
                (self.repo / "a").chmod(0o755)
            elif change == "bytes":
                self.write("nested/b", "changed\n")
            commit = self.commit(change)
            rust = subprocess.check_output(
                [
                    os.environ["CASTIRON_TEST_BIN"],
                    "sdk",
                    "codegen-hash",
                    "--repo",
                    str(self.repo),
                    "--commit",
                    commit,
                ],
                text=True,
            ).strip()
            self.assertEqual(rust, report.hash_codegen_commit(self.repo, commit))

    def test_reporting_script_can_be_a_mixed_file(self) -> None:
        path = "scripts/castiron/custom_code_report.py"
        self.write(path, "# generated reporter\n")
        _, base = self.baseline()
        self.write(path, "# generated reporter\n# local customization\n")
        head = self.commit()
        result, _ = report.build_report(self.repo, base, head, require_head_hash=True)
        changed = next(file for file in result["files"] if file["path"] == path)
        self.assertEqual(changed["category"], "newly_customized")

    def test_hash_vector_and_exclusions(self) -> None:
        self.write("a", "hello\n")
        first = self.commit()
        encoded = (
            report.DOMAIN
            + struct.pack(">Q", 1)
            + struct.pack(">Q", 1)
            + b"a100644"
            + struct.pack(">Q", 6)
            + b"hello\n"
        )
        expected = hashlib.sha256(encoded).hexdigest()
        self.assertEqual(report.hash_codegen_commit(self.repo, first), expected)
        self.write(".github/workflows/test.yml", "ignored\n")
        self.write(".github/actions/test/action.yml", "ignored\n")
        second = self.commit()
        self.assertEqual(report.hash_codegen_commit(self.repo, second), expected)
        os.chmod(self.repo / "a", 0o755)
        self.assertNotEqual(report.hash_codegen_commit(self.repo, self.commit()), expected)
        self.write(".github/CODEOWNERS", "not ignored\n")
        self.assertNotEqual(report.hash_codegen_commit(self.repo, self.commit()), expected)

    def test_classifications(self) -> None:
        a, b, c = (report.Entry(b"100644", value * 40) for value in "abc")
        cases = [
            ((a, a, b, b), None),
            ((a, a, a, b), "newly_customized"),
            ((a, b, a, a), "removed"),
            ((a, b, a, c), "existing_changed"),
            ((a, b, a, b), "unchanged"),
            ((a, b, c, b), "baseline_changed"),
            ((a, b, None, b), "no_longer_generated"),
            ((a, a, None, a), "no_longer_generated"),
            ((a, a, None, None), None),
            ((None, b, a, b), "newly_generation_owned"),
            ((None, a, a, a), "newly_generation_owned"),
            ((a, a, b, a), "baseline_changed"),
            ((a, b, b, b), "baseline_changed"),
            ((a, a, a, None), "newly_customized"),
        ]
        for values, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(report.classify(*values), expected)

    def test_report_ignores_handwritten_files_and_shows_custom_patch(self) -> None:
        generated, base = self.baseline()
        self.write("generated.py", "generated\n# custom\n")
        self.write("handwritten.py", "handwritten\n")
        head = self.commit()
        result, patch = report.build_report(self.repo, base, head, require_head_hash=True)
        self.assertEqual(result["counts"]["newly_customized"], 1)
        self.assertEqual(result["files"][0]["path"], "generated.py")
        self.assertIn(b"+# custom", patch)
        self.assertNotIn(b"handwritten", patch)
        self.assertEqual(result["after"]["commit"], generated)
        body = report.render_report(result, repository="openai/example", run_id=42, run_attempt=2)
        self.assertIn("<summary>Inspect the custom-code diff</summary>", body)
        self.assertIn("gh run download 42 --repo openai/example", body)
        self.assertIn("--name castiron-custom-code-42-2", body)
        self.assertIn(f"--head {head}", body)
        self.assertIn("current full custom patch", body)

    def test_bad_hash_and_lost_checkpoint_fail(self) -> None:
        generated, base = self.baseline()
        stats = self.repo / ".castiron.stats.yml"
        stats.write_text(
            stats.read_text().replace(report.hash_codegen_commit(self.repo, generated), "f" * 64)
        )
        with self.assertRaisesRegex(report.ReportError, "codegen_hash mismatch"):
            report.build_report(self.repo, base, self.commit())
        self.git("update-ref", "-d", "refs/remotes/origin/codegen/test")
        with self.assertRaises(report.ReportError):
            report.resolve_baseline(self.repo, base, fetch=False, require_hash=True)

    def test_stats_symlink_is_rejected(self) -> None:
        self.baseline()
        path = self.repo / ".castiron.stats.yml"
        original = path.read_text()
        path.unlink()
        path.symlink_to(original)
        with self.assertRaisesRegex(report.ReportError, "regular Git file"):
            report.read_stats(self.repo, self.commit())

    def test_public_snapshot_rejects_private_governance_and_unpublished_paths(self) -> None:
        entry = report.Entry(b"100644", "a" * 40)
        blocked = [
            b".castiron/private.json",
            b".github/CODEOWNERS",
            b".gitmodules",
            b"CODEOWNERS",
            b"SECURITY.md",
            b"docs/SECURITY.md",
        ]
        for path in blocked:
            with (
                self.subTest(path=path),
                mock.patch.object(
                    report, "tree_entries", side_effect=[{path: entry}, {path: entry}]
                ),
                mock.patch.object(report, "read_blobs") as read,
            ):
                with self.assertRaisesRegex(report.ReportError, "private or governance"):
                    report.copy_generated_tree(self.repo, "a" * 40, self.repo, "b" * 40)
                read.assert_not_called()
        with (
            mock.patch.object(report, "tree_entries", side_effect=[{b"unreleased.py": entry}, {}]),
            mock.patch.object(report, "read_blobs") as read,
        ):
            with self.assertRaisesRegex(
                report.ReportError, "absent from the approved public SDK tree"
            ):
                report.copy_generated_tree(self.repo, "a" * 40, self.repo, "b" * 40)
            read.assert_not_called()

    def test_zero_new_files_summary_reports_existing_changes(self) -> None:
        _, clean = self.baseline()
        self.write("generated.py", "generated\n# existing customization\n")
        base = self.commit()
        self.write("generated.py", "generated\n# existing customization updated\n")
        result, _ = report.build_report(self.repo, base, self.commit())
        body = report.render_report(result)
        self.assertIn("✅ No new custom-code files detected.", body)
        self.assertIn("1 mixed file remains; 1 existing customization changed.", body)
        self.assertNotIn("0 newly customized", body)
        empty, _ = report.build_report(self.repo, clean, clean)
        self.assertIn(
            "0 mixed files remain; 0 existing customizations changed.", report.render_report(empty)
        )

    def test_new_mixed_file_headline_includes_changed_generated_baselines(self) -> None:
        _, base = self.baseline()
        result, _ = report.build_report(self.repo, base, base)
        for category in ("baseline_changed", "newly_generation_owned"):
            result["files"] = [
                {
                    "path": "generated.py",
                    "category": category,
                    "custom_before": False,
                    "custom_after": True,
                    "added": "1",
                    "removed": "1",
                }
            ]
            body = report.render_report(result)
            self.assertNotIn("No new custom-code files", body)
            self.assertIn("1 newly customized", body)

    @unittest.skipUnless(shutil.which("node"), "GitHub Actions JavaScript runtime")
    def test_trusted_failure_publisher_updates_one_current_comment(self) -> None:
        workflow = (
            Path(__file__).resolve().parents[2]
            / ".github/workflows/castiron-custom-code-comment.yml"
        )
        section = workflow.read_text().split("- name: Publish a trusted failure status\n", 1)[1]
        script = textwrap.dedent(section.split("script: |\n", 1)[1])
        harness = r"""
const assert = require('node:assert/strict');
const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
async function check(stale, exists, priorRun, expected) {
  const writes = [];
  const event = {id: 20, run_attempt: 1, event: 'pull_request', path: '.github/workflows/castiron-custom-code.yml', head_sha: 'a'.repeat(40), pull_requests: [{number: 1}]};
  const current = {state: 'open', head: {sha: (stale ? 'c' : 'a').repeat(40)}};
  const previous = {id: 42, user: {type: 'Bot', login: 'github-actions[bot]'},
    body: `<!-- castiron:custom-code-report:v1 -->\n<!-- castiron:run:v1:${priorRun}:1 -->`};
  const github = {paginate: async () => exists ? [previous] : [], rest: {
    pulls: {get: async () => ({data: current})},
    issues: {listComments() {}, updateComment: async x => writes.push(['update', x]),
      createComment: async x => writes.push(['create', x])}}};
  const context = {payload: {workflow_run: event}, repo: {owner: 'openai', repo: 'example'},
    runId: 20, serverUrl: 'https://github.com'};
  await new AsyncFunction('github', 'context', SCRIPT)(github, context);
  assert.equal(writes.length, expected ? 1 : 0);
  if (expected) {
    assert.equal(writes[0][0], expected);
    assert.match(writes[0][1].body, /Report unavailable/);
    assert.match(writes[0][1].body, /castiron:run:v1:20:1/);
  }
}
(async () => {
  await check(false, true, 10, 'update');
  await check(false, false, 10, 'create');
  await check(true, true, 10, null);
  await check(false, true, 21, null);
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
        subprocess.run(
            ["node", "-e", "const SCRIPT = " + json.dumps(script) + ";\n" + harness],
            check=True,
            env={**os.environ, "GITHUB_RUN_ATTEMPT": "1"},
        )

    def test_workflow_reports_all_branches_without_write_credentials(self) -> None:
        workflows = Path(__file__).resolve().parents[2] / ".github/workflows"
        producer = (workflows / "castiron-custom-code.yml").read_text()
        publisher = (workflows / "castiron-custom-code-comment.yml").read_text()
        self.assertIn("pull_request:", producer)
        self.assertNotIn("CASTIRON_CUSTOM_CODE_BRANCHES", producer + publisher)
        self.assertNotIn("pull-requests: write", producer)
        self.assertNotIn("head.repo.full_name ==", producer)
        self.assertIn("workflow_run:", publisher)
        self.assertIn("ref: ${{ github.workflow_sha }}", publisher)
        self.assertNotIn("ref: ${{ github.event.pull_request.head.sha }}", publisher)
        self.assertIn("persist-credentials: false", publisher)
        self.assertIn("--report", publisher)
        compute, comment = publisher.split("\n  comment:\n", 1)
        self.assertNotIn("pull-requests: write", compute)
        self.assertIn("pull-requests: read", compute)
        self.assertIn(" trusted-report ", compute)
        self.assertNotIn("download-artifact@", compute)
        self.assertNotIn("unittest", compute)
        self.assertIn("needs: compute", comment)
        self.assertIn("artifact-ids: ${{ needs.compute.outputs.artifact-id }}", comment)
        self.assertNotIn("run-id: ${{ github.event.workflow_run.id }}", comment)
        self.assertNotIn("git fetch", comment)
        self.assertIn("--artifact-run-id", comment)
        digest = hashlib.sha256(
            (workflows.parents[1] / "scripts/castiron/custom_code_report.py").read_bytes()
        ).hexdigest()
        self.assertIn(f"REPORTER_SHA256: {digest}", producer)

    def test_comment_only_rerun_links_to_the_compute_artifact_attempt(self) -> None:
        workflow = (
            Path(__file__).resolve().parents[2]
            / ".github/workflows/castiron-custom-code-comment.yml"
        ).read_text()
        compute, comment = workflow.split("\n  comment:\n", 1)

        def field(section: str, prefix: str) -> str:
            return next(
                line.removeprefix(prefix)
                for line in section.splitlines()
                if line.startswith(prefix)
            )

        def resolve(value: str, context: dict[str, str]) -> str:
            for key, replacement in context.items():
                value = value.replace("${{ " + key + " }}", replacement)
            self.assertNotIn("${{", value)
            return value

        # A successful compute job's outputs survive a comment-only rerun.
        compute_context = {"github.run_id": "9", "github.run_attempt": "3"}
        uploaded_name = resolve(field(compute, "          name: "), compute_context)
        saved_attempt = resolve(field(compute, "      artifact-run-attempt: "), compute_context)
        comment_context = {
            "github.run_id": "9",
            "github.run_attempt": "4",
            "needs.compute.outputs.artifact-run-attempt": saved_attempt,
        }
        artifact_attempt = resolve(
            field(comment, "          ARTIFACT_RUN_ATTEMPT: "), comment_context
        )
        self.assertEqual(uploaded_name, "castiron-custom-code-9-3")
        self.assertEqual(artifact_attempt, "3")

        _, base = self.baseline()
        result, _ = report.build_report(self.repo, base, base)
        pull = {"state": "open", "head": {"sha": base}, "base": {"sha": base}}
        run = {
            "event": "pull_request",
            "path": ".github/workflows/castiron-custom-code.yml",
            "head_sha": base,
            "run_attempt": 1,
            "pull_requests": [{"number": 1}],
        }
        with mock.patch.object(
            report, "api", side_effect=[pull, run, [], pull, {"html_url": "published"}]
        ) as api:
            self.assertEqual(
                report.publish_comment(
                    result,
                    "openai/example",
                    1,
                    2,
                    1,
                    artifact_run_id=9,
                    artifact_run_attempt=int(artifact_attempt),
                ),
                "published",
            )
        body = api.call_args.args[2]["body"]
        self.assertIn(f"--name {uploaded_name}", body)
        self.assertNotIn("--name castiron-custom-code-9-4", body)
        self.assertIn("castiron:run:v1:2:1", body)

    def test_trusted_report_recomputes_pr_output_in_a_bare_repository(self) -> None:
        generated, _ = self.baseline()
        content_hash = report.hash_codegen_commit(self.repo, generated)
        snapshot = report.create_public_snapshot(
            self.repo,
            self.git("rev-parse", f"{generated}^{{tree}}"),
            GENERATION,
            content_hash,
            "codegen/public-test",
            None,
        )
        self.git("branch", "codegen/public-test", snapshot)
        stats = (self.repo / ".castiron.stats.yml").read_text()
        self.write(".castiron.stats.yml", stats + f"public_codegen_sha: {snapshot}\n")
        base = self.commit()
        legitimate, _ = report.build_report(self.repo, base, base, require_head_hash=True)
        self.write("generated.py", "generated\n# custom\n")
        # Neither a replacement reporter nor its claimed result may be executed
        # or read by the trusted job.
        self.write("scripts/castiron/custom_code_report.py", "raise RuntimeError('PR code ran')\n")
        self.write("report.json", json.dumps(legitimate))
        head = self.commit()
        broken_stats = (
            (self.repo / ".castiron.stats.yml").read_text().replace(content_hash, "0" * 64)
        )
        self.write(".castiron.stats.yml", broken_stats)
        broken = self.commit()
        remote = self.repo / "public.git"
        self.git("clone", "--bare", str(self.repo), str(remote))
        real_git = report.git

        def local_git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
            if args[:3] == ("remote", "add", "origin"):
                self.assertEqual(args[3], "https://github.com/openai/example.git")
                args = (*args[:3], str(remote))
            self.assertNotIn("checkout", args)
            return real_git(repo, *args, input_bytes=input_bytes)

        for label, revision in (("genuine", base), ("custom", head), ("broken", broken)):
            with self.subTest(label=label):
                calls: list[tuple[str, str]] = []
                bodies: list[str] = []
                pull = {
                    "state": "open",
                    "head": {"sha": revision},
                    "base": {"sha": base, "repo": {"full_name": "openai/example"}},
                }
                run: dict[str, Any] = {
                    "event": "pull_request",
                    "status": "completed",
                    "path": ".github/workflows/castiron-custom-code.yml",
                    "head_sha": revision,
                    "run_attempt": 1,
                    "pull_requests": [],
                }
                forged: dict[str, Any] = {**legitimate, "head_sha": revision, "files": []}
                self.assertIn("Generated baselines verified", report.render_report(forged))
                producer = self.repo / f"producer-{label}"
                producer.mkdir()
                (producer / "report.json").write_text(json.dumps(forged))

                def fake_api(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
                    calls.append((method, path))
                    if method == "GET":
                        responses: dict[str, Any] = {
                            "repos/openai/example": {"private": False},
                            "repos/openai/example/actions/runs/2": run,
                            f"repos/openai/example/commits/{revision}/pulls?per_page=100": [
                                {"number": 1}
                            ],
                            "repos/openai/example/pulls/1": pull,
                            "repos/openai/example/issues/1/comments?per_page=100&page=1": [],
                        }
                        if path in responses:
                            return responses[path]
                    if (
                        method == "POST"
                        and path == "repos/openai/example/issues/1/comments"
                        and payload
                    ):
                        bodies.append(payload["body"])
                        return {
                            "html_url": "https://github.com/openai/example/pull/1#issuecomment-1"
                        }
                    raise AssertionError(f"unexpected API call: {method} {path}")

                objects = self.repo / f"objects-{label}.git"
                out = self.repo / f"trusted-{label}"
                with (
                    mock.patch.object(report, "api", side_effect=fake_api),
                    mock.patch.object(report, "git", side_effect=local_git),
                ):
                    report.trusted_report(objects, "openai/example", 2, 1, out)
                    self.assertTrue(all(method == "GET" for method, _ in calls))
                    self.assertEqual(
                        real_git(objects, "rev-parse", "--is-bare-repository"), b"true\n"
                    )
                    self.assertFalse((objects / "scripts").exists())
                    actual = json.loads((out / "report.json").read_text())
                    report.publish_comment(
                        actual,
                        "openai/example",
                        1,
                        2,
                        1,
                        artifact_run_id=9,
                        artifact_run_attempt=3,
                    )
                self.assertEqual(len(bodies), 1)
                body = bodies[0]
                self.assertIn("castiron:run:v1:2:1", body)
                self.assertIn("/actions/runs/9", body)
                if label == "broken":
                    self.assertIn("Report unavailable", body)
                    self.assertNotIn("Generated baselines verified", body)
                elif label == "custom":
                    self.assertIn("1 newly customized", body)
                    self.assertIn("generated.py", body)
                    self.assertIn(b"+# custom", (out / "custom-code.patch").read_bytes())
                    self.assertNotIn("No new custom-code files detected", body)
                else:
                    self.assertIn("No new custom-code files detected", body)
                    self.assertIn("Generated baselines verified", body)
                    self.assertIn("--name castiron-custom-code-9-3", body)

    def test_trusted_report_rejects_invalid_or_stale_association_before_fetch(self) -> None:
        run = {
            "event": "pull_request",
            "status": "completed",
            "path": ".github/workflows/castiron-custom-code.yml",
            "head_sha": "a" * 40,
            "run_attempt": 1,
            "pull_requests": [{"number": 1}],
        }
        pull = {
            "state": "open",
            "head": {"sha": "a" * 40},
            "base": {"sha": "b" * 40, "repo": {"full_name": "openai/example"}},
        }
        cases: list[tuple[list[Any], bool]] = [
            ([{**run, "path": "other.yml"}], True),
            ([{**run, "status": "in_progress"}], True),
            ([{**run, "run_attempt": 2}], False),
            ([run, {**pull, "state": "closed"}], False),
            ([run, {**pull, "head": {"sha": "c" * 40}}], False),
            (
                [run, {**pull, "base": {"sha": "b" * 40, "repo": {"full_name": "other/repo"}}}],
                False,
            ),
            ([{**run, "pull_requests": []}, []], False),
            ([{**run, "pull_requests": [{"number": 1}, {"number": 2}]}, pull, pull], True),
        ]
        for responses, raises in cases:
            with (
                self.subTest(responses=responses),
                mock.patch.object(report, "api", side_effect=responses),
                mock.patch.object(report, "git") as git,
            ):
                if raises:
                    with self.assertRaises(report.ReportError):
                        report.trusted_report(
                            self.repo / "objects", "openai/example", 2, 1, self.repo / "out"
                        )
                else:
                    report.trusted_report(
                        self.repo / "objects", "openai/example", 2, 1, self.repo / "out"
                    )
                git.assert_not_called()
                self.assertFalse((self.repo / "out").exists())

    def test_removals_include_changed_baselines_but_not_handwritten_only_files(self) -> None:
        _, base = self.baseline()
        result, _ = report.build_report(self.repo, base, base)
        result["files"] = [
            {
                "path": category,
                "category": category,
                "custom_before": True,
                "custom_after": False,
                "added": "0",
                "removed": "0",
            }
            for category in ("baseline_changed", "no_longer_generated")
        ]
        self.assertIn("1 customizations removed", report.render_report(result))
        result["files"].append(
            {
                "path": "new.py",
                "category": "newly_customized",
                "custom_before": False,
                "custom_after": True,
                "added": "1",
                "removed": "0",
            }
        )
        self.assertIn("1 customizations removed", report.render_report(result))

    def test_public_snapshot_has_no_private_history_and_reports_without_private_remote(
        self,
    ) -> None:
        self.write("private-only.txt", "must never be published\n")
        private_ancestor = self.commit("private history")
        (self.repo / "private-only.txt").unlink()
        generated, base = self.baseline()
        self.git("branch", "codegen/test", generated)
        private_remote = self.repo / "private.git"
        self.git("clone", "--bare", str(self.repo), str(private_remote))
        self.git("remote", "add", "origin", str(private_remote))

        public = self.repo / "public"
        public.mkdir()
        report.git(public, "init", "-q", "-b", "main")
        report.git(public, "config", "user.name", "Public test")
        report.git(public, "config", "user.email", "public@example.test")
        (public / "generated.py").write_text("generated\n")
        (public / ".castiron.stats.yml").write_text(
            (self.repo / ".castiron.stats.yml").read_text().split("codegen_hash:")[0]
        )
        report.git(public, "add", ".")
        report.git(public, "commit", "-qm", "already public")
        public_base = report.git(public, "rev-parse", "HEAD").decode().strip()
        public_remote = self.repo / "public.git"
        report.git(public, "clone", "--bare", str(public), str(public_remote))
        report.git(public, "remote", "add", "origin", str(public_remote))
        snapshot = report.prepare_public_snapshot(
            self.repo, base, base, public, public_base, "castiron/promotions/pr-1"
        )
        self.assertNotEqual(snapshot["commit"], generated)
        self.assertEqual(report.git(public, "rev-list", "--count", snapshot["commit"]), b"1\n")
        self.assertEqual(report.hash_codegen_commit(public, snapshot["commit"]), snapshot["hash"])
        with self.assertRaises(report.ReportError):
            report.git(public, "cat-file", "-e", private_ancestor)
        self.assertNotIn(
            b"private-only.txt", report.git(public, "ls-tree", "-r", snapshot["commit"])
        )
        report.git(
            public, "push", "origin", f"{snapshot['commit']}:refs/heads/{snapshot['branch']}"
        )
        (public / "generated.py").write_text("generated\n# custom\n")
        report.git(public, "add", ".")
        report.git(public, "commit", "-qm", "public customization")
        public_head = report.git(public, "rev-parse", "HEAD").decode().strip()
        result, patch = report.build_report(
            public, public_base, public_head, fetch=True, require_head_hash=True, public=True
        )
        self.assertEqual(result["counts"]["newly_customized"], 1)
        self.assertIn(b"+# custom", patch)
        self.assertIn(" --public", report.render_report(result))
        self.assertFalse(result["before"]["hash_recorded"])
        again = report.prepare_public_snapshot(
            self.repo, base, base, public, public_base, "castiron/promotions/pr-1"
        )
        self.assertEqual(again["commit"], snapshot["commit"])
        tree = report.git(public, "rev-parse", f"{snapshot['commit']}^{{tree}}").decode().strip()
        message = report.git(public, "show", "-s", "--format=%B", snapshot["commit"])
        chained = (
            report.git(
                public,
                "commit-tree",
                tree,
                "-p",
                snapshot["commit"],
                "-F",
                "-",
                input_bytes=message,
            )
            .decode()
            .strip()
        )
        report.git(
            public, "push", "--force", "origin", f"{chained}:refs/heads/{snapshot['branch']}"
        )
        reused = report.prepare_public_snapshot(
            self.repo, base, base, public, public_base, "castiron/promotions/pr-1"
        )
        self.assertEqual(reused["commit"], chained)

        # A fresh generation may introduce files. Its public parent must be a
        # previously public snapshot, never the private checkpoint parent.
        next_generation = "650e8400-e29b-41d4-a716-446655440000"
        self.git("checkout", "--detach", generated)
        self.write("generated.py", "regenerated\n")
        self.write("new.py", "new generated file\n")
        self.git("add", "--", "generated.py", "new.py")
        metadata = base64.b64encode(
            json.dumps(
                {
                    "generation_id": next_generation,
                    "source_branch": "test",
                }
            ).encode()
        ).decode()
        self.git("commit", "-qm", f"next codegen\n\nGeneration metadata: {metadata}")
        next_codegen = self.git("rev-parse", "HEAD")
        self.git("push", "origin", f"{next_codegen}:refs/heads/codegen/test")
        self.write(
            ".castiron.stats.yml",
            (
                f"schema_version: 1\ngeneration_id: {next_generation}\n"
                f"codegen_sha: {next_codegen}\n"
                f"codegen_hash: {report.hash_codegen_commit(self.repo, next_codegen)}\n"
            ),
        )
        self.git("add", "--", ".castiron.stats.yml")
        self.git("commit", "-qm", "next integrated SDK")
        next_head = self.git("rev-parse", "HEAD")
        # An unreviewed path in private HEAD is not enough to publish it.
        with self.assertRaisesRegex(report.ReportError, "approved public SDK tree"):
            report.prepare_public_snapshot(
                self.repo, base, next_head, public, public_base, "castiron/promotions/pr-1"
            )
        # Model normal promotion applying its reviewed patch to the public index.
        (public / "generated.py").write_text("regenerated\n")
        (public / "new.py").write_text("new generated file\n")
        report.git(public, "add", "--", "generated.py", "new.py")
        advanced = report.prepare_public_snapshot(
            self.repo, base, next_head, public, public_base, "castiron/promotions/pr-1"
        )
        self.assertEqual(
            report.git(public, "rev-parse", advanced["commit"] + "^1").decode().strip(), chained
        )
        self.assertEqual(report.hash_codegen_commit(public, advanced["commit"]), advanced["hash"])
        with self.assertRaises(report.ReportError):
            report.git(public, "cat-file", "-e", next_codegen)
        report.git(
            public, "push", "origin", f"{advanced['commit']}:refs/heads/{advanced['branch']}"
        )
        (public / "generated.py").write_text("regenerated\n")
        (public / "new.py").write_text("new generated file\n")
        report.git(public, "add", "--", ".castiron.stats.yml", "generated.py", "new.py")
        report.git(public, "commit", "-qm", "next public SDK")
        next_public = report.git(public, "rev-parse", "HEAD").decode().strip()
        compared, _ = report.build_report(
            public, public_base, next_public, fetch=True, require_head_hash=True, public=True
        )
        self.assertEqual(compared["before"]["generation_id"], GENERATION)
        self.assertEqual(compared["after"]["generation_id"], next_generation)

        # Once A lands, handwritten-only promotion B may reuse A's exact
        # snapshot. Its original branch is a locator, not exclusive ownership.
        report.git(public, "push", "origin", f"{next_public}:refs/heads/main")
        self.write("generated.py", "regenerated\n# handwritten change\n")
        self.git("add", "--", "generated.py")
        self.git("commit", "-qm", "handwritten change")
        custom_head = self.git("rev-parse", "HEAD")
        (public / "generated.py").write_text("regenerated\n# handwritten change\n")
        report.git(public, "add", "--", "generated.py")
        other_branch = "castiron/promotions/pr-2"
        other = report.prepare_public_snapshot(
            self.repo, next_head, custom_head, public, next_public, other_branch
        )
        self.assertEqual(other["commit"], advanced["commit"])
        self.assertEqual(
            report.public_metadata(public, other["commit"])["Branch"], advanced["branch"]
        )
        report.git(public, "push", "origin", f"{other['commit']}:refs/heads/{other['branch']}")
        retried = report.prepare_public_snapshot(
            self.repo, next_head, custom_head, public, next_public, other_branch
        )
        self.assertEqual(retried["commit"], other["commit"])

        # A merge-queue commit also resolves the baseline from its own stats,
        # independently of the name or parents of the integrated SDK commit.
        merged_tree = report.git(public, "write-tree").decode().strip()
        pr_head = (
            report.git(
                public,
                "commit-tree",
                merged_tree,
                "-p",
                next_public,
                "-m",
                "public handwritten change",
            )
            .decode()
            .strip()
        )
        merged = (
            report.git(
                public,
                "commit-tree",
                merged_tree,
                "-p",
                next_public,
                "-p",
                pr_head,
                "-m",
                "merge queue",
            )
            .decode()
            .strip()
        )
        merged_report, _ = report.build_report(
            public, next_public, merged, fetch=True, require_head_hash=True, public=True
        )
        self.assertEqual(merged_report["after"]["commit"], advanced["commit"])
        self.assertEqual(merged_report["counts"]["newly_customized"], 1)

    def test_comment_updates_existing_bot_comment_and_skips_stale(self) -> None:
        _, base = self.baseline()
        result, _ = report.build_report(self.repo, base, base)
        calls: list[tuple[str, str, object]] = []

        def fake_api(method: str, path: str, payload: object = None) -> object:
            calls.append((method, path, payload))
            if "/pulls/" in path:
                return {"state": "open", "head": {"sha": base}, "base": {"sha": base}}
            if "/actions/runs/" in path:
                return {
                    "event": "pull_request",
                    "path": ".github/workflows/castiron-custom-code.yml",
                    "head_sha": base,
                    "run_attempt": 1,
                    "pull_requests": [{"number": 1}],
                }
            if "/comments?" in path:
                return [
                    {"id": 7, "user": {"login": "someone"}, "body": report.MARKER},
                    {
                        "id": 8,
                        "user": {"login": "github-actions[bot]"},
                        "body": report.MARKER,
                        "html_url": "existing",
                    },
                ]
            return {"html_url": "updated"}

        with mock.patch.object(report, "api", side_effect=fake_api):
            self.assertEqual(report.publish_comment(result, "openai/example", 1, 2, 1), "updated")
            self.assertEqual(calls[-1][:2], ("PATCH", "repos/openai/example/issues/comments/8"))
            calls.clear()
            result["head_sha"] = "f" * 40
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 1), "Skipped stale report"
            )
            self.assertEqual(len(calls), 1)

    def test_comment_rejects_older_runs_attempts_and_wrong_pr(self) -> None:
        _, base = self.baseline()
        result, _ = report.build_report(self.repo, base, base)
        pull = {"state": "open", "head": {"sha": base}, "base": {"sha": base}}
        run = {
            "event": "pull_request",
            "path": ".github/workflows/castiron-custom-code.yml",
            "head_sha": base,
            "run_attempt": 2,
            "pull_requests": [{"number": 1}],
        }
        comment = {
            "id": 8,
            "user": {"login": "github-actions[bot]"},
            "body": report.MARKER + "\n<!-- castiron:run:v1:3:1 -->",
            "html_url": "existing",
        }
        with mock.patch.object(report, "api", side_effect=[pull, run]) as api:
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 1), "Skipped stale report"
            )
            self.assertEqual(api.call_count, 2)
        with mock.patch.object(report, "api", side_effect=[pull, run, [comment]]) as api:
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 2), "Skipped stale report"
            )
            self.assertEqual(api.call_count, 3)
        with (
            mock.patch.object(report, "api", side_effect=[pull, {**run, "pull_requests": []}, []]),
            self.assertRaisesRegex(report.ReportError, "does not match report PR"),
        ):
            report.publish_comment(result, "openai/example", 1, 2, 2)
        with (
            mock.patch.object(report, "api", side_effect=[pull, {**run, "path": "other.yml"}]),
            self.assertRaisesRegex(report.ReportError, "does not match report PR"),
        ):
            report.publish_comment(result, "openai/example", 1, 2, 2)
        with mock.patch.object(
            report,
            "api",
            side_effect=[pull, {**run, "pull_requests": []}, [{"number": 1}], [comment]],
        ) as api:
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 2), "Skipped stale report"
            )
            self.assertIn(f"/commits/{base}/pulls", api.call_args_list[2].args[1])
        changed = {**pull, "head": {"sha": "f" * 40}}
        with mock.patch.object(report, "api", side_effect=[pull, run, [], changed]) as api:
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 2), "Skipped stale report"
            )
            self.assertEqual(api.call_count, 4)


if __name__ == "__main__":
    unittest.main()
