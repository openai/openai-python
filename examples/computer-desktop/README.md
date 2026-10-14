# Isolated desktop

Run a browser and a native editor inside a private Debian guest. The sample
routes a synthetic ticket and saves its receipt in Mousepad. It never controls
your personal desktop. It verifies the two resulting records independently.

Use an Apple-silicon Mac with vfkit and xorriso, or an ARM64 Linux host with
Docker that supports user namespaces and Chromium's sandbox. See the
[guest setup instructions](guest/README.md) for prerequisites and checked media.
From the SDK source root:

```sh
python3 -m venv .venv-desktop
. .venv-desktop/bin/activate
python -m pip install openai Pillow==12.3.0
python examples/computer-desktop/guest/setup.py --runtime-dir /tmp/desktop-$USER
python examples/computer-desktop/exercise.py --runtime-dir /tmp/desktop-$USER
```

Setup selects the supported platform, verifies its media and records the built
runtime. It reuses a matching runtime. The exercise uses no API key and starts
and removes its own guests.

VM setup and launch resolve the runtime to its canonical path. Each ancestor must
belong to root or the current user and must not be writable by other users
unless it is a sticky directory such as /private/tmp. The example trusts the
current host user; it does not protect against that user's deliberate file
replacement.

The VM launcher keeps a parent-liveness pipe open. If the SDK process crashes
or is killed, a small foreground owner stops and reaps its exact VM child.
Normal Stop still removes the private run directory. After a forced SDK exit
or host reboot, run directories can remain; remove them manually only after
all owners using that runtime have stopped.

After it passes, set `OPENAI_API_KEY` and `OPENAI_MODEL` on the host. Use a
model that supports the computer tool:

```sh
python examples/computer-desktop/run.py --live --runtime-dir /tmp/desktop-$USER
```

This uses the Responses API and can spend API credits. Approve the local task
in the terminal; Ctrl-C stops and removes its guest. Credentials stay in the
host SDK client. The host does not mount a personal profile or send a general
shell command to the guest.

`verify()` observes intermediate records. `seal()` stops the guest writers
before returning final records; the runner checks those again. The last image
is the frame captured before shutdown. A sealed workspace refuses further
input. Stop still removes it.

The native transport accepts a bounded 16 KiB request, checks every coordinate
and key before input, and gives each admitted command a deadline. A lost input
receipt retires that guest; the sample never retries uncertain input. See
[the ComputerDriver guide](../../docs/browser-providers.md#computerdriver) for the SDK protocol.
