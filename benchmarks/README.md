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

For a release or merge decision, use the more rigorous `pyperf` runner as a second check. It calibrates the loop
count, runs isolated worker processes, records machine metadata, and detects unstable measurements:

```sh
uv run --locked --all-extras python benchmarks/json_serialization.py \
  --serializer=stdlib --rigorous -o benchmark-results/stdlib.json

uv run --locked --all-extras python benchmarks/json_serialization.py \
  --serializer=orjson --rigorous -o benchmark-results/orjson.json

uv run --locked --all-extras pyperf check benchmark-results/stdlib.json
uv run --locked --all-extras pyperf check benchmark-results/orjson.json

uv run --locked --all-extras pyperf compare_to --table --table-format=md \
  benchmark-results/stdlib.json benchmark-results/orjson.json
```

Run `pyperf check` for both result files before comparing them. `pyperf` measures only serializer CPU, just like the
pytest suite; it is not an end-to-end asynchronous-client latency benchmark.
