# OpenAI Python Library - Complete API Reference

This document provides a comprehensive reference for the OpenAI Python library, covering all user-facing functionality with minimal token usage.

## Installation

```bash
pip install openai
```

## Quick Start

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

# Basic chat completion
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```


# OpenAI Python Library - Core Client Documentation

## Client Initialization

### OpenAI (Synchronous Client)
```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",           # Optional: defaults to OPENAI_API_KEY env var
    organization="org-id",            # Optional: defaults to OPENAI_ORG_ID env var  
    project="project-id",             # Optional: defaults to OPENAI_PROJECT_ID env var
    base_url="https://api.openai.com/v1",  # Optional: custom base URL
    timeout=60.0,                     # Optional: request timeout in seconds
    max_retries=2,                    # Optional: max retry attempts
    default_headers={"Custom": "header"},  # Optional: default headers
    http_client=None,                 # Optional: custom httpx.Client
)
```

### AsyncOpenAI (Asynchronous Client)
```python
from openai import AsyncOpenAI

async_client = AsyncOpenAI(
    api_key="your-api-key",           # Same parameters as OpenAI
    organization="org-id",
    project="project-id", 
    base_url="https://api.openai.com/v1",
    timeout=60.0,
    max_retries=2,
    default_headers={"Custom": "header"},
    http_client=None,                 # Optional: custom httpx.AsyncClient
)
```

### Azure OpenAI
```python
from openai import AzureOpenAI, AsyncAzureOpenAI

# Synchronous Azure client
azure_client = AzureOpenAI(
    api_key="your-azure-key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_version="2024-02-01"
)

# Asynchronous Azure client  
async_azure_client = AsyncAzureOpenAI(
    api_key="your-azure-key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_version="2024-02-01"
)
```

## Main Client Resources

Both `OpenAI` and `AsyncOpenAI` clients provide access to these resources:

- `client.chat` - Chat completions
- `client.completions` - Text completions  
- `client.embeddings` - Text embeddings
- `client.images` - Image generation/editing
- `client.audio` - Speech-to-text, text-to-speech
- `client.files` - File operations
- `client.models` - Model management
- `client.moderations` - Content moderation
- `client.fine_tuning` - Fine-tuning operations
- `client.vector_stores` - Vector store operations
- `client.batches` - Batch processing
- `client.beta` - Beta features (assistants, threads, etc.)

## Exception Types

```python
from openai import (
    OpenAIError,              # Base exception
    APIError,                 # API-related errors
    APIStatusError,           # HTTP status errors (4xx, 5xx)
    APIConnectionError,       # Connection errors
    APITimeoutError,          # Timeout errors
    APIResponseValidationError, # Response validation errors
    BadRequestError,          # 400 errors
    AuthenticationError,      # 401 errors
    PermissionDeniedError,    # 403 errors
    NotFoundError,            # 404 errors
    ConflictError,            # 409 errors
    UnprocessableEntityError, # 422 errors
    RateLimitError,           # 429 errors
    InternalServerError,      # 5xx errors
)
```

## Key Configuration Options

- **Environment Variables**: `OPENAI_API_KEY`, `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID`
- **Timeout**: Configure request timeouts (default: 60s)
- **Retries**: Configure retry behavior (default: 2 retries)
- **Base URL**: Override API endpoint for custom deployments
- **Headers**: Set custom default headers for all requests

## Import Paths

```python
# Main clients
from openai import OpenAI, AsyncOpenAI

# Azure clients  
from openai import AzureOpenAI, AsyncAzureOpenAI

# Exceptions
from openai import OpenAIError, APIError, RateLimitError

# Types
from openai import types

# Streaming
from openai import Stream, AsyncStream

# Utilities
from openai import file_from_path
```

## Response Wrappers

Access raw HTTP responses or streaming responses:

```python
# Raw response access
client.with_raw_response.chat.completions.create(...)

# Streaming response access  
client.with_streaming_response.chat.completions.create(...)
```


# OpenAI Python Library - Chat Completions API Documentation

## Import Path
```python
from openai import OpenAI
client = OpenAI()
```

## Main Chat Completions Interface

### Basic Usage
```python
# Access chat completions
client.chat.completions.create()
client.chat.completions.parse()  # For structured outputs
```

## Core Methods

### 1. `create()` - Standard Chat Completions
```python
def create(
    messages: Iterable[ChatCompletionMessageParam],
    model: Union[str, ChatModel],
    stream: bool = False,
    # Core parameters
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    n: Optional[int] = None,
    stop: Union[Optional[str], List[str], None] = None,
    # Tool/Function calling
    tools: Iterable[ChatCompletionToolParam] = None,
    tool_choice: ChatCompletionToolChoiceOptionParam = None,
    functions: Iterable[Function] = None,  # Deprecated
    function_call: FunctionCall = None,    # Deprecated
    # Advanced parameters
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    logit_bias: Optional[Dict[str, int]] = None,
    logprobs: Optional[bool] = None,
    top_logprobs: Optional[int] = None,
    seed: Optional[int] = None,
    user: str = None,
    # Response options
    response_format: ResponseFormat = None,
    stream_options: ChatCompletionStreamOptionsParam = None,
) -> Union[ChatCompletion, Stream[ChatCompletionChunk]]
```

**Returns:**
- `ChatCompletion` (non-streaming)
- `Stream[ChatCompletionChunk]` (streaming)

### 2. `parse()` - Structured Output Completions
```python
def parse(
    messages: Iterable[ChatCompletionMessageParam],
    model: Union[str, ChatModel],
    response_format: type[ResponseFormatT],
    # Same parameters as create()
) -> ParsedChatCompletion[ResponseFormatT]
```

**Purpose:** Automatically converts Pydantic models to JSON schema and parses responses back to structured objects.

## Key Types and Parameters

### Message Types
```python
from openai.types.chat import ChatCompletionMessageParam

# Union of message types:
# - ChatCompletionSystemMessageParam
# - ChatCompletionUserMessageParam  
# - ChatCompletionAssistantMessageParam
# - ChatCompletionToolMessageParam
# - ChatCompletionFunctionMessageParam (deprecated)
# - ChatCompletionDeveloperMessageParam
```

**Message Examples:**
```python
# System message
{"role": "system", "content": "You are a helpful assistant"}

# User message
{"role": "user", "content": "Hello!"}
{"role": "user", "content": [{"type": "text", "text": "Describe this image"}, {"type": "image_url", "image_url": {"url": "..."}}]}

# Assistant message
{"role": "assistant", "content": "Hello! How can I help?"}
{"role": "assistant", "tool_calls": [...]}

# Tool message
{"role": "tool", "tool_call_id": "call_123", "content": "Tool result"}
```

### Tool/Function Calling

#### Tool Definition
```python
from openai.types.chat import ChatCompletionToolParam

tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        },
        "strict": True  # Enable strict schema adherence
    }
}
```

#### Tool Choice Options
```python
from openai.types.chat import ChatCompletionToolChoiceOptionParam

# Options:
tool_choice = "auto"      # Let model decide
tool_choice = "none"      # Don't call tools
tool_choice = "required"  # Must call a tool
tool_choice = {"type": "function", "function": {"name": "specific_function"}}
```

### Response Types

#### Standard Response
```python
from openai.types.chat import ChatCompletion

class ChatCompletion:
    id: str
    choices: List[Choice]
    created: int
    model: str
    object: str
    usage: CompletionUsage

class Choice:
    finish_reason: Literal["stop", "length", "tool_calls", "content_filter", "function_call"]
    index: int
    message: ChatCompletionMessage
    logprobs: Optional[ChoiceLogprobs]
```

#### Streaming Response
```python
from openai.types.chat import ChatCompletionChunk

class ChatCompletionChunk:
    id: str
    choices: List[ChoiceDelta]
    created: int
    model: str
    object: str

class ChoiceDelta:
    delta: ChoiceDeltaMessage
    finish_reason: Optional[str]
    index: int
```

#### Tool Calls in Response
```python
from openai.types.chat import ChatCompletionMessageToolCall

class ChatCompletionMessageToolCall:
    id: str
    type: Literal["function"]
    function: Function

class Function:
    name: str
    arguments: str  # JSON string
```

## Usage Examples

### Basic Chat
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message.content)
```

### Streaming
```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Tool Calling
```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"]
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    tools=tools,
    tool_choice="auto"
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        # Execute function and send result back
```

### Structured Output (Pydantic)
```python
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    location: str
    temperature: float
    condition: str

response = client.chat.completions.parse(
    model="gpt-4",
    messages=[{"role": "user", "content": "Weather in NYC"}],
    response_format=WeatherResponse
)

weather = response.choices[0].message.parsed
print(f"{weather.location}: {weather.temperature}°F, {weather.condition}")
```

## Key Parameters Summary

- **messages**: Conversation history (required)
- **model**: Model ID like "gpt-4", "gpt-3.5-turbo" (required)
- **stream**: Enable streaming responses
- **tools**: Function definitions for tool calling
- **tool_choice**: Control tool usage ("auto", "none", "required", or specific tool)
- **max_tokens**: Maximum response length
- **temperature**: Randomness (0.0-2.0)
- **top_p**: Nucleus sampling
- **response_format**: Control output format (JSON, structured)
- **stream_options**: Streaming configuration
- **seed**: Deterministic outputs


# OpenAI Python Library: Audio, Embeddings, and Images API Documentation

## Audio

### Speech Synthesis
**Import:** `from openai import OpenAI; client = OpenAI(); client.audio.speech.create()`

**Method:** `create()`
- **Required Parameters:**
  - `input` (str): Text to generate audio for (max 4096 characters)
  - `model` (str): TTS model (`tts-1`, `tts-1-hd`, `gpt-4o-mini-tts`)
  - `voice` (str): Voice selection (`alloy`, `ash`, `ballad`, `coral`, `echo`, `fable`, `onyx`, `nova`, `sage`, `shimmer`, `verse`)
- **Optional Parameters:**
  - `response_format` (str): Audio format (`mp3`, `opus`, `aac`, `flac`, `wav`, `pcm`)
  - `speed` (float): Playback speed (0.25-4.0, default 1.0)
  - `instructions` (str): Voice control instructions (not for `tts-1`/`tts-1-hd`)
  - `stream_format` (str): Streaming format (`sse`, `audio`)
- **Returns:** Binary audio content

### Transcription
**Import:** `client.audio.transcriptions.create()`

**Method:** `create()`
- **Required Parameters:**
  - `file` (FileTypes): Audio file (flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, webm)
  - `model` (str): Model (`gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `whisper-1`)
- **Optional Parameters:**
  - `language` (str): Input language (ISO-639-1 format)
  - `prompt` (str): Style guide or context
  - `response_format` (str): Output format (`json`, `text`, `srt`, `verbose_json`, `vtt`)
  - `temperature` (float): Sampling temperature (0-1)
  - `timestamp_granularities` (List[str]): Timestamp detail (`word`, `segment`)
  - `stream` (bool): Enable streaming
  - `chunking_strategy`: Audio chunking options
  - `include` (List[str]): Additional info (`logprobs`)
- **Returns:** `Transcription` object with text, optional logprobs, and usage stats

### Translation
**Import:** `client.audio.translations.create()`

**Method:** `create()`
- **Required Parameters:**
  - `file` (FileTypes): Audio file to translate
  - `model` (str): Only `whisper-1` supported
- **Optional Parameters:**
  - `prompt` (str): Style guide (in English)
  - `response_format` (str): Output format (`json`, `text`, `srt`, `verbose_json`, `vtt`)
  - `temperature` (float): Sampling temperature (0-1)
- **Returns:** `Translation` object or string (based on format)

## Embeddings

**Import:** `client.embeddings.create()`

**Method:** `create()`
- **Required Parameters:**
  - `input` (str|List[str]|Iterable[int]): Text or tokens to embed
  - `model` (str): Embedding model
- **Optional Parameters:**
  - `dimensions` (int): Output dimensions (text-embedding-3+ only)
  - `encoding_format` (str): Format (`float`, `base64`)
  - `user` (str): End-user identifier
- **Returns:** `CreateEmbeddingResponse` with:
  - `data`: List of `Embedding` objects with vectors
  - `model`: Model name
  - `usage`: Token usage statistics

## Images

### Generation
**Import:** `client.images.generate()`

**Method:** `generate()`
- **Required Parameters:**
  - `prompt` (str): Image description
- **Optional Parameters:**
  - `model` (str): Model (`dall-e-2`, `dall-e-3`, `gpt-image-1`)
  - `n` (int): Number of images (1-10)
  - `size` (str): Image size (`256x256`, `512x512`, `1024x1024`, `1536x1024`, `1024x1536`)
  - `quality` (str): Quality (`standard`, `hd`, `low`, `medium`, `high`, `auto`)
  - `response_format` (str): Format (`url`, `b64_json`)
  - `style` (str): Style (`vivid`, `natural`)
  - `background` (str): Background (`transparent`, `opaque`, `auto`)
  - `output_format` (str): File format (`png`, `jpeg`, `webp`)
  - `output_compression` (int): Compression level (0-100%)
- **Returns:** `ImagesResponse` with generated images

### Editing
**Import:** `client.images.edit()`

**Method:** `edit()`
- **Required Parameters:**
  - `image` (FileTypes|List[FileTypes]): Source image(s)
  - `prompt` (str): Edit description
- **Optional Parameters:**
  - `mask` (FileTypes): Transparency mask for editing areas
  - `model` (str): Model (`dall-e-2`, `gpt-image-1`)
  - `n` (int): Number of variations
  - `size`, `quality`, `response_format`, `background`, `output_format`, `output_compression`: Same as generation
- **Returns:** `ImagesResponse` with edited images

### Variations
**Import:** `client.images.create_variation()`

**Method:** `create_variation()`
- **Required Parameters:**
  - `image` (FileTypes): Source image (PNG, <4MB, square)
- **Optional Parameters:**
  - `model` (str): Only `dall-e-2` supported
  - `n` (int): Number of variations (1-10)
  - `response_format` (str): Format (`url`, `b64_json`)
  - `size` (str): Size (`256x256`, `512x512`, `1024x1024`)
- **Returns:** `ImagesResponse` with image variations

## Common Response Types

- **Audio**: Binary content or structured objects with text/usage
- **Embeddings**: Vector arrays with usage statistics
- **Images**: URLs or base64-encoded images with metadata

All methods support async variants via `AsyncOpenAI` client.


# OpenAI Python Library - File Management, Fine-tuning, and Batch Processing

## File Operations (`openai.resources.files`)

### Import
```python
from openai import OpenAI
client = OpenAI()
```

### Methods

#### `client.files.create(file, purpose)`
Upload a file for use across various endpoints.
- **Parameters:**
  - `file`: FileTypes - The file object to upload (max 512MB per file)
  - `purpose`: FilePurpose - One of: `"assistants"`, `"batch"`, `"fine-tune"`, `"vision"`, `"user_data"`, `"evals"`
- **Returns:** `FileObject` with `id`, `filename`, `bytes`, `created_at`, `purpose`, `status`

#### `client.files.retrieve(file_id)`
Get information about a specific file.
- **Parameters:** `file_id`: str
- **Returns:** `FileObject`

#### `client.files.list(after=None, limit=None, order=None, purpose=None)`
List organization's files with pagination.
- **Parameters:**
  - `after`: str - Cursor for pagination
  - `limit`: int - Max 10,000 objects (default: 10,000)
  - `order`: "asc" | "desc" - Sort by created_at
  - `purpose`: str - Filter by purpose
- **Returns:** `SyncCursorPage[FileObject]`

#### `client.files.delete(file_id)`
Delete a file.
- **Parameters:** `file_id`: str
- **Returns:** `FileDeleted` with `id`, `deleted`, `object`

#### `client.files.content(file_id)`
Retrieve file content.
- **Parameters:** `file_id`: str
- **Returns:** `StreamedBinaryAPIResponse`

---

## Batch Processing (`openai.resources.batches`)

### Import
```python
client.batches  # Access via client
```

### Methods

#### `client.batches.create(completion_window, endpoint, input_file_id, metadata=None)`
Create and execute a batch from uploaded file.
- **Parameters:**
  - `completion_window`: "24h" - Processing time frame
  - `endpoint`: "/v1/responses" | "/v1/chat/completions" | "/v1/embeddings" | "/v1/completions"
  - `input_file_id`: str - ID of uploaded JSONL file (max 200MB, 50,000 requests)
  - `metadata`: Optional[dict] - 16 key-value pairs max
- **Returns:** `Batch` with `id`, `status`, `created_at`, `endpoint`, `input_file_id`

#### `client.batches.retrieve(batch_id)`
Get batch information.
- **Parameters:** `batch_id`: str
- **Returns:** `Batch`

#### `client.batches.list(after=None, limit=None)`
List organization's batches.
- **Parameters:**
  - `after`: str - Pagination cursor
  - `limit`: int - 1-100 objects (default: 20)
- **Returns:** `SyncCursorPage[Batch]`

#### `client.batches.cancel(batch_id)`
Cancel an in-progress batch.
- **Parameters:** `batch_id`: str
- **Returns:** `Batch` with status "cancelling" → "cancelled"

### Batch Status Values
- `"validating"`, `"failed"`, `"in_progress"`, `"finalizing"`, `"completed"`, `"expired"`, `"cancelling"`, `"cancelled"`

---

## Fine-tuning (`openai.resources.fine_tuning.jobs`)

### Import
```python
client.fine_tuning.jobs  # Access via client
```

### Methods

#### `client.fine_tuning.jobs.create(model, training_file, **kwargs)`
Create a fine-tuning job.
- **Parameters:**
  - `model`: "babbage-002" | "davinci-002" | "gpt-3.5-turbo" | "gpt-4o-mini" | str
  - `training_file`: str - ID of uploaded JSONL training file
  - `hyperparameters`: Optional - `batch_size`, `learning_rate_multiplier`, `n_epochs`
  - `validation_file`: Optional[str] - Validation data file ID
  - `suffix`: Optional[str] - Model name suffix (max 18 chars)
  - `metadata`: Optional[dict] - Key-value pairs
- **Returns:** `FineTuningJob` with `id`, `model`, `status`, `created_at`

#### `client.fine_tuning.jobs.retrieve(fine_tuning_job_id)`
Get fine-tuning job details.
- **Parameters:** `fine_tuning_job_id`: str
- **Returns:** `FineTuningJob`

#### `client.fine_tuning.jobs.list(after=None, limit=None)`
List fine-tuning jobs.
- **Parameters:**
  - `after`: str - Pagination cursor
  - `limit`: int - Max objects to return
- **Returns:** `SyncCursorPage[FineTuningJob]`

#### `client.fine_tuning.jobs.cancel(fine_tuning_job_id)`
Cancel a fine-tuning job.
- **Parameters:** `fine_tuning_job_id`: str
- **Returns:** `FineTuningJob`

#### `client.fine_tuning.jobs.list_events(fine_tuning_job_id, after=None, limit=None)`
List events for a fine-tuning job.
- **Parameters:**
  - `fine_tuning_job_id`: str
  - `after`: str - Pagination cursor
  - `limit`: int - Max events to return
- **Returns:** `SyncCursorPage[FineTuningJobEvent]`

---

## Upload Management (`openai.resources.uploads`)

### Import
```python
client.uploads  # Access via client
```

### Methods

#### `client.uploads.upload_file_chunked(file, mime_type, purpose, **kwargs)`
Upload large files in 64MB chunks.
- **Parameters:**
  - `file`: Path | bytes - File path or bytes data
  - `mime_type`: str - MIME type of file
  - `purpose`: FilePurpose - File purpose
  - `filename`: str - Required for bytes input
  - `bytes`: int - File size (required for bytes input)
  - `part_size`: int - Chunk size (default: 64MB)
- **Returns:** `Upload` object

#### `client.uploads.create(bytes, filename, mime_type, purpose)`
Create upload session for large files.
- **Parameters:**
  - `bytes`: int - Total file size
  - `filename`: str - File name
  - `mime_type`: str - MIME type
  - `purpose`: FilePurpose - File purpose
- **Returns:** `Upload` with `id`, `expires_at`, `created_at`

#### `client.uploads.cancel(upload_id)`
Cancel an upload session.
- **Parameters:** `upload_id`: str
- **Returns:** `Upload`

#### `client.uploads.complete(upload_id, part_ids, md5=None)`
Complete upload after all parts uploaded.
- **Parameters:**
  - `upload_id`: str
  - `part_ids`: List[str] - IDs of uploaded parts
  - `md5`: Optional[str] - MD5 hash for verification
- **Returns:** `Upload`

### Upload Parts (`client.uploads.parts`)

#### `client.uploads.parts.create(upload_id, data)`
Upload a single part.
- **Parameters:**
  - `upload_id`: str
  - `data`: bytes - Part data
- **Returns:** `UploadPart` with `id`, `created_at`, `upload_id`

---

## Key Response Types

### FileObject
```python
{
    "id": str,
    "bytes": int,
    "created_at": int,
    "filename": str,
    "purpose": str,
    "status": "uploaded" | "processed" | "error"
}
```

### Batch
```python
{
    "id": str,
    "status": str,
    "created_at": int,
    "endpoint": str,
    "input_file_id": str,
    "completion_window": str
}
```

### FineTuningJob
```python
{
    "id": str,
    "model": str,
    "status": str,
    "created_at": int,
    "training_file": str,
    "hyperparameters": dict
}
```

### Upload
```python
{
    "id": str,
    "bytes": int,
    "created_at": int,
    "expires_at": int,
    "filename": str,
    "object": "upload"
}
```


# OpenAI Python Library - Beta Features Documentation

⚠️ **BETA FEATURES**: These APIs are in beta and may change. The Assistants API is deprecated in favor of the Responses API.

## Import Path
```python
from openai import OpenAI
client = OpenAI()

# Access beta features
client.beta.assistants
client.beta.threads
client.beta.realtime
```

## 1. Assistants API

### Import
```python
from openai.resources.beta.assistants import Assistants
```

### Key Methods

#### Create Assistant
```python
assistant = client.beta.assistants.create(
    model="gpt-4o",  # Required
    name="My Assistant",
    description="Assistant description",
    instructions="System instructions for the assistant",
    tools=[{"type": "code_interpreter"}, {"type": "file_search"}],
    tool_resources={
        "code_interpreter": {"file_ids": ["file-123"]},
        "file_search": {"vector_store_ids": ["vs-123"]}
    },
    temperature=0.7,
    top_p=1.0,
    response_format={"type": "json_object"},
    reasoning_effort="medium",  # For o-series models
    metadata={"key": "value"}
)
```

#### Other Assistant Methods
```python
# Retrieve assistant
assistant = client.beta.assistants.retrieve("asst_123")

# Update assistant
assistant = client.beta.assistants.update("asst_123", name="Updated Name")

# List assistants
assistants = client.beta.assistants.list(limit=20, order="desc")

# Delete assistant
deleted = client.beta.assistants.delete("asst_123")
```

## 2. Threads API

### Import
```python
from openai.resources.beta.threads import Threads
```

### Key Methods

#### Create Thread
```python
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "Hello, how can you help me?",
            "attachments": [{"file_id": "file-123", "tools": [{"type": "file_search"}]}]
        }
    ],
    tool_resources={
        "code_interpreter": {"file_ids": ["file-123"]},
        "file_search": {"vector_store_ids": ["vs-123"]}
    },
    metadata={"key": "value"}
)
```

#### Thread Management
```python
# Retrieve thread
thread = client.beta.threads.retrieve("thread_123")

# Update thread
thread = client.beta.threads.update("thread_123", metadata={"updated": "true"})

# Delete thread
deleted = client.beta.threads.delete("thread_123")

# Create and run (convenience method)
run = client.beta.threads.create_and_run(
    assistant_id="asst_123",
    thread={"messages": [{"role": "user", "content": "Hello"}]},
    stream=False
)
```

## 3. Messages API

### Import
```python
from openai.resources.beta.threads.messages import Messages
```

### Key Methods

#### Create Message
```python
message = client.beta.threads.messages.create(
    thread_id="thread_123",
    role="user",  # "user" or "assistant"
    content="Your message content",
    attachments=[
        {
            "file_id": "file-123",
            "tools": [{"type": "file_search"}]
        }
    ],
    metadata={"key": "value"}
)
```

#### Message Management
```python
# List messages
messages = client.beta.threads.messages.list(
    thread_id="thread_123",
    limit=20,
    order="desc",
    run_id="run_123"  # Filter by run
)

# Retrieve message
message = client.beta.threads.messages.retrieve(
    thread_id="thread_123",
    message_id="msg_123"
)

# Update message
message = client.beta.threads.messages.update(
    thread_id="thread_123",
    message_id="msg_123",
    metadata={"updated": "true"}
)

# Delete message
deleted = client.beta.threads.messages.delete(
    thread_id="thread_123",
    message_id="msg_123"
)
```

## 4. Runs API

### Import
```python
from openai.resources.beta.threads.runs import Runs
```

### Key Methods

#### Create Run
```python
run = client.beta.threads.runs.create(
    thread_id="thread_123",
    assistant_id="asst_123",
    model="gpt-4o",  # Override assistant model
    instructions="Additional instructions",
    additional_instructions="Appended instructions",
    additional_messages=[{"role": "user", "content": "Extra context"}],
    tools=[{"type": "code_interpreter"}],
    tool_choice="auto",  # "none", "auto", "required", or specific tool
    parallel_tool_calls=True,
    response_format={"type": "json_object"},
    temperature=0.7,
    top_p=1.0,
    max_completion_tokens=1000,
    max_prompt_tokens=1000,
    reasoning_effort="medium",
    truncation_strategy={"type": "last_messages", "last_messages": 10},
    stream=False,
    metadata={"key": "value"}
)
```

#### Run Management
```python
# List runs
runs = client.beta.threads.runs.list(
    thread_id="thread_123",
    limit=20,
    order="desc"
)

# Retrieve run
run = client.beta.threads.runs.retrieve(
    thread_id="thread_123",
    run_id="run_123"
)

# Update run
run = client.beta.threads.runs.update(
    thread_id="thread_123",
    run_id="run_123",
    metadata={"updated": "true"}
)

# Cancel run
run = client.beta.threads.runs.cancel(
    thread_id="thread_123",
    run_id="run_123"
)

# Submit tool outputs
run = client.beta.threads.runs.submit_tool_outputs(
    thread_id="thread_123",
    run_id="run_123",
    tool_outputs=[
        {
            "tool_call_id": "call_123",
            "output": "Tool output result"
        }
    ]
)
```

#### Streaming and Polling
```python
# Create and stream
stream = client.beta.threads.runs.create_and_stream(
    thread_id="thread_123",
    assistant_id="asst_123"
)

# Create and poll (wait for completion)
run = client.beta.threads.runs.create_and_poll(
    thread_id="thread_123",
    assistant_id="asst_123"
)
```

## 5. Realtime API

### Import
```python
from openai.resources.beta.realtime import Realtime
```

### Key Methods

#### Connect to Realtime API
```python
# Establish WebSocket connection
connection = client.beta.realtime.connect(
    model="gpt-4o-realtime-preview",
    extra_headers={"Custom-Header": "value"},
    extra_query={"param": "value"},
    websocket_connection_options={
        "timeout": 30,
        "max_size": 1024*1024
    }
)

# Use connection manager
with connection as conn:
    # Send events
    conn.session.update({"voice": "alloy"})
    conn.response.create({"type": "response.create"})
    
    # Handle events
    for event in conn:
        if event.type == "response.audio.delta":
            # Handle audio data
            audio_data = event.delta
        elif event.type == "response.text.delta":
            # Handle text data
            text_data = event.delta
```

#### Sessions Management
```python
# Create session
session = client.beta.realtime.sessions.create(
    model="gpt-4o-realtime-preview",
    voice="alloy"
)

# Update session
session = client.beta.realtime.sessions.update(
    session_id="sess_123",
    voice="echo"
)
```

## Key Response Types

### Assistant
```python
class Assistant:
    id: str
    object: str = "assistant"
    created_at: int
    name: Optional[str]
    description: Optional[str]
    model: str
    instructions: Optional[str]
    tools: List[AssistantTool]
    tool_resources: Optional[ToolResources]
    metadata: Optional[Metadata]
    temperature: Optional[float]
    top_p: Optional[float]
    response_format: Optional[AssistantResponseFormatOption]
```

### Thread
```python
class Thread:
    id: str
    object: str = "thread"
    created_at: int
    tool_resources: Optional[ToolResources]
    metadata: Optional[Metadata]
```

### Message
```python
class Message:
    id: str
    object: str = "thread.message"
    created_at: int
    thread_id: str
    role: Literal["user", "assistant"]
    content: List[MessageContent]
    attachments: Optional[List[Attachment]]
    metadata: Optional[Metadata]
```

### Run
```python
class Run:
    id: str
    object: str = "thread.run"
    created_at: int
    thread_id: str
    assistant_id: str
    status: Literal["queued", "in_progress", "requires_action", "cancelling", "cancelled", "failed", "completed", "expired"]
    model: str
    instructions: str
    tools: List[AssistantTool]
    metadata: Optional[Metadata]
```

## Common Parameters

- **model**: Model ID (e.g., "gpt-4o", "gpt-4o-mini")
- **temperature**: 0.0-2.0, controls randomness
- **top_p**: 0.0-1.0, nucleus sampling
- **tools**: List of tools: `code_interpreter`, `file_search`, `function`
- **metadata**: Up to 16 key-value pairs (64 char keys, 512 char values)
- **stream**: Boolean for streaming responses
- **reasoning_effort**: "low", "medium", "high" (o-series models only)

## Error Handling

All beta methods can raise `OpenAIError` exceptions. Use try-catch blocks for error handling:

```python
try:
    assistant = client.beta.assistants.create(model="gpt-4o")
except OpenAIError as e:
    print(f"Error: {e}")
```


# OpenAI Python Library - Additional Functionality Documentation

## Models Management

### Import Path
```python
from openai import OpenAI
client = OpenAI()
```

### Methods

#### `client.models.list()`
Lists all available models with basic information.
- **Returns**: `SyncPage[Model]` - Paginated list of models
- **Response Fields**: `id`, `created`, `object`, `owned_by`

#### `client.models.retrieve(model: str)`
Retrieves specific model information.
- **Parameters**: `model` (str) - Model ID
- **Returns**: `Model` object with model details

#### `client.models.delete(model: str)`
Deletes a fine-tuned model (requires Owner role).
- **Parameters**: `model` (str) - Model ID to delete
- **Returns**: `ModelDeleted` object

---

## Content Moderation

### Import Path
```python
from openai import OpenAI
client = OpenAI()
```

### Methods

#### `client.moderations.create()`
Classifies text/image inputs for harmful content.
- **Parameters**:
  - `input` (str | List[str] | Iterable[ModerationMultiModalInputParam]) - Content to moderate
  - `model` (str | ModerationModel, optional) - Moderation model to use
- **Returns**: `ModerationCreateResponse` with classification results
- **Supports**: Text strings, arrays of strings, or multi-modal input objects

---

## Vector Stores

### Import Path
```python
from openai import OpenAI
client = OpenAI()
```

### Methods

#### `client.vector_stores.create()`
Creates a new vector store for file search.
- **Parameters**:
  - `name` (str, optional) - Vector store name
  - `file_ids` (List[str], optional) - File IDs to include
  - `chunking_strategy` (FileChunkingStrategyParam, optional) - Chunking strategy
  - `expires_after` (ExpiresAfter, optional) - Expiration policy
  - `metadata` (Metadata, optional) - Key-value pairs (max 16)
- **Returns**: `VectorStore` object

#### `client.vector_stores.retrieve(vector_store_id: str)`
Retrieves vector store details.
- **Parameters**: `vector_store_id` (str) - Vector store ID
- **Returns**: `VectorStore` object

#### `client.vector_stores.update(vector_store_id: str)`
Updates vector store properties.
- **Parameters**:
  - `vector_store_id` (str) - Vector store ID
  - `name` (str, optional) - New name
  - `expires_after` (ExpiresAfter, optional) - New expiration
  - `metadata` (Metadata, optional) - Updated metadata
- **Returns**: `VectorStore` object

#### `client.vector_stores.list()`
Lists vector stores with pagination.
- **Parameters**: `after`, `before`, `limit`, `order` for pagination
- **Returns**: `SyncCursorPage[VectorStore]`

#### `client.vector_stores.delete(vector_store_id: str)`
Deletes a vector store.
- **Parameters**: `vector_store_id` (str) - Vector store ID
- **Returns**: `VectorStoreDeleted` object

#### `client.vector_stores.search(vector_store_id: str)`
Searches within a vector store.
- **Parameters**:
  - `vector_store_id` (str) - Vector store ID
  - `query` (str) - Search query
  - `limit` (int, optional) - Max results
- **Returns**: `VectorStoreSearchResponse`

### Sub-resources
- `client.vector_stores.files` - Manage files in vector stores
- `client.vector_stores.file_batches` - Batch file operations

---

## Response Handling

### Import Path
```python
from openai import OpenAI
client = OpenAI()
```

### Methods

#### `client.responses.create()`
Creates model responses with advanced configuration.
- **Parameters**:
  - `input` (str | ResponseInputParam, optional) - Text/image/file inputs
  - `model` (ResponsesModel, optional) - Model to use
  - `instructions` (str, optional) - System message
  - `max_output_tokens` (int, optional) - Token limit
  - `temperature` (float, optional) - Sampling temperature
  - `tools` (Iterable[ToolParam], optional) - Available tools
  - `stream` (bool, optional) - Enable streaming
  - `background` (bool, optional) - Background processing
  - `previous_response_id` (str, optional) - For multi-turn conversations
- **Returns**: `Response` object or `Stream[ResponseStreamEvent]` if streaming

#### `client.responses.retrieve(response_id: str)`
Retrieves a specific response.
- **Parameters**: `response_id` (str) - Response ID
- **Returns**: `Response` object

### Sub-resources
- `client.responses.input_items` - Manage response input items

---

## Evaluation Tools

### Import Path
```python
from openai import OpenAI
client = OpenAI()
```

### Methods

#### `client.evals.create()`
Creates evaluation structure for model testing.
- **Parameters**:
  - `data_source_config` (DataSourceConfig) - Data source configuration
  - `testing_criteria` (Iterable[TestingCriterion]) - Grading criteria
  - `name` (str, optional) - Evaluation name
  - `metadata` (Metadata, optional) - Additional metadata
- **Returns**: `EvalCreateResponse`

#### `client.evals.retrieve(eval_id: str)`
Gets evaluation by ID.
- **Parameters**: `eval_id` (str) - Evaluation ID
- **Returns**: `EvalRetrieveResponse`

#### `client.evals.update(eval_id: str)`
Updates evaluation properties.
- **Parameters**:
  - `eval_id` (str) - Evaluation ID
  - `name` (str, optional) - New name
  - `metadata` (Metadata, optional) - Updated metadata
- **Returns**: `EvalUpdateResponse`

#### `client.evals.list()`
Lists evaluations with pagination.
- **Parameters**: `after`, `limit`, `order`, `order_by` for pagination/sorting
- **Returns**: `SyncCursorPage[EvalListResponse]`

#### `client.evals.delete(eval_id: str)`
Deletes an evaluation.
- **Parameters**: `eval_id` (str) - Evaluation ID
- **Returns**: `EvalDeleteResponse`

### Sub-resources
- `client.evals.runs` - Manage evaluation runs

---

## Container Management

### Import Path
```python
from openai import OpenAI
client = OpenAI()
```

### Methods

#### `client.containers.create()`
Creates a new container.
- **Parameters**:
  - `name` (str) - Container name
  - `file_ids` (List[str], optional) - Files to copy to container
  - `expires_after` (ExpiresAfter, optional) - Expiration time
- **Returns**: `ContainerCreateResponse`

#### `client.containers.retrieve(container_id: str)`
Retrieves container details.
- **Parameters**: `container_id` (str) - Container ID
- **Returns**: `ContainerRetrieveResponse`

#### `client.containers.list()`
Lists containers with pagination.
- **Parameters**: `after`, `limit`, `order` for pagination
- **Returns**: `SyncCursorPage[ContainerListResponse]`

#### `client.containers.delete(container_id: str)`
Deletes a container.
- **Parameters**: `container_id` (str) - Container ID
- **Returns**: None

### Sub-resources
- `client.containers.files` - Manage files within containers

---

## Common Parameters

### Pagination
Most list methods support:
- `after` (str) - Cursor for pagination
- `limit` (int) - Number of items to return
- `order` ("asc" | "desc") - Sort order

### Metadata
Key-value pairs for object annotation:
- Max 16 pairs per object
- Keys: max 64 characters
- Values: max 512 characters

### Async Support
All methods have async equivalents:
```python
from openai import AsyncOpenAI
client = AsyncOpenAI()
await client.models.list()
```

---

## Complete Example Usage

```python
from openai import OpenAI

# Initialize client
client = OpenAI(api_key="your-api-key")

# Chat completion
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Generate embeddings
embeddings = client.embeddings.create(
    model="text-embedding-3-small",
    input="Text to embed"
)

# Generate image
image = client.images.generate(
    model="dall-e-3",
    prompt="A beautiful sunset",
    size="1024x1024"
)

# Upload and manage files
file = client.files.create(
    file=open("data.jsonl", "rb"),
    purpose="fine-tune"
)

# Create fine-tuning job
job = client.fine_tuning.jobs.create(
    model="gpt-3.5-turbo",
    training_file=file.id
)

# Content moderation
moderation = client.moderations.create(
    input="Text to moderate"
)

print("OpenAI Python library setup complete!")
```

---

## Error Handling Best Practices

```python
from openai import OpenAIError, RateLimitError, APITimeoutError

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
except RateLimitError:
    print("Rate limit exceeded. Please wait.")
except APITimeoutError:
    print("Request timed out. Please try again.")
except OpenAIError as e:
    print(f"OpenAI API error: {e}")
```

This completes the comprehensive OpenAI Python library API reference. All user-facing functionality is documented with minimal token usage while maintaining clarity and completeness.

