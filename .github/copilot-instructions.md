# OpenAI Python SDK - AI Coding Agent Instructions

## Architecture Overview

This is the official OpenAI Python SDK, generated from OpenAPI specs via [Stainless](https://github.com/stainless-ai/sdk-generator). The codebase has three layers:

1. **Client Layer** (`_client.py`): `OpenAI` and `AsyncOpenAI` classes expose API resources and HTTP methods (`get`, `post`, etc.)
2. **Resource Layer** (`resources/`): Domain-specific classes (e.g., `Batches`, `Chat`, `Embeddings`) inherit from `SyncAPIResource` or `AsyncAPIResource`
3. **Type Layer** (`types/`): Generated Pydantic models for request/response schemas and per-resource params

### Key Insight: Generated vs Manual Code
- Most SDK files are **generated and will be overwritten** by the Stainless generator
- Safe-to-edit directories: `src/openai/lib/`, `examples/`, `tests/`
- Manual patches: Persist between generations but may cause merge conflicts
- See [CONTRIBUTING.md](../CONTRIBUTING.md) for generator details

## Critical Files & Patterns

### Resource Pattern
Every API endpoint follows this pattern:

```python
# src/openai/resources/batches.py
class Batches(SyncAPIResource):
    def create(self, *, param1: str, extra_headers: Headers | None = None) -> Batch:
        return self._post("/v1/batches", body=maybe_transform(...), cast_to=Batch)

class AsyncBatches(AsyncAPIResource):
    async def create(self, ...) -> Batch:
        return await self._post(...)
```

- Both sync and async versions required
- Use `self._post()`, `self._get()`, etc. (inherited from `SyncAPIResource`/`AsyncAPIResource`)
- Transform params via `maybe_transform()` / `async_maybe_transform()`
- Cast responses using `cast_to=` parameter

### Response Types
- Raw response: `APIResponse[T]` with `.parse()` method
- Streaming: `Stream[T]` / `AsyncStream[T]` for server-sent events
- Use `.with_raw_response` property to access raw HTTP data (headers, status)
- Use `.with_streaming_response` for non-eager body reads

### Type System
- Request params live in `types/*_params.py` files (e.g., `batch_create_params.py`)
- Response types in `types/*.py` (e.g., `batch.py` → `Batch` class)
- All models inherit from `BaseModel` (Pydantic v1/v2 compatible via `_models.py`)
- Use `Omit`, `NOT_GIVEN` for optional-but-not-provided distinction
- Type unions: `str | Literal["custom"]` for constrained values

## Development Workflow

### Setup Environment
```bash
# With Rye (preferred)
./scripts/bootstrap          # Auto-provisions Python + venv
rye sync --all-features      # Install dependencies

# Without Rye
pip install -r requirements-dev.lock
```

### Running Tests
```bash
# Requires Prism mock server
npx prism mock openapi.yml &
./scripts/test              # Runs pytest with respx mocking
# Or test against custom endpoint
TEST_API_BASE_URL=https://api.example.com ./scripts/test
```

### Linting & Formatting
```bash
rye run format      # Ruff + docs formatting
rye run lint        # Type checking (Pyright/mypy) + lints
./scripts/lint --fix
```

### Adding Examples
Non-generated, always safe to edit:
```bash
chmod +x examples/my_example.py
./examples/my_example.py    # Runs directly with rye shebang
```

## Testing Patterns

Located in `tests/` and `tests/api_resources/`:

- **Fixtures** (`conftest.py`): `client` (sync) and `async_client` (session-scoped)
- **Response Mocking**: Uses `respx_mock` to mock HTTP responses
- **Strict Validation**: `_strict_response_validation=True` flag validates responses match schemas
- **Test Organization**: Mirror resource structure (e.g., `test_api_resources/test_chat.py` tests `resources/chat/`)

Example test pattern:
```python
def test_create_batch(client: OpenAI) -> None:
    batch = client.batches.create(
        endpoint="/v1/chat/completions",
        input_file_id="file_xyz",
        completion_window="24h"
    )
    assert isinstance(batch, Batch)
```

## Common Development Tasks

### Adding a New Resource Endpoint
1. Create `resources/my_resource.py` with `MyResource(SyncAPIResource)` and `AsyncMyResource(AsyncAPIResource)`
2. Add type definitions in `types/my_resource.py` and `types/my_resource_params.py`
3. Update `_client.py` to expose resource: `self.my_resource = MyResource(self)`
4. Export in `__init__.py`
5. Add tests mirroring the structure

### Fixing Type Validation Issues
- Check `_strict_response_validation=False` in test fixtures to understand field mismatches
- Inspect response models in `types/` to match API responses
- Use `_utils._transform.py` for custom coercion logic

### Working with Optional Parameters
- Use `Omit` type for "don't send this field" vs `None` for "send null"
- Example: `metadata: Metadata | Omit = omit` means optional and not sent by default
- Compare with: `optional_field: str | None` which allows sending None

## Dependencies & Constraints

- **Min Python**: 3.9+ (see `pyproject.toml`)
- **Key Deps**: `httpx>=0.23.0`, `pydantic>=1.9.0`, `typing-extensions>=4.10`, `anyio>=3.5.0`
- **Optional**: `aiohttp` (for `DefaultAioHttpClient`), `websockets>=13` (for realtime)
- **Dev**: Rye, Ruff, Pyright, pytest, respx for mocking

## Conventions & Tips

1. **Import organization**: Absolute imports from package root (not relative)
2. **Error handling**: Use custom exception hierarchy in `_exceptions.py` (e.g., `APIStatusError`, `RateLimitError`)
3. **Streaming**: Check `types/completion.py` for streaming event unions; use `stream=True` param
4. **Pagination**: `SyncCursorPage` / `AsyncCursorPage` with `.auto_paginate_iter()` method
5. **Breaking Changes**: Detected via `scripts/detect-breaking-changes.py`
6. **Files/Uploads**: Use `_files.py` and `file_from_path()` helper for binary handling
7. **Async Context Managers**: Both clients support `async with AsyncOpenAI(...) as client:`

## Debugging & Inspection

- Enable debug logging: `openai.set_debug_logging(True)` or `logging.getLogger("openai").setLevel(logging.DEBUG)`
- Inspect raw responses: Use `.with_raw_response` property for headers, status codes
- Mock server issues: Test against real API with `TEST_API_BASE_URL=https://api.openai.com` (requires valid key)
- Type checking: Run `rye run pyright` to validate all type hints
