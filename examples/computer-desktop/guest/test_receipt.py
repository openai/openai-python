"""No-key VM receipt tests. Never run vfkit or boot test images."""

from __future__ import annotations

import os
import sys
import json
import select
import shutil
import signal
import hashlib
import tempfile
import unittest
import subprocess
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import setup

LEGACY = "d7ea5a8ba6b12769814cd9e49c087b62253d86bd449d6b0d8d52b7c4ddbd7767"
LEGACY_BUILD = "c9e6a0fef444b7a0ef32035650a95ca85d20f0ee422bab65a707588d05a9a5fe"
# Original guest files and media from local driver revision 47032ac6, with its
# accepted original provisioning build. Later guest edits must never alter this fixture.
LEGACY_RECIPE = {
    "preseed.cfg": "4da7885186bb7256c42774f592d67a3de6b2eccce3ae31c517c1bb3c4889d2dc",
    "finish-guest.sh": "c4ba6e4aa50c337aa5708732b62c67e81f8a2b80a6aeca2bb0508bfb0f3c7ba6",
    "init-media.sh": "94e7c89067584fdaa3630c24b82ddd7e4885d4ff8eacc9fa47d5c85c73ff027b",
    "desktop.service": "53676eaace1d99a22d1bdec1d793e9749028bf9130fae514076814bcb2dc297c",
    "desktop-action.socket": "9171a00af875f25a61d350578f4900da35ab144767847c51c9faf9ce89fd6540",
    "desktop-action@.service": "c018ee75e12e7bedebed7891ea7fc78f2d963a48ed4558626bf54b1146ee70e5",
    "action.py": "7feda4fd7b96df4f874529a90f8b8d2e297e9b3b96499c5206a02d4041fcecea",
    "start.py": "fd2732f2f3347cfd1e8bdca63da5d2f69af9c8874fd936d42f265ce54577f291",
    "fixture.html": "372e2fab899edd561230cdf3223da42aba27c4fb6bafedda7d23080544514203",
    "install.py": "0dc2d946f10d40a1c8dc47429e3e29eb982893cf6166dc44f4e6ebcf88830619",
    "media": "b5518444d59ab634224906d0586cb2fafe9f2a6e28ae7dcc28620667bc266f1d",
    "build": "c9e6a0fef444b7a0ef32035650a95ca85d20f0ee422bab65a707588d05a9a5fe",
}


def changed_build(*_args: object) -> None:
    raise AssertionError("Validation may not build anything")


class ReceiptTests(unittest.TestCase):
    def test_sigterm_reaps_staged_installer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "build/inputs"
            inputs.mkdir(parents=True)
            (inputs / "install.py").write_text(
                "import os,signal,sys\nfrom pathlib import Path\n"
                "root=Path(sys.argv[2])\n"
                "def stop(*_):\n (root/'drained').write_text('installer cleanup'); sys.exit(0)\n"
                "signal.signal(signal.SIGINT,stop)\n"
                "print(os.getpid(),flush=True)\n"
                "signal.pause()\n"
            )
            code = (
                "import sys;from pathlib import Path;"
                "sys.path.insert(0,sys.argv[1]);import setup;"
                "root=Path(sys.argv[2]);sys.argv=['setup.py','--runtime-dir',str(root)];"
                "setup.setup=lambda root,*args:setup.run_staged_installer(root);"
                "setup.main();(root/'unexpected').write_text('completed')"
            )
            child = None
            with subprocess.Popen(
                [sys.executable, "-E", "-S", "-c", code, str(HERE), str(root)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ) as owner:
                try:
                    assert owner.stdout is not None
                    ready, _, _ = select.select([owner.stdout], [], [], 5)
                    self.assertTrue(ready, "installer did not become ready")
                    child = int(owner.stdout.readline())
                    owner.send_signal(signal.SIGTERM)
                    self.assertNotEqual(owner.wait(timeout=5), 0)
                    self.assertEqual((root / "drained").read_text(), "installer cleanup")
                    self.assertFalse((root / "unexpected").exists())
                    with self.assertRaises(ProcessLookupError):
                        os.kill(child, 0)
                finally:
                    if owner.poll() is None:
                        owner.kill()
                        owner.wait()
                    if child is not None:
                        try:
                            os.kill(child, signal.SIGKILL)
                        except ProcessLookupError:
                            # The installer was already reaped by its owner.
                            pass

    def test_offline_media_uses_verified_private_copies(self) -> None:
        self.check_offline_media(False)

    def test_offline_media_rejects_changed_staged_copy(self) -> None:
        self.check_offline_media(True)

    def check_offline_media(self, corrupt: bool) -> None:
        with tempfile.TemporaryDirectory() as directory:
            area = Path(directory)
            source = area / "source"
            (source / "extra").mkdir(parents=True)
            root = area / "runtime"
            contents = {setup.DVD_NAME: b"checked dvd", "extra/one.deb": b"checked package"}
            media = tuple(
                setup.Media(name, "https://example.test/unused", len(data), hashlib.sha256(data).hexdigest(), "sha256")
                for name, data in contents.items()
            )
            for name, data in contents.items():
                (source / name).write_bytes(data)
            vfkit = area / "vfkit"
            vfkit.write_bytes(b"fixture executable, never run")
            original_check = setup.check_media
            original_copy = shutil.copyfile

            def check_then_change_cache(path: Path) -> None:
                original_check(path)
                for name, data in contents.items():
                    (source / name).write_bytes(b"x" * len(data))

            def copy(source_path: Path, target_path: Path) -> object:
                result = original_copy(source_path, target_path)
                if corrupt and target_path == root / "build/downloads" / setup.DVD_NAME:
                    target_path.write_bytes(b"bad staged bytes")
                return result

            def command(args: list[str], **_kwargs: object) -> None:
                if args[0] == "/usr/bin/codesign":
                    return
                self.assertEqual(args[0], "/usr/bin/bsdtar")
                dvd = Path(args[2])
                self.assertEqual(dvd, root / "build/downloads" / setup.DVD_NAME)
                self.assertEqual(dvd.read_bytes(), contents[setup.DVD_NAME])
                self.assertEqual((root / "build/bp22/extra/one.deb").read_bytes(), contents["extra/one.deb"])
                raise RuntimeError("Stop before media extraction")

            # The production fingerprint includes the real host build functions.
            # Capture it before these tests replace host operations with local probes.
            with patch.object(setup, "MEDIA", media):
                initial_recipe = setup.recipe()
            with (
                patch.object(setup, "MEDIA", media),
                patch.object(setup, "recipe", return_value=initial_recipe),
                patch.object(setup.platform, "system", return_value="Darwin"),
                patch.object(setup.platform, "machine", return_value="arm64"),
                patch.object(setup, "executable", return_value=vfkit),
                patch.object(setup.os, "access", return_value=True),
                patch.object(setup.shutil, "disk_usage", return_value=SimpleNamespace(free=20 * 1024**3)),
                patch.object(setup, "check_media", side_effect=check_then_change_cache),
                patch.object(setup.shutil, "copyfile", side_effect=copy),
                patch.object(setup, "command", side_effect=command),
                patch.object(setup, "run_staged_installer", side_effect=AssertionError("No guest may run")),
            ):
                if corrupt:
                    with self.assertRaisesRegex(ValueError, "Wrong Debian media bytes"):
                        setup.build(root, source, vfkit, vfkit)
                else:
                    with self.assertRaisesRegex(RuntimeError, "Stop before media extraction"):
                        setup.build(root, source, vfkit, vfkit)

    def test_build_checks_private_binary_before_downloading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            area = Path(directory)
            source = area / "source-vfkit"
            source.write_bytes(b"trusted fixture bytes")
            root = area / "runtime"
            checked: list[Path] = []

            def verify_command(args: list[str], **_kwargs: object) -> None:
                self.assertEqual(args[:3], ["/usr/bin/codesign", "--verify", "--strict"])
                checked.append(Path(args[3]))
                self.assertEqual(checked[-1].read_bytes(), b"trusted fixture bytes")

            def stop_download(_directory: Path) -> None:
                source.write_bytes(b"source replaced during download")
                raise RuntimeError("Stop before fixture download")

            initial_recipe = setup.recipe()
            with (
                patch.object(setup, "recipe", return_value=initial_recipe),
                patch.object(setup.platform, "system", return_value="Darwin"),
                patch.object(setup.platform, "machine", return_value="arm64"),
                patch.object(setup, "executable", return_value=source),
                patch.object(setup.os, "access", return_value=True),
                patch.object(setup.shutil, "disk_usage", return_value=SimpleNamespace(free=20 * 1024**3)),
                patch.object(setup, "command", side_effect=verify_command),
                patch.object(setup, "download", side_effect=stop_download),
                patch.object(setup, "run_staged_installer", side_effect=AssertionError("No guest may run")),
            ):
                with self.assertRaisesRegex(RuntimeError, "Stop before fixture download"):
                    setup.build(root, None, source, source)
            self.assertEqual(checked, [root / "bin/vfkit"])
            self.assertEqual((root / "bin/vfkit").read_bytes(), b"trusted fixture bytes")

    def prepare_runtime(self) -> None:
        self.directory = tempfile.TemporaryDirectory(
            dir="/private/tmp" if sys.platform == "darwin" else None, prefix="vrc-"
        )
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for name in ("runs", "bin", "build"):
            (self.root / name).mkdir(mode=0o700)
        self.binary = self.root / "bin/vfkit"
        self.binary.write_bytes(b"test data, never executable by the tests\n")
        self.binary.chmod(0o700)
        self.disk = self.root / "build/desktop.raw"
        with self.disk.open("xb") as file:
            file.truncate(16 * 1024**3)
        self.disk.chmod(0o400)
        self.record = {
            "recipe": setup.recipe(),
            "disk": setup.disk_identity(self.root),
            "vfkit": setup.digest(self.binary),
        }
        self.save()

    def save(self) -> None:
        receipt = self.root / "setup.json"
        receipt.write_text(json.dumps(self.record))
        receipt.chmod(0o600)

    def legacy(self, launcher: str = LEGACY) -> None:
        recipe = self.record["recipe"]
        assert isinstance(recipe, dict)
        self.record["recipe"] = {
            **{name: recipe[name] for name in (*setup.GUEST_FILES, "install.py")},
            "setup.py": launcher,
        }
        self.save()

    def assert_launch_refused(self) -> None:
        if (HERE.parent / "guest.mjs").exists():
            subprocess.run(["node", str(HERE.parent / "receipt-test.mjs"), str(self.root)], check=True, timeout=30)
        else:
            sys.path.insert(0, str(HERE.parent))
            sys.path.insert(0, str(HERE.parents[2] / "src"))
            import guest

            from openai.lib.computer import ComputerUseError

            original = subprocess.Popen
            attempted: list[object] = []

            def guarded_popen(args: list[str], *rest: object, **kwargs: object) -> object:
                if Path(args[0]) == self.binary:
                    attempted.append(args)
                    raise AssertionError("Test blocked guest spawn")
                return original(args, *rest, **kwargs)  # type: ignore[call-overload]

            with patch("subprocess.Popen", guarded_popen):
                with self.assertRaises((ComputerUseError, ValueError, OSError)):
                    guest.Guest(self.root)
            self.assertEqual(attempted, [])
        self.assertEqual(list((self.root / "runs").iterdir()), [])

    def test_current_runtime_is_valid(self) -> None:
        self.prepare_runtime()
        setup.verify(self.root)

    def test_runtime_alias_and_writable_parent(self) -> None:
        self.prepare_runtime()
        with tempfile.TemporaryDirectory(
            dir="/private/tmp" if sys.platform == "darwin" else None, prefix="va-"
        ) as temporary:
            parent = Path(temporary)
            moved = parent / "runtime"
            self.root.rename(moved)
            alias = parent / "alias"
            alias.symlink_to(moved, target_is_directory=True)
            setup.verify(alias)
            parent.chmod(0o777)
            try:
                with self.assertRaisesRegex(ValueError, "ancestor"):
                    setup.verify(moved)
            finally:
                parent.chmod(0o700)

    @unittest.skipUnless(sys.platform == "darwin" and setup.platform.machine() == "arm64", "Mac VM preflight")
    def test_known_legacy_requires_original_build(self) -> None:
        self.prepare_runtime()
        current = setup.recipe()
        self.legacy()
        with self.assertRaisesRegex(ValueError, "does not match"):
            setup.verify(self.root)
        # The old build hash alone must not authorize today's guest files.
        with (
            patch.object(setup, "recipe", return_value={**current, "build": LEGACY_BUILD}),
            self.assertRaisesRegex(ValueError, "does not match"),
        ):
            setup.verify(self.root)

        for launcher in (
            "83aca5abddda1de4c378f039bbf8d03919e7b8fa040eea3f7b73f74165f5371b",
            "e7dd9dca9752560369f1ea9d8e2eb6a515a52c7f03f95868a00e046f1b8279f2",
            LEGACY,
        ):
            with self.subTest(launcher=launcher):
                self.record["recipe"] = dict(LEGACY_RECIPE)
                self.legacy(launcher)
                with patch.object(setup, "recipe", return_value=LEGACY_RECIPE):
                    setup.verify(self.root)
                for field in ("build", "media", "action.py"):
                    with (
                        self.subTest(changed=field),
                        patch.object(setup, "recipe", return_value={**LEGACY_RECIPE, field: "0" * 64}),
                        self.assertRaisesRegex(ValueError, "does not match"),
                    ):
                        setup.verify(self.root)

        self.record["recipe"] = dict(LEGACY_RECIPE)
        self.legacy("0" * 64)
        with (
            patch.object(setup, "recipe", return_value=LEGACY_RECIPE),
            self.assertRaisesRegex(ValueError, "does not match"),
        ):
            setup.verify(self.root)

    def test_missing_receipt(self) -> None:
        self.prepare_runtime()
        (self.root / "setup.json").unlink()
        self.assert_launch_refused()

    def test_changed_binary(self) -> None:
        self.prepare_runtime()
        self.binary.write_bytes(b"substituted data that must never execute\n")
        self.assert_launch_refused()

    def test_replaced_same_size_readonly_disk(self) -> None:
        self.prepare_runtime()
        replacement = self.root / "build/replacement.raw"
        with replacement.open("xb") as file:
            file.truncate(16 * 1024**3)
        replacement.chmod(0o400)
        os.replace(replacement, self.disk)
        self.assert_launch_refused()

    def test_unknown_legacy_launcher(self) -> None:
        self.prepare_runtime()
        self.legacy("0" * 64)
        self.assert_launch_refused()

    def test_changed_guest_recipe(self) -> None:
        self.prepare_runtime()
        recipe = self.record["recipe"]
        assert isinstance(recipe, dict)
        recipe["action.py"] = "0" * 64
        self.save()
        self.assert_launch_refused()

    def test_unexpected_receipt_field(self) -> None:
        self.prepare_runtime()
        self.record["extra"] = "unused"
        self.save()
        self.assert_launch_refused()

    def test_wrong_receipt_permissions(self) -> None:
        self.prepare_runtime()
        (self.root / "setup.json").chmod(0o644)
        self.assert_launch_refused()

    def test_receipt_rejects_changed_media(self) -> None:
        self.prepare_runtime()
        first, *rest = setup.MEDIA
        with patch.object(setup, "MEDIA", (first._replace(digest="0" * len(first.digest)), *rest)):
            with self.assertRaisesRegex(ValueError, "does not match"):
                setup.verify(self.root)
        setup.verify(self.root)

    def test_receipt_rejects_changed_provisioning(self) -> None:
        self.prepare_runtime()
        with patch.object(setup, "build", changed_build):
            with self.assertRaisesRegex(ValueError, "does not match"):
                setup.verify(self.root)
        setup.verify(self.root)

    def test_verify_only_missing_path_never_provisions(self) -> None:
        self.prepare_runtime()
        missing = self.root / "absent"
        result = subprocess.run(
            [sys.executable, "-E", "-S", str(HERE / "setup.py"), "--runtime-dir", str(missing), "--verify-only"],
            capture_output=True,
            timeout=30,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
