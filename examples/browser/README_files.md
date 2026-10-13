# Approved files in an owned browser

These Python 3.10+ exercises use real local Chromium without an API key or
provider request. The original exercises register `upload` and `download`
as ordinary functions with `AsyncResponsesToolRunner`. The portable exercise
uses the optional `upload_file` and `download_file` members in
`AsyncBrowserToolset`. It connects to local Chromium through CDP and tests two local sources.
The default browser tools do not include either file member.

Follow the [browser setup](README.md) to get the released example files and
install the SDK, Playwright, and Chromium. Run these commands from the
unpacked release's root. If you are in `examples`, run `cd ..` first.

```sh
. .venv-browser/bin/activate
python examples/browser/exercise_upload.py
python examples/browser/exercise_download.py
python examples/browser/exercise_portable_files.py
```

The fixtures run only on loopback. Each owner stages files in its own private
area under the system temporary directory.
A launcher must explicitly grant file access; the default permits nothing.
Approval must return `True`. The upload function accepts only a grant ID. The owner reads a bounded copy
from a generated file under its upload root. The grant binds that copy to the
original document, record, input, session and expiry.
After admission, an uncertain native delivery returns `unknown`. The owner
will not replay it. Stop revokes new work and stops waiting for a pending approval callback.
It drains preparation and any admitted transfer, then removes staging. The callback may finish
later, but its result cannot start a transfer. An interrupted approval's grant cannot be reused.
Stop does not wait for unrelated work in the caller's task.

The application controls the staged file until preparation freezes its bytes.
This example assumes other processes running as the same OS user are trusted;
it does not isolate files from that user before preparation. Later path changes
cannot alter an issued grant's frozen bytes.

The caller supplies the original record and control handles and the expected
record ID before it creates either owner. Select controls in trusted application
code, not from model arguments. For example, with handles `record` and `control`:

```python
owner = await DownloadOwner.create(
    page,
    {"allow_download": True, "record": record, "control": control, "record_id": record_id},
    approve,
)
grant = owner.issue({"url": source_url, "count": expected_count, "sha256": expected_digest}, expires_at)
driver.download_file = owner.download_file
tools = AsyncBrowserToolset(driver, members=["download_file"], confirm=confirm)
```

`source_url`, size, digest and expiry come from trusted application data.
`expires_at` is absolute milliseconds. Use `UploadOwner.create` with
`allow_upload` and an original file-input handle for uploads. Its existing
`prepare(root, name, expires_at)` returns a grant after it reads the private
staging root. Only the grant ID goes to the tool. Both the tool confirmation
and the owner approval must allow the call; the owner checks the same original
page and controls again after approval. The methods accept a per-call
`cancelled` predicate. An aborted call does not retire unrelated owner work.

The download owner copies one grant for an HTTPS source or a literal loopback
HTTP source. It refuses credentials in the URL, fragments, redirects and
ambient cookies, auth and proxy configuration. It checks the expected byte count and
digest before reporting completion. The model cannot choose an endpoint,
header, path or name. The application reads at most 65,537 raw bytes,
including one byte to detect overflow; the quarantine file never exceeds
65,536 bytes. Header size is checked after HTTPX parses it and before the
application consumes the body. This is not a parser, OS, RSS or browser
temporary-file limit. The owner rejects redirects and unsupported content.
An admitted uncertain read cannot replay. Timeout or cancellation removes
the partial file.

An owner also exposes `owner.state()`. It returns version 1, direction, the current transfer
outcome, cleanup status, and at most 32 recent changes. `earlier_omitted` is true when older
changes were dropped. Preparation failures appear in the recent list and do not replace a transfer
already in progress. A busy or retired owner records a refusal without replacing that outcome.
Changing the returned snapshot cannot change the owner.

Transfer status is `in_progress`, `refused`, `interrupted`, `unknown`, or `completed`.
The separate `effect` is `none` until transfer admission, `unknown` once delivery may have
started, and `completed` only after the final identity and content checks. For example,
`{"status":"interrupted","effect":"unknown"}` means Stop caught admitted work; it does not
mean the page received nothing. A later Stop does not relabel an earlier timeout as interruption.
Cleanup is `not_started`, `pending`, or `completed`. It stays pending when drain or removal
has not completed; the application can await `stop()` again.

State contains fixed values, with no paths, file names, contents, grants, URLs, credentials,
sizes, digests, or error text. The existing `receipt()` still returns the original per-call
transfer result. To expose state to a model, explicitly register an ordinary function:

```python
async def file_status(_: dict[str, object]) -> str:
    return json.dumps(owner.state())

runner = AsyncResponsesToolRunner(functions=[AsyncRegisteredFunction(
    {
        "type": "function",
        "name": "file_status",
        "description": "Read bounded transfer and cleanup outcomes.",
        "strict": True,
        "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
    },
    file_status,
)])
```

The exercises register this alongside the grant-only transfer function. A stopped runner never
silently resumes to report status. Read state locally, or make a separate authorized runner call
that registers only the capabilities it still permits.

Ordinary browser downloads remain blocked. A quarantined file cannot be rendered, run or exported by the model.
It cannot be attached to a model or reused as an upload.
The local CDP proof covers two synthetic services. It does not establish behavior
on arbitrary or authenticated remote sites, or a production isolation boundary.
