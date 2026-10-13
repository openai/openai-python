"""Check private trace storage and numeric export without a browser or an API key."""

import json
import shutil

from diagnostics import RunDiagnostics, DiagnosticCapture, read_diagnostic_trace, diagnostic_observation

secret = "synthetic-private-credential"
capture = DiagnosticCapture((secret,))
try:
    assert capture.directory.stat().st_mode & 0o777 == 0o700
    run = RunDiagnostics(capture, "live")
    run.record(
        "observation",
        diagnostic_observation(
            [
                {"type": "input_text", "text": f"Rule: route this invoice to review. {secret}"},
                {"type": "input_image", "image_url": "data:image/png;base64,PRIVATE_SCREENSHOT"},
            ]
        ),
    )
    run.record(
        "choices",
        [
            {"id": "review", "description": "Send to review", "done": False},
            {"id": "pay", "description": "Pay invoice", "done": False},
            {"id": "done", "description": "Finish", "done": True},
        ],
    )
    run.event(
        {
            "api": "decisions",
            "stage": "request",
            "reason": "completed",
            "call_id": None,
            "member": None,
            "duration_ms": 13,
            "usage": {"input_tokens": 17, "output_tokens": 3, "total_tokens": 20},
        }
    )
    run.event({"api": "decisions", "stage": "selection", "reason": "completed", "call_id": "pay", "usage": None})
    run.record("effect", {"member": "click", "state": {"saved": "paid"}})
    run.record("verification", {"verified": False})
    run.measure("actionMs", 2)
    run.measure("approvalMs", 7)
    run.close()
    assert run.recorder is not None
    assert run.recorder.filename.stat().st_mode & 0o777 == 0o600
    raw = run.recorder.filename.read_text()
    assert secret not in raw and "PRIVATE_SCREENSHOT" not in raw
    trace = read_diagnostic_trace(run.recorder.filename)
    assert not trace["incomplete"]
    assert next(record for record in trace["records"] if record["kind"] == "verification")["data"]["verified"] is False
    assert (
        next(
            record
            for record in trace["records"]
            if isinstance(record["data"], dict) and record["data"].get("stage") == "selection"
        )["data"]["call_id"]
        == "pay"
    )
    assert run.summary(2)["usage"] == {
        "recordedRequests": 1,
        "missingRequests": 1,
        "complete": False,
        "inputTokens": 17,
        "outputTokens": 3,
        "totalTokens": 20,
    }
    assert run.summary(2)["timing"] == {"apiMs": 13, "actionMs": 2, "approvalMs": 7}
    assert "paid" not in json.dumps(run.summary(2))
    assert RunDiagnostics(None, "live").summary(1)["usage"]["inputTokens"] is None

    visual = DiagnosticCapture()
    try:
        try:
            DiagnosticCapture(capture_id=str(visual.directory))
            raise AssertionError("Paths must not select captures")
        except ValueError:
            pass
        recorder = visual.start()
        assert recorder is not None
        pixels = b"x" * (1024 * 1024)
        for sequence in range(1, 11):
            recorder.frame({"sequence": sequence, "owner": "human", "role": "Task", "mime": "image/jpeg"}, pixels)
        recorder.frame({"sequence": 11, "owner": "human", "role": "Task", "mime": "image/jpeg"}, pixels + b"x")
        recorder.close()
        reopened = DiagnosticCapture(capture_id=visual.id)
        assert reopened.traces() == ["run-1"]
        trace = reopened.trace("run-1")
        assert len([entry for entry in trace["records"] if entry["kind"] == "frame"]) == 8
        assert trace["records"][-1]["data"] == {"status": "complete", "omitted": 0, "frames": 8, "omittedFrames": 3}
        assert reopened.frame("run-1", "1")[0] == pixels
        for invalid in ("9", "../1", "01"):
            try:
                reopened.frame("run-1", invalid)
                raise AssertionError("Missing frames must not load")
            except (ValueError, OSError):
                pass
        next_run = reopened.start()
        assert next_run is not None and next_run.filename.name == "run-2.jsonl"
        next_run.record("observation", "Visible literal <button>synthetic note</button>")
        next_run.close()
        assert not any(entry["kind"] == "frame" for entry in reopened.trace("run-2")["records"])
        full = reopened.start()
        assert full is not None
        metadata = {"sequence": 1, "owner": "human", "role": "Task", "mime": "image/jpeg"}
        full.frame(metadata, b"saved frame")
        full.frame(metadata, b"duplicate must not replace or delete saved frame")
        space = 1024 * 1024 - 512 - full.filename.stat().st_size
        full.record("observation", "x" * (space - 80))
        full.frame({**metadata, "sequence": 2}, b"unreferenced frame")
        full.close()
        near_limit = reopened.trace("run-3")
        assert not near_limit["incomplete"]
        assert near_limit["records"][-1]["data"] == {"status": "limited", "omitted": 1, "frames": 1, "omittedFrames": 2}
        assert reopened.frame("run-3", "1")[0] == b"saved frame"
        assert not (reopened.directory / "run-3-2.frame").exists()
        try:
            reopened.frame("run-3", "2")
        except ValueError:
            pass
        else:
            raise AssertionError("Omitted frames must not be readable")
    finally:
        shutil.rmtree(visual.directory)

    bounded = capture.start()
    assert bounded is not None
    bounded.record("run", {"api": "responses", "mode": "rehearsal", "taskId": "reservations"})
    bounded.record("observation", "x" * (1024 * 1024))
    bounded.close()
    assert bounded.status == "limited" and bounded.omitted == 1
    assert len(read_diagnostic_trace(bounded.filename)["records"]) == 2
    assert read_diagnostic_trace(bounded.filename)["records"][-1]["data"] == {
        "status": "limited",
        "omitted": 1,
        "frames": 0,
        "omittedFrames": 0,
    }

    failed = capture.start()
    assert failed is not None
    failed.record("run", {"api": "responses", "mode": "rehearsal", "taskId": "reservations"})
    circular: dict[str, object] = {}
    circular["self"] = circular
    failed.record("observation", circular)
    assert failed.status == "failed"
    assert len(read_diagnostic_trace(failed.filename)["records"]) == 1
    with failed.filename.open("a") as handle:
        handle.write('{"version":')
    damaged = read_diagnostic_trace(failed.filename)
    assert damaged["incomplete"] and len(damaged["records"]) == 1
    malformed = capture.start()
    assert malformed is not None
    malformed.close()
    for kind, data in (
        ("run", {}),
        ("observation", [None]),
        ("choices", [{"id": "save", "description": "Save", "done": None}]),
        ("runner", {"stage": "request"}),
        ("effect", {"member": "click", "state": None}),
        ("verification", {"verified": "yes"}),
        ("capture", {"status": "complete", "omitted": False, "frames": 0, "omittedFrames": 0}),
        ("frame", None),
        ("frame", {"sequence": 1, "owner": "human", "role": "Task"}),
    ):
        prefix = {"version": 1, "kind": "observation", "atMs": 0, "data": "retained prefix"}
        malformed.filename.write_text(
            "\n".join(
                json.dumps(record)
                for record in (
                    prefix,
                    {"version": 1, "kind": kind, "atMs": 1, "data": data},
                    {
                        "version": 1,
                        "kind": "capture",
                        "atMs": 2,
                        "data": {"status": "complete", "omitted": 0, "frames": 0, "omittedFrames": 0},
                    },
                )
            )
        )
        assert capture.trace("run-4") == {"records": [prefix], "incomplete": True}, kind
        try:
            capture.frame("run-4", "1")
        except ValueError:
            pass
        else:
            raise AssertionError("Malformed frame survived the prefix check")
    for _ in range(4, 16):
        recorder = capture.start()
        assert recorder is not None
        recorder.close()
    assert capture.start() is None
    print("PASS private trace, wrong-choice evidence, redaction, unknown usage, bounds and failure isolation")
finally:
    shutil.rmtree(capture.directory)
