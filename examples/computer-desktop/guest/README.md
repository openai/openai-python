# Set up the fixed desktop guest

Run one command from the SDK source root on an Apple-silicon Mac:

```sh
python3 examples/computer-desktop/guest/setup.py --runtime-dir /private/tmp/desktop-$UID
```

Setup finds vfkit and xorriso on your PATH. It downloads the fixed Debian DVD
and two packages, checks their pinned hashes, and builds the guest.
It needs no SDK install or API key. It creates a new private runtime directory
and makes its installed guest disk read-only.

## Before the first run

Use Python 3.10 or later on macOS with Virtualization.framework access. The
tested tools are vfkit 0.6.2 and xorriso 1.5.8.pl02. Setup requires a valid
macOS code signature on vfkit. Obtain trusted builds from the upstream
[vfkit project](https://github.com/crc-org/vfkit) and
[xorriso project](https://www.gnu.org/software/xorriso/). Verify their release
signatures or source tags before use. vfkit's upstream README also documents
its Homebrew installation. If you build vfkit, run `make` from the verified
source; its Makefile signs the executable with the virtualization entitlement.
Put both executables on PATH, or pass their absolute paths:

```sh
python3 examples/computer-desktop/guest/setup.py \
  --runtime-dir /private/tmp/desktop-$UID \
  --vfkit /absolute/path/to/vfkit --xorriso /absolute/path/to/xorriso
```

Setup does not install tools or services on your Mac. macOS supplies bsdtar and
codesign. Allow at least 12 GiB free for the original 3.7 GiB DVD, a remastered
DVD and installed blocks in a 16 GiB sparse disk. A guest requests 4 CPUs and
4 GiB of memory; two-guest exercises request twice that.

The runtime path must be short and absolute and cannot contain spaces, commas
or percent signs. Setup checks it against the macOS Unix socket limit before
creating anything. Do not put it in the SDK checkout or use a directory that
contains personal files. Use an unused path if your chosen directory already
exists.

## Downloads and offline inputs

The default command fetches Debian 12.13 ARM64 DVD-1 from the Debian CD
archive. It gets two packages from the matching dated Bookworm snapshot. The fixed
DVD hash was checked against Debian's signed CD manifest. The package hashes
come from its signed ARM64 package index. Setup rejects a different version,
incomplete transfer, hash mismatch, or redirect outside the approved Debian
archive hosts. It does not select newer packages or another image when a file
is unavailable. Downloads stay inside the newly created private runtime.

To reuse original media you already have, pass `--media-dir`. Setup copies the
files into the new private runtime and checks those copies before using them.
The supplied directory needs these inputs at these paths:

```text
media/
  debian-12.13.0-arm64-DVD-1.iso
  extra/xdotool_3.20160805.1-5_arm64.deb
  extra/xvfb_21.1.7-3+deb12u11_arm64.deb
```

```sh
python3 examples/computer-desktop/guest/setup.py \
  --runtime-dir /private/tmp/desktop-$UID --media-dir /absolute/path/to/media
```

This mode reads those originals and leaves them unchanged. You can combine it
with the two executable overrides above.

## Reuse and readiness

Run the same setup command again to validate a completed runtime. If it matches
this recipe, setup exits without downloading, rebuilding, or touching active
runs. A legacy directory, incomplete build, changed recipe or changed disk is
refused and preserved. Use a new runtime path after a failed build; never retry
installation into that disk.

Installation has a 15-minute limit and stops after 180 seconds without disk
progress. The installer owns and reaps its exact vfkit child. The installed
guest has no NIC or host directory shares. Its root disk stays read-only; each
SDK run gets a fresh EFI store, temporary guest filesystems and a private Unix
socket. No passwordless network service is exposed.

A completed installation still needs a native action check. Follow the
[desktop example's no-key exercise](../exercise.py). Run it from the repository root:
Use a Python environment with `openai` and `Pillow==12.3.0` installed.

```sh
python examples/computer-desktop/exercise.py --runtime-dir /private/tmp/desktop-$UID
```

It uses the same runtime
path and verifies the fixed browser ticket and editor receipt. After all of
your SDK owners have stopped and `runs/` is empty, you may remove only the
runtime directory you created. The setup command never deletes an existing
runtime.

## Optional local Linux fixture

On an x86-64 Linux host with local Docker, select the container backend:

```sh
python3 examples/computer-desktop/guest/setup.py \
  --backend container --runtime-dir /tmp/desktop-$UID
```

This is the same fixed synthetic offline browser and editor exercise, with
real screenshots and input. A container shares the host kernel and Docker
daemon; it does not provide the Mac VM's isolation. Do not use this fixture
with secrets or untrusted third-party sites. Mac VM setup remains the default.

You need Python 3.10 or later, x86-64 Linux, and a locally installed Docker
daemon available through `/var/run/docker.sock`. Your user must already be
able to access that socket. Setup does not install host packages, change
daemon policies or start services. Clear Docker context, config, TLS and
builder overrides before running; remote endpoints are refused. Every
command uses a fresh empty private Docker config and the local Unix socket.

Setup builds locally from a pinned Playwright base plus signed Ubuntu desktop
packages from the current Ubuntu archive. Separate fresh builds can resolve
different package versions. Setup records and fixes the resulting local image
ID for that runtime; it does not claim reproducible builds across machines.
It copies only the fixed guest fixture and its Dockerfile to a
private allowlisted context. SDK source, host home files, keys, and credentials
never enter the build or runtime container. The immutable local image ID and
fixture recipe go in `setup.json`. Rerun the same command to validate them.
Run the [no-key exercise](../exercise.py) with this runtime path:

```sh
python examples/computer-desktop/exercise.py --runtime-dir /tmp/desktop-$UID
```

Each SDK owner creates one container with no network, published ports, host
mounts or devices. The control owner and fixed action helper run as root with
only the SETUID, SETGID and KILL capabilities. The browser, editor and display
server run as an unprivileged user with Chromium sandboxing enabled. The
container uses no-new-privileges, private IPC, a read-only root and bounded
memory, CPU, processes and temporary filesystems. The owner sends the existing
fixed action protocol through `docker exec`; it opens no VNC port.
Stop removes only the exact owned container and run directory. It never
deletes an image from the shared Docker cache.

If Docker create or cleanup is interrupted, the owner preserves its run
receipt under `runs/<id>/`. Once the local daemon is available, reconcile and
remove that one run explicitly:

```sh
python3 examples/computer-desktop/container_runtime.py remove \
  --runtime-dir /tmp/desktop-$UID --id <id-from-runs>
```

This command checks the original nonce, name, image and isolation before
removing a container. Linux runtime and run receipts are also tied to their
original path and directory identity. Copies or moves cannot transfer
ownership of a live container. If the container ID is known, cleanup checks
that exact ID even if its name changed. If create failed before an ID arrived,
an empty name lookup is not proof of absence: a pending create might still
finish later. Cleanup keeps that receipt until it can positively reconcile the
original container. A mismatched or incomplete runtime is preserved; choose a new
path instead of rebuilding into it. QEMU, ARM Linux and Docker Desktop have
not been validated by this backend.
