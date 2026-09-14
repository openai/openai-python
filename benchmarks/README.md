# JSON serialization benchmarks

These benchmarks are intentionally outside `tests/`: performance measurements are hardware-sensitive and do not run
in normal unit-test or CI commands.

Run the complete suite on one otherwise-idle machine:

```sh
uv run --locked --all-extras pytest benchmarks/test_json_serialization.py \
  -n 0 \
  --benchmark-only \
  --benchmark-autosave \
  --benchmark-histogram=benchmark-results/json-serialization
```

The command prints a statistics table, saves the machine and interpreter metadata with the raw samples under
`.benchmarks/`, and writes an SVG histogram to `benchmark-results/`. Neither directory is intended for source
control.

For a branch comparison, first save a run from each checkout, then compare their JSON result files:

```sh
uv run --locked --all-extras pytest-benchmark compare --between=median,mean baseline.json candidate.json
```

The benchmark compares the exact previous `json.dumps()` implementation with `openapi_dumps()`. It measures
serialization CPU only. When evaluating async clients, retain the thread-offload proposed in #3815: the benchmark
does not model event-loop scheduling or network I/O.
