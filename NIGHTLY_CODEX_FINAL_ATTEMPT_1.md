Implemented the nightly patch for issue #2724.

Changed:
- [file_batches.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/resources/vector_stores/file_batches.py:330): `file_batches.poll` no longer sends `X-Stainless-Poll-Helper`, matching normal `retrieve` behavior while still polling locally.
- [vector_store_file_batch.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/types/vector_stores/vector_store_file_batch.py:41): fixed the batch object literal to `vector_store.file_batch`.
- [test_file_batches.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/api_resources/vector_stores/test_file_batches.py:239): added sync/async regression tests asserting `poll` returns the file batch id and does not send the poll-helper header.
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md): added the required report.

Validation:
- Focused regression tests: `4 passed, 1 skipped`
- `ruff format --check`: passed
- `ruff check`: passed

The full generated file test run was attempted, but unrelated tests require the Steady mock server on `127.0.0.1:4010` and failed with connection errors. The new respx-backed tests do not require that server and passed.