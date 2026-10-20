"""Start only the disposable fixture display. No host bindings or API client."""

import os
import sys
import json
import time
import signal
import socket
import threading
import subprocess
import http.server
from pathlib import Path

# Isolated Python deliberately omits the script directory. This directory is
# installed read-only for the GUI user; never import from its HOME or cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from action import inspect_outputs

ROOT = Path("/run/desktop")
OWNER = Path("/run/desktop-owner")
children: list[subprocess.Popen[bytes]] = []
writers: list[subprocess.Popen[bytes]] = []


def quiet(self: http.server.BaseHTTPRequestHandler, format: str, *args: object) -> None:
    """The private fixture never records requested URLs."""
    pass


class Fixture(http.server.BaseHTTPRequestHandler):
    log_message = quiet
    timeout = 2

    def do_GET(self) -> None:
        if self.path != "/":
            self.send_error(404)
            return
        content = Path("/opt/desktop/fixture.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        if self.path != "/effect":
            self.send_error(404)
            return
        length = self.headers.get("Content-Length", "")
        if not length.isdecimal() or int(length) > 200:
            self.send_error(400)
            return
        try:
            event = json.loads(self.rfile.read(int(length)))
        except ValueError:
            self.send_error(400)
            return
        if event != {"id": "D-2201", "action": "route"}:
            self.send_error(400)
            return
        with (OWNER / "events.jsonl").open("a", encoding="utf-8") as file:
            file.write(json.dumps(event) + "\n")
        self.send_response(204)
        self.end_headers()


def launch(*argv: str, writer: bool = False) -> subprocess.Popen[bytes]:
    child = subprocess.Popen(
        argv,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=writer,
        user=gui.st_uid,
        group=gui.st_gid,
        extra_groups=[],
        umask=0o022,
    )
    children.append(child)
    if writer:
        writers.append(child)
    return child


def stop(_signal: int, _frame: object) -> None:
    for child in reversed(children):
        if child.poll() is None:
            child.terminate()
    raise SystemExit(0)


signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)
gui = Path(os.environ["HOME"]).stat()
if not ROOT.exists():
    ROOT.mkdir(mode=0o755)
    os.chown(ROOT, gui.st_uid, gui.st_gid)
OWNER.mkdir(mode=0o700, exist_ok=True)
server = http.server.HTTPServer(("127.0.0.1", 4311), Fixture)
serving = threading.Thread(target=server.serve_forever, daemon=True)
serving.start()
control = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
control.bind(str(OWNER / "owner.sock"))
os.chmod(OWNER / "owner.sock", 0o600)
control.listen(1)
control.settimeout(0.2)
launch("Xvfb", ":1", "-screen", "0", "1024x768x24", "-nolisten", "tcp", "-noreset", "-ac")
end = time.monotonic() + 20
while time.monotonic() < end:
    if children[0].poll() is not None:
        raise SystemExit("Private display failed.")
    ready = subprocess.run(["xdpyinfo", "-display", ":1"], capture_output=True, check=False)
    if ready.returncode == 0:
        break
    time.sleep(0.1)
else:
    raise SystemExit("Private display timed out.")
launch("dbus-run-session", "--", "openbox")
# Keep normal browser sandbox behavior. A runtime that cannot start it is unsupported.
launch(
    "chromium",
    "--no-first-run",
    "--disable-sync",
    "--disable-background-networking",
    "--user-data-dir=/home/desktop/chromium",
    "--window-position=0,0",
    "--window-size=510,720",
    "--app=http://127.0.0.1:4311/",
    writer=True,
)
launch("mousepad", "--disable-server", "/run/desktop/result.txt", writer=True)
end = time.monotonic() + 20
while time.monotonic() < end:
    if any(child.poll() is not None for child in children):
        raise SystemExit("A fixture application stopped.")
    windows: list[str] = []
    for app in ("chromium", "mousepad"):
        found = subprocess.run(
            ["xdotool", "search", "--onlyvisible", "--class", app],
            capture_output=True,
            check=False,
            timeout=2,
            text=True,
        )
        matches = found.stdout.splitlines()
        if found.returncode == 0 and matches and matches[0].isdecimal():
            windows.append(matches[0])
    if len(windows) == 2:
        for window, x in zip(windows, (0, 512), strict=True):
            subprocess.run(
                ["xdotool", "windowsize", "--sync", window, "508", "720"],
                check=True,
                capture_output=True,
                timeout=2,
            )
            subprocess.run(
                ["xdotool", "windowmove", "--sync", window, str(x), "0"],
                check=True,
                capture_output=True,
                timeout=2,
            )
        (OWNER / "display-ready").touch()
        break
    time.sleep(0.1)
else:
    raise SystemExit("The browser and editor did not create visible windows.")
sealed = False
while all(child.poll() is None for child in children if not sealed or child not in writers):
    try:
        connection, _ = control.accept()
    except socket.timeout:
        continue
    with connection:
        connection.settimeout(8)
        with connection.makefile("rb") as request:
            if request.readline(8) != b"seal\n":
                continue
        if not sealed:
            # Guest action admission is held. Give both fixed receipts one
            # shared commit budget; only the post-stop read is authoritative.
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                proof = inspect_outputs()
                if proof["file_matches"] and proof["browser_matches"]:
                    break
                time.sleep(min(0.05, max(0, deadline - time.monotonic())))
            # Keep the owned Popen leaders unreaped until both owned groups
            # have been stopped, so their identities cannot be reused.
            for child in writers:
                os.killpg(child.pid, signal.SIGTERM)
            time.sleep(1)
            for child in writers:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    # The owned process group has already exited.
                    pass
            deadline = time.monotonic() + 1
            for child in writers:
                child.wait(timeout=max(0.01, deadline - time.monotonic()))
            # The server is serial. Shutdown waits for any current bounded
            # request before stopping accepts and joining the only writer.
            server.shutdown()
            server.server_close()
            serving.join(timeout=1)
            if serving.is_alive():
                raise RuntimeError("Fixture writer did not stop.")
            sealed = True
        connection.sendall(b"sealed\n")
raise SystemExit("A fixture application stopped.")
