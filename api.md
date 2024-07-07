# Shared Types

```python
from openai.types import ErrorObject, FunctionDefinition, FunctionParameters
```

# Completions

Types:

```python
from openai.types import Completion, CompletionChoice, CompletionUsage
```

Methods:

- <code title="post /completions">client.completions.<a href="./src/openai/resources/completions.py">create</a>(\*\*<a href="src/openai/types/completion_create_params.py">params</a>) -> <a href="./src/openai/types/completion.py">Completion</a></code>

# Chat

Types:

```python
from openai.types import ChatModel
```

## Completions

Types:

```python
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionChunk,
    ChatCompletionContentPart,
    ChatCompletionContentPartImage,
    ChatCompletionContentPartText,
    ChatCompletionFunctionCallOption,
    ChatCompletionFunctionMessageParam,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionNamedToolChoice,
    ChatCompletionRole,
    ChatCompletionStreamOptions,
    ChatCompletionSystemMessageParam,
    ChatCompletionTokenLogprob,
    ChatCompletionTool,
    ChatCompletionToolChoiceOption,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)
```

Methods:

- <code title="post /chat/completions">client.chat.completions.<a href="./src/openai/resources/chat/completions.py">create</a>(\*\*<a href="src/openai/types/chat/completion_create_params.py">params</a>) -> <a href="./src/openai/types/chat/chat_completion.py">ChatCompletion</a></code>

# Embeddings

Types:

```python
from openai.types import CreateEmbeddingResponse, Embedding
```

Methods:

- <code title="post /embeddings">client.embeddings.<a href="./src/openai/resources/embeddings.py">create</a>(\*\*<a href="src/openai/types/embedding_create_params.py">params</a>) -> <a href="./src/openai/types/create_embedding_response.py">CreateEmbeddingResponse</a></code>

# Files

Types:

```python
from openai.types import FileContent, FileDeleted, FileObject
```

Methods:

- <code title="post /files">client.files.<a href="./src/openai/resources/files.py">create</a>(\*\*<a href="src/openai/types/file_create_params.py">params</a>) -> <a href="./src/openai/types/file_object.py">FileObject</a></code>
- <code title="get /files/{file_id}">client.files.<a href="./src/openai/resources/files.py">retrieve</a>(file_id) -> <a href="./src/openai/types/file_object.py">FileObject</a></code>
- <code title="get /files">client.files.<a href="./src/openai/resources/files.py">list</a>(\*\*<a href="src/openai/types/file_list_params.py">params</a>) -> <a href="./src/openai/types/file_object.py">SyncPage[FileObject]</a></code>
- <code title="delete /files/{file_id}">client.files.<a href="./src/openai/resources/files.py">delete</a>(file_id) -> <a href="./src/openai/types/file_deleted.py">FileDeleted</a></code>
- <code title="get /files/{file_id}/content">client.files.<a href="./src/openai/resources/files.py">content</a>(file_id) -> HttpxBinaryResponseContent</code>
- <code title="get /files/{file_id}/content">client.files.<a href="./src/openai/resources/files.py">retrieve_content</a>(file_id) -> str</code>
- <code>client.files.<a href="./src/openai/resources/files.py">wait_for_processing</a>(\*args) -> FileObject</code>

# Images

Types:

```python
from openai.types import Image, ImagesResponse
```

Methods:

- <code title="post /images/variations">client.images.<a href="./src/openai/resources/images.py">create_variation</a>(\*\*<a href="src/openai/types/image_create_variation_params.py">params</a>) -> <a href="./src/openai/types/images_response.py">ImagesResponse</a></code>
- <code title="post /images/edits">client.images.<a href="./src/openai/resources/images.py">edit</a>(\*\*<a href="src/openai/types/image_edit_params.py">params</a>) -> <a href="./src/openai/types/images_response.py">ImagesResponse</a></code>
- <code title="post /images/generations">client.images.<a href="./src/openai/resources/images.py">generate</a>(\*\*<a href="src/openai/types/image_generate_params.py">params</a>) -> <a href="./src/openai/types/images_response.py">ImagesResponse</a></code>

# Audio

## Transcriptions

Types:

```python
from openai.types.audio import Transcription
```

Methods:

- <code title="post /audio/transcriptions">client.audio.transcriptions.<a href="./src/openai/resources/audio/transcriptions.py">create</a>(\*\*<a href="src/openai/types/audio/transcription_create_params.py">params</a>) -> <a href="./src/openai/types/audio/transcription.py">Transcription</a></code>

## Translations

Types:

```python
from openai.types.audio import Translation
```

Methods:

- <code title="post /audio/translations">client.audio.translations.<a href="./src/openai/resources/audio/translations.py">create</a>(\*\*<a href="src/openai/types/audio/translation_create_params.py">params</a>) -> <a href="./src/openai/types/audio/translation.py">Translation</a></code>

## Speech

Methods:

- <code title="post /audio/speech">client.audio.speech.<a href="./src/openai/resources/audio/speech.py">create</a>(\*\*<a href="src/openai/types/audio/speech_create_params.py">params</a>) -> HttpxBinaryResponseContent</code>

# Moderations

Types:

```python
from openai.types import Moderation, ModerationCreateResponse
```

Methods:

- <code title="post /moderations">client.moderations.<a href="./src/openai/resources/moderations.py">create</a>(\*\*<a href="src/openai/types/moderation_create_params.py">params</a>) -> <a href="./src/openai/types/moderation_create_response.py">ModerationCreateResponse</a></code>

# Models

Types:

```python
from openai.types import Model, ModelDeleted
```

Methods:

- <code title="get /models/{model}">client.models.<a href="./src/openai/resources/models.py">retrieve</a>(model) -> <a href="./src/openai/types/model.py">Model</a></code>
- <code title="get /models">client.models.<a href="./src/openai/resources/models.py">list</a>() -> <a href="./src/openai/types/model.py">SyncPage[Model]</a></code>
- <code title="delete /models/{model}">client.models.<a href="./src/openai/resources/models.py">delete</a>(model) -> <a href="./src/openai/types/model_deleted.py">ModelDeleted</a></code>

# FineTuning

## Jobs

Types:

```python
from openai.types.fine_tuning import (
    FineTuningJob,
    FineTuningJobEvent,
    FineTuningJobIntegration,
    FineTuningJobWandbIntegration,
    FineTuningJobWandbIntegrationObject,
)
```

Methods:

- <code title="post /fine_tuning/jobs">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">create</a>(\*\*<a href="src/openai/types/fine_tuning/job_create_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>
- <code title="get /fine_tuning/jobs/{fine_tuning_job_id}">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">retrieve</a>(fine_tuning_job_id) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>
- <code title="get /fine_tuning/jobs">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">list</a>(\*\*<a href="src/openai/types/fine_tuning/job_list_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">SyncCursorPage[FineTuningJob]</a></code>
- <code title="post /fine_tuning/jobs/{fine_tuning_job_id}/cancel">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">cancel</a>(fine_tuning_job_id) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>
- <code title="get /fine_tuning/jobs/{fine_tuning_job_id}/events">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">list_events</a>(fine_tuning_job_id, \*\*<a href="src/openai/types/fine_tuning/job_list_events_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job_event.py">SyncCursorPage[FineTuningJobEvent]</a></code>

### Checkpoints

Types:

```python
from openai.types.fine_tuning.jobs import FineTuningJobCheckpoint
```

Methods:

- <code title="get /fine_tuning/jobs/{fine_tuning_job_id}/checkpoints">client.fine_tuning.jobs.checkpoints.<a href="./src/openai/resources/fine_tuning/jobs/checkpoints.py">list</a>(fine_tuning_job_id, \*\*<a href="src/openai/types/fine_tuning/jobs/checkpoint_list_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/jobs/fine_tuning_job_checkpoint.py">SyncCursorPage[FineTuningJobCheckpoint]</a></code>

# Beta

## VectorStores

Types:

```python
from openai.types.beta import VectorStore, VectorStoreDeleted
```

Methods:

- <code title="post /vector_stores">client.beta.vector_stores.<a href="./src/openai/resources/beta/vector_stores/vector_stores.py">create</a>(\*\*<a href="src/openai/types/beta/vector_store_create_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_store.py">VectorStore</a></code>
- <code title="get /vector_stores/{vector_store_id}">client.beta.vector_stores.<a href="./src/openai/resources/beta/vector_stores/vector_stores.py">retrieve</a>(vector_store_id) -> <a href="./src/openai/types/beta/vector_store.py">VectorStore</a></code>
- <code title="post /vector_stores/{vector_store_id}">client.beta.vector_stores.<a href="./src/openai/resources/beta/vector_stores/vector_stores.py">update</a>(vector_store_id, \*\*<a href="src/openai/types/beta/vector_store_update_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_store.py">VectorStore</a></code>
- <code title="get /vector_stores">client.beta.vector_stores.<a href="./src/openai/resources/beta/vector_stores/vector_stores.py">list</a>(\*\*<a href="src/openai/types/beta/vector_store_list_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_store.py">SyncCursorPage[VectorStore]</a></code>
- <code title="delete /vector_stores/{vector_store_id}">client.beta.vector_stores.<a href="./src/openai/resources/beta/vector_stores/vector_stores.py">delete</a>(vector_store_id) -> <a href="./src/openai/types/beta/vector_store_deleted.py">VectorStoreDeleted</a></code>

### Files

Types:

```python
from openai.types.beta.vector_stores import VectorStoreFile, VectorStoreFileDeleted
```

Methods:

- <code title="post /vector_stores/{vector_store_id}/files">client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">create</a>(vector_store_id, \*\*<a href="src/openai/types/beta/vector_stores/file_create_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file.py">VectorStoreFile</a></code>
- <code title="get /vector_stores/{vector_store_id}/files/{file_id}">client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">retrieve</a>(file_id, \*, vector_store_id) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file.py">VectorStoreFile</a></code>
- <code title="get /vector_stores/{vector_store_id}/files">client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">list</a>(vector_store_id, \*\*<a href="src/openai/types/beta/vector_stores/file_list_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file.py">SyncCursorPage[VectorStoreFile]</a></code>
- <code title="delete /vector_stores/{vector_store_id}/files/{file_id}">client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">delete</a>(file_id, \*, vector_store_id) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file_deleted.py">VectorStoreFileDeleted</a></code>
- <code>client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">create_and_poll</a>(\*args) -> VectorStoreFile</code>
- <code>client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">poll</a>(\*args) -> VectorStoreFile</code>
- <code>client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">upload</a>(\*args) -> VectorStoreFile</code>
- <code>client.beta.vector_stores.files.<a href="./src/openai/resources/beta/vector_stores/files.py">upload_and_poll</a>(\*args) -> VectorStoreFile</code>

### FileBatches

Types:

```python
from openai.types.beta.vector_stores import VectorStoreFileBatch
```

Methods:

- <code title="post /vector_stores/{vector_store_id}/file_batches">client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">create</a>(vector_store_id, \*\*<a href="src/openai/types/beta/vector_stores/file_batch_create_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file_batch.py">VectorStoreFileBatch</a></code>
- <code title="get /vector_stores/{vector_store_id}/file_batches/{batch_id}">client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">retrieve</a>(batch_id, \*, vector_store_id) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file_batch.py">VectorStoreFileBatch</a></code>
- <code title="post /vector_stores/{vector_store_id}/file_batches/{batch_id}/cancel">client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">cancel</a>(batch_id, \*, vector_store_id) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file_batch.py">VectorStoreFileBatch</a></code>
- <code title="get /vector_stores/{vector_store_id}/file_batches/{batch_id}/files">client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">list_files</a>(batch_id, \*, vector_store_id, \*\*<a href="src/openai/types/beta/vector_stores/file_batch_list_files_params.py">params</a>) -> <a href="./src/openai/types/beta/vector_stores/vector_store_file.py">SyncCursorPage[VectorStoreFile]</a></code>
- <code>client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">create_and_poll</a>(\*args) -> VectorStoreFileBatch</code>
- <code>client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">poll</a>(\*args) -> VectorStoreFileBatch</code>
- <code>client.beta.vector_stores.file_batches.<a href="./src/openai/resources/beta/vector_stores/file_batches.py">upload_and_poll</a>(\*args) -> VectorStoreFileBatch</code>

## Assistants

Types:

```python
from openai.types.beta import (
    Assistant,
    AssistantDeleted,
    AssistantStreamEvent,
    AssistantTool,
    CodeInterpreterTool,
    FileSearchTool,
    FunctionTool,
    MessageStreamEvent,
    RunStepStreamEvent,
    RunStreamEvent,
    ThreadStreamEvent,
)
```

Methods:

- <code title="post /assistants">client.beta.assistants.<a href="./src/openai/resources/beta/assistants.py">create</a>(\*\*<a href="src/openai/types/beta/assistant_create_params.py">params</a>) -> <a href="./src/openai/types/beta/assistant.py">Assistant</a></code>
- <code title="get /assistants/{assistant_id}">client.beta.assistants.<a href="./src/openai/resources/beta/assistants.py">retrieve</a>(assistant_id) -> <a href="./src/openai/types/beta/assistant.py">Assistant</a></code>
- <code title="post /assistants/{assistant_id}">client.beta.assistants.<a href="./src/openai/resources/beta/assistants.py">update</a>(assistant_id, \*\*<a href="src/openai/types/beta/assistant_update_params.py">params</a>) -> <a href="./src/openai/types/beta/assistant.py">Assistant</a></code>
- <code title="get /assistants">client.beta.assistants.<a href="./src/openai/resources/beta/assistants.py">list</a>(\*\*<a href="src/openai/types/beta/assistant_list_params.py">params</a>) -> <a href="./src/openai/types/beta/assistant.py">SyncCursorPage[Assistant]</a></code>
- <code title="delete /assistants/{assistant_id}">client.beta.assistants.<a href="./src/openai/resources/beta/assistants.py">delete</a>(assistant_id) -> <a href="./src/openai/types/beta/assistant_deleted.py">AssistantDeleted</a></code>

## Threads

Types:

```python
from openai.types.beta import (
    AssistantResponseFormat,
    AssistantResponseFormatOption,
    AssistantToolChoice,
    AssistantToolChoiceFunction,
    AssistantToolChoiceOption,
    Thread,
    ThreadDeleted,
)
```

Methods:

- <code title="post /threads">client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">create</a>(\*\*<a href="src/openai/types/beta/thread_create_params.py">params</a>) -> <a href="./src/openai/types/beta/thread.py">Thread</a></code>
- <code title="get /threads/{thread_id}">client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">retrieve</a>(thread_id) -> <a href="./src/openai/types/beta/thread.py">Thread</a></code>
- <code title="post /threads/{thread_id}">client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">update</a>(thread_id, \*\*<a href="src/openai/types/beta/thread_update_params.py">params</a>) -> <a href="./src/openai/types/beta/thread.py">Thread</a></code>
- <code title="delete /threads/{thread_id}">client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">delete</a>(thread_id) -> <a href="./src/openai/types/beta/thread_deleted.py">ThreadDeleted</a></code>
- <code title="post /threads/runs">client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">create_and_run</a>(\*\*<a href="src/openai/types/beta/thread_create_and_run_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/run.py">Run</a></code>
- <code>client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">create_and_run_poll</a>(\*args) -> Run</code>
- <code>client.beta.threads.<a href="./src/openai/resources/beta/threads/threads.py">create_and_run_stream</a>(\*args) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]</code>

### Runs

Types:

```python
from openai.types.beta.threads import RequiredActionFunctionToolCall, Run, RunStatus
```

Methods:

- <code title="post /threads/{thread_id}/runs">client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">create</a>(thread_id, \*\*<a href="src/openai/types/beta/threads/run_create_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/run.py">Run</a></code>
- <code title="get /threads/{thread_id}/runs/{run_id}">client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">retrieve</a>(run_id, \*, thread_id) -> <a href="./src/openai/types/beta/threads/run.py">Run</a></code>
- <code title="post /threads/{thread_id}/runs/{run_id}">client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">update</a>(run_id, \*, thread_id, \*\*<a href="src/openai/types/beta/threads/run_update_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/run.py">Run</a></code>
- <code title="get /threads/{thread_id}/runs">client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">list</a>(thread_id, \*\*<a href="src/openai/types/beta/threads/run_list_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/run.py">SyncCursorPage[Run]</a></code>
- <code title="post /threads/{thread_id}/runs/{run_id}/cancel">client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">cancel</a>(run_id, \*, thread_id) -> <a href="./src/openai/types/beta/threads/run.py">Run</a></code>
- <code title="post /threads/{thread_id}/runs/{run_id}/submit_tool_outputs">client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">submit_tool_outputs</a>(run_id, \*, thread_id, \*\*<a href="src/openai/types/beta/threads/run_submit_tool_outputs_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/run.py">Run</a></code>
- <code>client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">create_and_poll</a>(\*args) -> Run</code>
- <code>client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">create_and_stream</a>(\*args) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]</code>
- <code>client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">poll</a>(\*args) -> Run</code>
- <code>client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">stream</a>(\*args) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]</code>
- <code>client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">submit_tool_outputs_and_poll</a>(\*args) -> Run</code>
- <code>client.beta.threads.runs.<a href="./src/openai/resources/beta/threads/runs/runs.py">submit_tool_outputs_stream</a>(\*args) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]</code>

#### Steps

Types:

```python
from openai.types.beta.threads.runs import (
    CodeInterpreterLogs,
    CodeInterpreterOutputImage,
    CodeInterpreterToolCall,
    CodeInterpreterToolCallDelta,
    FileSearchToolCall,
    FileSearchToolCallDelta,
    FunctionToolCall,
    FunctionToolCallDelta,
    MessageCreationStepDetails,
    RunStep,
    RunStepDelta,
    RunStepDeltaEvent,
    RunStepDeltaMessageDelta,
    ToolCall,
    ToolCallDelta,
    ToolCallDeltaObject,
    ToolCallsStepDetails,
)
```

Methods:

- <code title="get /threads/{thread_id}/runs/{run_id}/steps/{step_id}">client.beta.threads.runs.steps.<a href="./src/openai/resources/beta/threads/runs/steps.py">retrieve</a>(step_id, \*, thread_id, run_id) -> <a href="./src/openai/types/beta/threads/runs/run_step.py">RunStep</a></code>
- <code title="get /threads/{thread_id}/runs/{run_id}/steps">client.beta.threads.runs.steps.<a href="./src/openai/resources/beta/threads/runs/steps.py">list</a>(run_id, \*, thread_id, \*\*<a href="src/openai/types/beta/threads/runs/step_list_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/runs/run_step.py">SyncCursorPage[RunStep]</a></code>

### Messages

Types:

```python
from openai.types.beta.threads import (
    Annotation,
    AnnotationDelta,
    FileCitationAnnotation,
    FileCitationDeltaAnnotation,
    FilePathAnnotation,
    FilePathDeltaAnnotation,
    ImageFile,
    ImageFileContentBlock,
    ImageFileDelta,
    ImageFileDeltaBlock,
    ImageURL,
    ImageURLContentBlock,
    ImageURLDelta,
    ImageURLDeltaBlock,
    Message,
    MessageContent,
    MessageContentDelta,
    MessageContentPartParam,
    MessageDeleted,
    MessageDelta,
    MessageDeltaEvent,
    Text,
    TextContentBlock,
    TextContentBlockParam,
    TextDelta,
    TextDeltaBlock,
)
```

Methods:

- <code title="post /threads/{thread_id}/messages">client.beta.threads.messages.<a href="./src/openai/resources/beta/threads/messages.py">create</a>(thread_id, \*\*<a href="src/openai/types/beta/threads/message_create_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/message.py">Message</a></code>
- <code title="get /threads/{thread_id}/messages/{message_id}">client.beta.threads.messages.<a href="./src/openai/resources/beta/threads/messages.py">retrieve</a>(message_id, \*, thread_id) -> <a href="./src/openai/types/beta/threads/message.py">Message</a></code>
- <code title="post /threads/{thread_id}/messages/{message_id}">client.beta.threads.messages.<a href="./src/openai/resources/beta/threads/messages.py">update</a>(message_id, \*, thread_id, \*\*<a href="src/openai/types/beta/threads/message_update_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/message.py">Message</a></code>
- <code title="get /threads/{thread_id}/messages">client.beta.threads.messages.<a href="./src/openai/resources/beta/threads/messages.py">list</a>(thread_id, \*\*<a href="src/openai/types/beta/threads/message_list_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/message.py">SyncCursorPage[Message]</a></code>
- <code title="delete /threads/{thread_id}/messages/{message_id}">client.beta.threads.messages.<a href="./src/openai/resources/beta/threads/messages.py">delete</a>(message_id, \*, thread_id) -> <a href="./src/openai/types/beta/threads/message_deleted.py">MessageDeleted</a></code>

# Batches

Types:

```python
from openai.types import Batch, BatchError, BatchRequestCounts
```

Methods:

- <code title="post /batches">client.batches.<a href="./src/openai/resources/batches.py">create</a>(\*\*<a href="src/openai/types/batch_create_params.py">params</a>) -> <a href="./src/openai/types/batch.py">Batch</a></code>
- <code title="get /batches/{batch_id}">client.batches.<a href="./src/openai/resources/batches.py">retrieve</a>(batch_id) -> <a href="./src/openai/types/batch.py">Batch</a></code>
- <code title="get /batches">client.batches.<a href="./src/openai/resources/batches.py">list</a>(\*\*<a href="src/openai/types/batch_list_params.py">params</a>) -> <a href="./src/openai/types/batch.py">SyncCursorPage[Batch]</a></code>
- <code title="post /batches/{batch_id}/cancel">client.batches.<a href="./src/openai/resources/batches.py">cancel</a>(batch_id) -> <a href="./src/openai/types/batch.py">Batch</a></code>
