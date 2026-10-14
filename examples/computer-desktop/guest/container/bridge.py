"""Give the existing fixed action handler one private stream, with no listening port."""

import os
import sys
import socket

left, right = socket.socketpair()
pid = os.fork()
if pid == 0:
    left.close()
    os.dup2(right.fileno(), 3, inheritable=True)
    os.environ["LISTEN_PID"] = str(os.getpid())
    os.environ["LISTEN_FDS"] = "1"
    os.execv(sys.executable, [sys.executable, "-I", "/opt/desktop/action.py"])

right.close()
try:
    left.settimeout(14)
    left.sendall(sys.stdin.buffer.readline(16385))
    left.shutdown(socket.SHUT_WR)
    total = 0
    while block := left.recv(65536):
        total += len(block)
        if total > 6 * 1024 * 1024:
            raise RuntimeError("Fixed desktop reply exceeded its limit.")
        sys.stdout.buffer.write(block)
finally:
    left.close()
    _, status = os.waitpid(pid, 0)
    if status:
        raise RuntimeError("Desktop action did not finish.")
