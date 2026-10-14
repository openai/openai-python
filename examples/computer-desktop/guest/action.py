"""One bounded action on the socket supplied by the guest service manager."""

import os
import json
import stat
import time
import fcntl
import base64
import socket
import struct
import tempfile
import subprocess
from typing import cast
from pathlib import Path

ROOT = Path("/run/desktop")
OWNER = Path("/run/desktop-owner")
WIDTH, HEIGHT = 1024, 768
MODS = {
    "CTRL": "Control_L",
    "CONTROL": "Control_L",
    "SHIFT": "Shift_L",
    "ALT": "Alt_L",
    "META": "Super_L",
    "CMD": "Super_L",
    "SUPER": "Super_L",
}
KEYS = {
    **MODS,
    "ENTER": "Return",
    "TAB": "Tab",
    "BACKSPACE": "BackSpace",
    "DELETE": "Delete",
    "ESC": "Escape",
    "ESCAPE": "Escape",
    "SPACE": "space",
    "ARROWUP": "Up",
    "ARROWDOWN": "Down",
    "ARROWLEFT": "Left",
    "ARROWRIGHT": "Right",
    "HOME": "Home",
    "END": "End",
    "PAGEUP": "Page_Up",
    "PAGEDOWN": "Page_Down",
}
BUTTONS = {"left": 1, "wheel": 2, "right": 3, "back": 8, "forward": 9}
FIELDS: dict[str, set[str]] = {
    "click": {"x", "y", "button", "keys"},
    "double_click": {"x", "y", "keys"},
    "drag": {"path", "keys"},
    "keypress": {"keys"},
    "move": {"x", "y", "keys"},
    "scroll": {"x", "y", "scroll_x", "scroll_y", "keys"},
    "type": {"text"},
    "wait": set(),
    "screenshot": set(),
    "ready": set(),
    "verify": set(),
    "seal": set(),
}


class Invalid(ValueError):
    pass


def number(value: object, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise Invalid("Invalid coordinate or amount.")
    return value


def point(value: dict[str, object]) -> tuple[int, int]:
    return number(value.get("x"), 0, WIDTH - 1), number(value.get("y"), 0, HEIGHT - 1)


def validate(raw: object) -> tuple[dict[str, object], list[str]]:
    if type(raw) is not dict:
        raise Invalid("Expected an action.")
    value = cast(dict[str, object], raw)
    kind = value.get("type")
    if type(kind) is not str:
        raise Invalid("Expected an action.")
    if kind not in FIELDS or not set(value).issubset({"type"} | FIELDS[kind]):
        raise Invalid("Unsupported action.")
    if kind in ("click", "double_click", "move", "scroll"):
        point(value)
    if kind == "click" and value.get("button") not in BUTTONS:
        raise Invalid("Unsupported button.")
    if kind == "scroll":
        number(value.get("scroll_x"), -2048, 2048)
        number(value.get("scroll_y"), -2048, 2048)
    if kind == "drag":
        path = value.get("path")
        if type(path) is not list:
            raise Invalid("Drag requires 2..100 points.")
        path = cast(list[object], path)
        if not 2 <= len(path) <= 100:
            raise Invalid("Drag requires 2..100 points.")
        for item in path:
            if type(item) is not dict:
                raise Invalid("Invalid drag point.")
            item = cast(dict[str, object], item)
            if set(item) != {"x", "y"}:
                raise Invalid("Invalid drag point.")
            point(item)
    if kind == "type":
        text = value.get("text")
        if type(text) is not str:
            raise Invalid("Text must be a string.")
        if "\0" in text:
            raise Invalid("Text cannot contain NUL.")
        try:
            text.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise Invalid("Text must be Unicode scalar values.") from exc
    keys = value.get("keys")
    if keys is None:
        keys = cast(list[object], [])
    if type(keys) is not list:
        raise Invalid("Too many held keys.")
    keys = cast(list[object], keys)
    if kind == "keypress" and not keys:
        raise Invalid("Keypress requires keys.")
    if len(keys) > 5:
        raise Invalid("Too many held keys.")
    mapped: list[str] = []
    for index, key in enumerate(keys):
        if type(key) is not str:
            raise Invalid("Unsupported key.")
        name = key.upper()
        terminal = kind == "keypress" and index == len(keys) - 1
        choices = KEYS if terminal else MODS
        if terminal and name in MODS:
            raise Invalid("Keypress requires a final nonmodifier key.")
        if name in choices:
            actual = choices[name]
        elif terminal and len(name) == 1 and "A" <= name <= "Z":
            actual = name.lower()
        else:
            raise Invalid("Unsupported key.")
        if actual in mapped:
            raise Invalid("Duplicate key.")
        mapped.append(actual)
    return value, mapped


def cmd(*argv: str) -> bytes:
    return subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, check=True, timeout=5).stdout


def xdo(*argv: object) -> None:
    cmd("xdotool", *(str(arg) for arg in argv))


def inspect_outputs() -> dict[str, object]:
    """Read only the two fixed receipt files; live writes cannot block or exceed the limit."""
    contents: list[bytes | None] = []
    for path in (ROOT / "result.txt", OWNER / "events.jsonl"):
        try:
            fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | os.O_NOFOLLOW)
            try:
                info = os.fstat(fd)
                data = os.read(fd, 8193) if stat.S_ISREG(info.st_mode) and info.st_size <= 8192 else None
                contents.append(data if data is not None and len(data) <= 8192 else None)
            finally:
                os.close(fd)
        except FileNotFoundError:
            contents.append(b"")
        except OSError:
            contents.append(None)
    text, raw = contents
    expected = (json.dumps({"id": "D-2201", "action": "route"}) + "\n").encode("utf-8")
    return {
        "ok": True,
        "file_matches": text in (b"Desktop receipt D-2201", b"Desktop receipt D-2201\n"),
        "browser_matches": raw == expected,
        "file_empty": text == b"",
        "browser_effects": len(raw.splitlines()) if raw is not None else None,
    }


def reply(request: object) -> dict[str, object]:
    action, keys = validate(request)
    kind = action["type"]
    if kind == "ready":
        return {"ok": (OWNER / "display-ready").is_file()}
    sealed = OWNER / "sealed"
    if sealed.is_file() and kind not in ("seal", "verify", "screenshot"):
        return {"ok": False, "uncertain": False, "error": "Completed desktop is read-only."}
    if kind == "seal" and not sealed.is_file():
        cmd("scrot", "--overwrite", str(OWNER / "final-frame.png"))
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as owner:
            owner.settimeout(7)
            owner.connect(str(OWNER / "owner.sock"))
            owner.sendall(b"seal\n")
            with owner.makefile("rb") as response:
                if response.readline(9) != b"sealed\n":
                    raise Invalid("Fixture did not stop its writers.")
        sealed.touch()
    if kind in ("verify", "seal"):
        return inspect_outputs()
    if kind == "screenshot":
        with tempfile.TemporaryDirectory(prefix="capture-", dir=OWNER) as directory:
            if sealed.is_file():
                path = OWNER / "final-frame.png"
            else:
                path = Path(directory) / "frame.png"
                cmd("scrot", "--overwrite", str(path))
            size = path.stat().st_size
            if not 24 <= size <= 4 * 1024 * 1024:
                raise Invalid("Screenshot size limit.")
            png = path.read_bytes()
            if png[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack(">II", png[16:24]) != (
                WIDTH,
                HEIGHT,
            ):
                raise Invalid("Screenshot viewport mismatch.")
            return {
                "ok": True,
                "image_url": "data:image/png;base64," + base64.b64encode(png).decode("ascii"),
            }
    if kind != "wait":
        # Once this fixed task has both committed receipts, later input needs
        # a fresh workspace. Refuse before xdotool can queue a new edit.
        proof = inspect_outputs()
        if proof["file_matches"] and proof["browser_matches"]:
            return {
                "ok": False,
                "uncertain": False,
                "error": "Completed desktop is read-only; seal it or start a new workspace.",
            }
    down: list[str] = []
    mouse_down = False
    try:
        for key in keys:
            down.append(key)
            xdo("keydown", "--", key)
        if kind in ("click", "double_click", "move", "scroll"):
            x, y = point(action)
            xdo("mousemove", x, y)
        if kind == "click":
            xdo("click", BUTTONS[cast(str, action["button"])])
        elif kind == "double_click":
            xdo("click", "--repeat", 2, "--delay", 80, 1)
        elif kind == "drag":
            drag_path = cast(list[dict[str, object]], action["path"])
            x, y = point(drag_path[0])
            xdo("mousemove", x, y)
            mouse_down = True
            xdo("mousedown", 1)
            for item in drag_path[1:]:
                x, y = point(item)
                xdo("mousemove", x, y)
        elif kind == "scroll":
            for amount, negative, positive in (
                (cast(int, action["scroll_y"]), 4, 5),
                (cast(int, action["scroll_x"]), 6, 7),
            ):
                if amount:
                    # X11 reports wheel notches. Round CSS pixel deltas up to 120px/notch.
                    count = (abs(amount) + 119) // 120
                    xdo(
                        "click",
                        "--repeat",
                        count,
                        "--delay",
                        5,
                        negative if amount < 0 else positive,
                    )
        elif kind == "type":
            text = cast(str, action["text"]).replace("\r\n", "\r").replace("\n", "\r")
            xdo("type", "--delay", 0, "--clearmodifiers", "--", text)
        elif kind == "wait":
            time.sleep(0.25)
    finally:
        cleanup_error = None
        if mouse_down:
            try:
                xdo("mouseup", 1)
            except (OSError, subprocess.SubprocessError) as exc:
                cleanup_error = exc
        for key in reversed(down):
            try:
                xdo("keyup", "--", key)
            except (OSError, subprocess.SubprocessError) as exc:
                cleanup_error = exc
        if cleanup_error:
            raise cleanup_error
    return {"ok": True}


def main() -> None:
    pid = os.environ.pop("LISTEN_PID", None)
    count = os.environ.pop("LISTEN_FDS", None)
    os.environ.pop("LISTEN_FDNAMES", None)
    if pid != str(os.getpid()) or count != "1":
        raise RuntimeError("One service-manager connection is required.")
    os.set_inheritable(3, False)
    with socket.socket(fileno=3) as connection:
        if connection.type != socket.SOCK_STREAM:
            raise RuntimeError("A stream connection is required.")
        peer = connection.getpeername()
        if connection.family == getattr(socket, "AF_VSOCK", None) and peer[0] != getattr(
            socket, "VMADDR_CID_HOST", None
        ):
            raise RuntimeError("Only the host may request desktop actions.")
        connection.settimeout(10)
        with connection.makefile("rb") as stream:
            try:
                raw = stream.readline(16385)
                if len(raw) > 16384:
                    raise Invalid("Action size limit exceeded.")
                request = json.loads(raw)
                # Invalid requests cannot imply an attempted operation.
                validate(request)
            except (Invalid, UnicodeError, ValueError, TypeError):
                result = {
                    "ok": False,
                    "uncertain": False,
                    "error": "Unsupported or invalid action.",
                }
            else:
                try:
                    # The private runtime inode is shared by this guest's action processes.
                    descriptor = os.open(OWNER, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
                    try:
                        fcntl.flock(descriptor, fcntl.LOCK_EX)
                        result = reply(request)
                    finally:
                        os.close(descriptor)
                except (OSError, ValueError, subprocess.SubprocessError, TypeError):
                    result = {
                        "ok": False,
                        "uncertain": request["type"] not in ("ready", "verify", "screenshot"),
                        "error": "Desktop operation failed.",
                    }
        payload = (json.dumps(result, ensure_ascii=True) + "\n").encode("ascii")
        if len(payload) > 6 * 1024 * 1024:
            raise RuntimeError("Action reply size limit exceeded.")
        connection.sendall(payload)


if __name__ == "__main__":
    main()
