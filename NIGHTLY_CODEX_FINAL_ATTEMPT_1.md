Implemented the small fix for issue #2641.

Changed:
- [src/openai/types/completion_usage.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/types/completion_usage.py): added typed support for `completion_tokens_details.text_tokens`, `prompt_tokens_details.image_tokens`, and `prompt_tokens_details.text_tokens`.
- [tests/lib/chat/test_completions_streaming.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/lib/chat/test_completions_streaming.py): added a focused regression test parsing a streaming `ChatCompletionChunk` usage payload.
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md): wrote the required summary.

Verification:
- Passed: `.venv/bin/python -m pytest tests/lib/chat/test_completions_streaming.py::test_chat_completion_chunk_usage_supports_text_and_image_token_details`
- Passed: `.venv/bin/python -m ruff check src/openai/types/completion_usage.py tests/lib/chat/test_completions_streaming.py`

I also attempted direct `pyright` on the touched files, but it failed because this environment’s direct pyright invocation did not resolve installed test dependencies like `pytest`, `httpx`, and `respx`; I recorded that in the report.