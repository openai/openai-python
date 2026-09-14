# JSON serialization benchmarks

These benchmarks are intentionally outside `tests/`: performance measurements are hardware-sensitive and do not run
in normal unit-test or CI commands.

Run the complete suite on one otherwise-idle machine:

```sh
uv run --locked --all-extras pytest benchmarks/test_json_serialization.py \
  -n 0 \
  --benchmark-only \
  --benchmark-autosave \
  --benchmark-json=benchmark-results/json-serialization.json
```

The command prints a statistics table, saves the machine and interpreter metadata with the raw samples under
`.benchmarks/`, and writes a portable JSON result file to `benchmark-results/`. Neither generated-results directory
is intended for source control.

| Encoded payload | Representative use case |
| --- | --- |
| 835 B | Small tool arguments and an individual streaming event |
| 3,983 B | Short requests, responses, and structured outputs |
| 18,162 B | Larger responses and moderate chat requests |
| 63,078 B | Mid-sized context between chat and RAG workloads |
| 288,712 B | RAG context and long conversation history |
| 1,127,848 B | Large context and large tool results |

`test_openapi_dumps` isolates serializer CPU. `test_build_request` measures the SDK's actual
`BaseClient._build_request()` path with a pre-built payload and no network request. That outbound code is shared by
REST requests and the request which starts a streaming response. It does not benchmark endpoint parameter
transformation, provider/network latency, or parsing incoming SSE events; this change cannot speed those events.

The two serializers are compared as the application uses them: both return UTF-8 `bytes`, with payload construction
outside the timed section. The stdlib baseline is exactly `json.dumps(..., ensure_ascii=False, separators=(",", ":"),
allow_nan=False).encode("utf-8")`; correctness tests assert compact UTF-8 output and byte-for-byte equality for the
benchmark payloads. Each case also asserts its exact encoded byte length; the pytest ID and pyperf benchmark name use
that length.

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
  --scope=serialization --serializer=stdlib --rigorous -o benchmark-results/serialization-stdlib.json

uv run --locked --all-extras python benchmarks/json_serialization.py \
  --scope=serialization --serializer=orjson --rigorous -o benchmark-results/serialization-orjson.json

uv run --locked --all-extras pyperf check benchmark-results/serialization-stdlib.json
uv run --locked --all-extras pyperf check benchmark-results/serialization-orjson.json

uv run --locked --all-extras pyperf compare_to --table --table-format=md \
  benchmark-results/serialization-stdlib.json benchmark-results/serialization-orjson.json
```

Repeat the same commands with `--scope=request-preparation` and distinct output filenames to rigorously measure the
no-network SDK request-preparation path. Run `pyperf check` for both result files before comparing them. Neither
scope is an end-to-end asynchronous-client latency benchmark.
