# Structured Outputs Parsing Helpers

The OpenAI API supports extracting JSON from the model with the `response_format` request param, for more details on the API, see [this guide](https://platform.openai.com/docs/guides/structured-outputs).

The SDK provides a `client.beta.chat.completions.parse()` method which is a wrapper over the `client.chat.completions.create()` that
provides richer integrations with Python specific types & returns a `ParsedChatCompletion` object, which is a subclass of the standard `ChatCompletion` class.

## Auto-parsing response content with Pydantic models

You can pass a pydantic model to the `.parse()` method and the SDK will automatically convert the model
into a JSON schema, send it to the API and parse the response content back into the given model.

```py
from typing import List
from pydantic import BaseModel
from openai import OpenAI

class Step(BaseModel):
    explanation: str
    output: str

class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str

client = OpenAI()
completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "solve 8x + 31 = 2"},
    ],
    response_format=MathResponse,
)

message = completion.choices[0].message
if message.parsed:
    print(message.parsed.steps)
    print("answer: ", message.parsed.final_answer)
else:
    print(message.refusal)
```

## Auto-parsing function tool calls

The `.parse()` method will also automatically parse `function` tool calls if:
- You use the `openai.pydantic_function_tool()` helper method
- You mark your tool schema with `"strict": True`

For example:

```py
from enum import Enum
from typing import List, Union
from pydantic import BaseModel
import openai

class Table(str, Enum):
    orders = "orders"
    customers = "customers"
    products = "products"

class Column(str, Enum):
    id = "id"
    status = "status"
    expected_delivery_date = "expected_delivery_date"
    delivered_at = "delivered_at"
    shipped_at = "shipped_at"
    ordered_at = "ordered_at"
    canceled_at = "canceled_at"

class Operator(str, Enum):
    eq = "="
    gt = ">"
    lt = "<"
    le = "<="
    ge = ">="
    ne = "!="

class OrderBy(str, Enum):
    asc = "asc"
    desc = "desc"

class DynamicValue(BaseModel):
    column_name: str

class Condition(BaseModel):
    column: str
    operator: Operator
    value: Union[str, int, DynamicValue]

class Query(BaseModel):
    table_name: Table
    columns: List[Column]
    conditions: List[Condition]
    order_by: OrderBy

client = openai.OpenAI()
completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant. The current date is August 6, 2024. You help users query for the data they are looking for by calling the query function.",
        },
        {
            "role": "user",
            "content": "look up all my orders in may of last year that were fulfilled but not delivered on time",
        },
    ],
    tools=[
        openai.pydantic_function_tool(Query),
    ],
)

tool_call = (completion.choices[0].message.tool_calls or [])[0]
print(tool_call.function)
assert isinstance(tool_call.function.parsed_arguments, Query)
print(tool_call.function.parsed_arguments.table_name)
```

### Differences from `.create()`

The `beta.chat.completions.parse()` method imposes some additional restrictions on it's usage that `chat.completions.create()` does not. 

- If the completion completes with `finish_reason` set to `length` or `content_filter`, the `LengthFinishReasonError` / `ContentFilterFinishReasonError` errors will be raised.
- Only strict function tools can be passed, e.g. `{'type': 'function', 'function': {..., 'strict': True}}`

# Streaming Helpers

OpenAI supports streaming responses when interacting with the [Chat Completion] & [Assistant](#assistant-streaming-api) APIs.

## Chat Completions API

The SDK provides a `.beta.chat.completions.stream()` method that wraps the `.chat.completions.create(stream=True)` stream providing a more granular event API & automatic accumulation of each delta.

It also supports all aforementioned [parsing helpers](#parsing-helpers).

Unlike `.create(stream=True)`, the `.stream()` method requires usage within a context manager to prevent accidental leakage of the response:

```py
from openai import AsyncOpenAI

client = AsyncOpenAI()

async with client.beta.chat.completions.stream(
    model='gpt-4o-2024-08-06',
    messages=[...],
) as stream:
    async for event in stream:
        if event.type == 'content.delta':
            print(event.content, flush=True, end='')
```

When the context manager is entered, a `ChatCompletionStream` / `AsyncChatCompletionStream` instance is returned which, like `.create(stream=True)` is an iterator in the sync client and an async iterator in the async client. The full list of events that are yielded by the iterator are outlined [below](#chat-completions-events).

When the context manager exits, the response will be closed, however the `stream` instance is still available outside
the context manager.

### Chat Completions Events

These events allow you to track the progress of the chat completion generation, access partial results, and handle different aspects of the stream separately.

Below is a list of the different event types you may encounter:

#### ChunkEvent

Emitted for every chunk received from the API.

- `type`: `"chunk"`
- `chunk`: The raw `ChatCompletionChunk` object received from the API
- `snapshot`: The current accumulated state of the chat completion

#### ContentDeltaEvent

Emitted for every chunk containing new content.

- `type`: `"content.delta"`
- `delta`: The new content string received in this chunk
- `snapshot`: The accumulated content so far
- `parsed`: The partially parsed content (if applicable)

#### ContentDoneEvent

Emitted when the content generation is complete. May be fired multiple times if there are multiple choices.

- `type`: `"content.done"`
- `content`: The full generated content
- `parsed`: The fully parsed content (if applicable)

#### RefusalDeltaEvent

Emitted when a chunk contains part of a content refusal.

- `type`: `"refusal.delta"`
- `delta`: The new refusal content string received in this chunk
- `snapshot`: The accumulated refusal content string so far

#### RefusalDoneEvent

Emitted when the refusal content is complete.

- `type`: `"refusal.done"`
- `refusal`: The full refusal content

#### FunctionToolCallArgumentsDeltaEvent

Emitted when a chunk contains part of a function tool call's arguments.

- `type`: `"tool_calls.function.arguments.delta"`
- `name`: The name of the function being called
- `index`: The index of the tool call
- `arguments`: The accumulated raw JSON string of arguments
- `parsed_arguments`: The partially parsed arguments object
- `arguments_delta`: The new JSON string fragment received in this chunk

#### FunctionToolCallArgumentsDoneEvent

Emitted when a function tool call's arguments are complete.

- `type`: `"tool_calls.function.arguments.done"`
- `name`: The name of the function being called
- `index`: The index of the tool call
- `arguments`: The full raw JSON string of arguments
- `parsed_arguments`: The fully parsed arguments object. If you used `openai.pydantic_function_tool()` this will be an instance of the given model.

#### LogprobsContentDeltaEvent

Emitted when a chunk contains new content [log probabilities](https://cookbook.openai.com/examples/using_logprobs).

- `type`: `"logprobs.content.delta"`
- `content`: A list of the new log probabilities received in this chunk
- `snapshot`: A list of the accumulated log probabilities so far

#### LogprobsContentDoneEvent

Emitted when all content [log probabilities](https://cookbook.openai.com/examples/using_logprobs) have been received.

- `type`: `"logprobs.content.done"`
- `content`: The full list of token log probabilities for the content

#### LogprobsRefusalDeltaEvent

Emitted when a chunk contains new refusal [log probabilities](https://cookbook.openai.com/examples/using_logprobs).

- `type`: `"logprobs.refusal.delta"`
- `refusal`: A list of the new log probabilities received in this chunk
- `snapshot`: A list of the accumulated log probabilities so far

#### LogprobsRefusalDoneEvent

Emitted when all refusal [log probabilities](https://cookbook.openai.com/examples/using_logprobs) have been received.

- `type`: `"logprobs.refusal.done"`
- `refusal`: The full list of token log probabilities for the refusal

### Chat Completions stream methods

A handful of helper methods are provided on the stream class for additional convenience,

**`.get_final_completion()`**

Returns the accumulated `ParsedChatCompletion` object

```py
async with client.beta.chat.completions.stream(...) as stream:
    ...

completion = await stream.get_final_completion()
print(completion.choices[0].message)
```

**`.until_done()`**

If you want to wait for the stream to complete, you can use the `.until_done()` method.

```py
async with client.beta.chat.completions.stream(...) as stream:
    await stream.until_done()
    # stream is now finished
```

## Assistant Streaming API

OpenAI supports streaming responses from Assistants. The SDK provides convenience wrappers around the API
so you can subscribe to the types of events you are interested in as well as receive accumulated responses.

More information can be found in the documentation: [Assistant Streaming](https://platform.openai.com/docs/assistants/overview?lang=python)

#### An example of creating a run and subscribing to some events

You can subscribe to events by creating an event handler class and overloading the relevant event handlers.

```python
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import ToolCall, ToolCallDelta

client = openai.OpenAI()

# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.

class EventHandler(AssistantEventHandler):
  @override
  def on_text_created(self, text: Text) -> None:
    print(f"\nassistant > ", end="", flush=True)

  @override
  def on_text_delta(self, delta: TextDelta, snapshot: Text):
    print(delta.value, end="", flush=True)

  @override
  def on_tool_call_created(self, tool_call: ToolCall):
    print(f"\nassistant > {tool_call.type}\n", flush=True)

  @override
  def on_tool_call_delta(self, delta: ToolCallDelta, snapshot: ToolCall):
    if delta.type == "code_interpreter" and delta.code_interpreter:
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)

# Then, we use the `stream` SDK helper
# with the `EventHandler` class to create the Run
# and stream the response.

with client.beta.threads.runs.stream(
  thread_id="thread_id",
  assistant_id="assistant_id",
  event_handler=EventHandler(),
) as stream:
  stream.until_done()
```

#### An example of iterating over events

You can also iterate over all the streamed events.

```python
with client.beta.threads.runs.stream(
  thread_id=thread.id,
  assistant_id=assistant.id
) as stream:
    for event in stream:
        # Print the text from text delta events
        if event.event == "thread.message.delta" and event.data.delta.content:
            print(event.data.delta.content[0].text)
```

#### An example of iterating over text

You can also iterate over just the text deltas received

```python
with client.beta.threads.runs.stream(
  thread_id=thread.id,
  assistant_id=assistant.id
) as stream:
    for text in stream.text_deltas:
        print(text)
```

### Creating Streams

There are three helper methods for creating streams:

```python
client.beta.threads.runs.stream()
```

This method can be used to start and stream the response to an existing run with an associated thread
that is already populated with messages.

```python
client.beta.threads.create_and_run_stream()
```

This method can be used to add a message to a thread, start a run and then stream the response.

```python
client.beta.threads.runs.submit_tool_outputs_stream()
```

This method can be used to submit a tool output to a run waiting on the output and start a stream.

### Assistant Events

The assistant API provides events you can subscribe to for the following events.

```python
def on_event(self, event: AssistantStreamEvent)
```

This allows you to subscribe to all the possible raw events sent by the OpenAI streaming API.
In many cases it will be more convenient to subscribe to a more specific set of events for your use case.

More information on the types of events can be found here: [Events](https://platform.openai.com/docs/api-reference/assistants-streaming/events)

```python
def on_run_step_created(self, run_step: RunStep)
def on_run_step_delta(self, delta: RunStepDelta, snapshot: RunStep)
def on_run_step_done(self, run_step: RunStep)
```

These events allow you to subscribe to the creation, delta and completion of a RunStep.

For more information on how Runs and RunSteps work see the documentation [Runs and RunSteps](https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps)

```python
def on_message_created(self, message: Message)
def on_message_delta(self, delta: MessageDelta, snapshot: Message)
def on_message_done(self, message: Message)
```

This allows you to subscribe to Message creation, delta and completion events. Messages can contain
different types of content that can be sent from a model (and events are available for specific content types).
For convenience, the delta event includes both the incremental update and an accumulated snapshot of the content.

More information on messages can be found
on in the documentation page [Message](https://platform.openai.com/docs/api-reference/messages/object).

```python
def on_text_created(self, text: Text)
def on_text_delta(self, delta: TextDelta, snapshot: Text)
def on_text_done(self, text: Text)
```

These events allow you to subscribe to the creation, delta and completion of a Text content (a specific type of message).
For convenience, the delta event includes both the incremental update and an accumulated snapshot of the content.

```python
def on_image_file_done(self, image_file: ImageFile)
```

Image files are not sent incrementally so an event is provided for when a image file is available.

```python
def on_tool_call_created(self, tool_call: ToolCall)
def on_tool_call_delta(self, delta: ToolCallDelta, snapshot: ToolCall)
def on_tool_call_done(self, tool_call: ToolCall)
```

These events allow you to subscribe to events for the creation, delta and completion of a ToolCall.

More information on tools can be found here [Tools](https://platform.openai.com/docs/assistants/tools)

```python
def on_end(self)
```

The last event send when a stream ends.

```python
def on_timeout(self)
```

This event is triggered if the request times out.

```python
def on_exception(self, exception: Exception)
```

This event is triggered if an exception occurs during streaming.

### Assistant Methods

The assistant streaming object also provides a few methods for convenience:

```python
def current_event() -> AssistantStreamEvent | None
def current_run() -> Run | None
def current_message_snapshot() -> Message | None
def current_run_step_snapshot() -> RunStep | None
```

These methods are provided to allow you to access additional context from within event handlers. In many cases
the handlers should include all the information you need for processing, but if additional context is required it
can be accessed.

Note: There is not always a relevant context in certain situations (these will be `None` in those cases).

```python
def get_final_run(self) -> Run
def get_final_run_steps(self) -> List[RunStep]
def get_final_messages(self) -> List[Message]
```

These methods are provided for convenience to collect information at the end of a stream. Calling these events
will trigger consumption of the stream until completion and then return the relevant accumulated objects.

# Polling Helpers

When interacting with the API some actions such as starting a Run and adding files to vector stores are asynchronous and take time to complete.
The SDK includes helper functions which will poll the status until it reaches a terminal state and then return the resulting object.
If an API method results in an action which could benefit from polling there will be a corresponding version of the
method ending in `_and_poll`.

All methods also allow you to set the polling frequency, how often the API is checked for an update, via a function argument (`poll_interval_ms`).

The polling methods are:

```python
client.beta.threads.create_and_run_poll(...)
client.beta.threads.runs.create_and_poll(...)
client.beta.threads.runs.submit_tool_ouptputs_and_poll(...)
client.beta.vector_stores.files.upload_and_poll(...)
client.beta.vector_stores.files.create_and_poll(...)
client.beta.vector_stores.file_batches.create_and_poll(...)
client.beta.vector_stores.file_batches.upload_and_poll(...)
```
