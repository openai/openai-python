# Shared Types

```python
from openai.types import (
    AllModels,
    ChatModel,
    ComparisonFilter,
    CompoundFilter,
    ErrorObject,
    FunctionDefinition,
    FunctionParameters,
    Metadata,
    Reasoning,
    ReasoningEffort,
    ResponseFormatJSONObject,
    ResponseFormatJSONSchema,
    ResponseFormatText,
    ResponsesModel,
)
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
    ChatCompletionAudio,
    ChatCompletionAudioParam,
    ChatCompletionChunk,
    ChatCompletionContentPart,
    ChatCompletionContentPartImage,
    ChatCompletionContentPartInputAudio,
    ChatCompletionContentPartRefusal,
    ChatCompletionContentPartText,
    ChatCompletionDeleted,
    ChatCompletionDeveloperMessageParam,
    ChatCompletionFunctionCallOption,
    ChatCompletionFunctionMessageParam,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionModality,
    ChatCompletionNamedToolChoice,
    ChatCompletionPredictionContent,
    ChatCompletionRole,
    ChatCompletionStoreMessage,
    ChatCompletionStreamOptions,
    ChatCompletionSystemMessageParam,
    ChatCompletionTokenLogprob,
    ChatCompletionTool,
    ChatCompletionToolChoiceOption,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionReasoningEffort,
)
```

Methods:

- <code title="post /chat/completions">client.chat.completions.<a href="./src/openai/resources/chat/completions/completions.py">create</a>(\*\*<a href="src/openai/types/chat/completion_create_params.py">params</a>) -> <a href="./src/openai/types/chat/chat_completion.py">ChatCompletion</a></code>
- <code title="get /chat/completions/{completion_id}">client.chat.completions.<a href="./src/openai/resources/chat/completions/completions.py">retrieve</a>(completion_id) -> <a href="./src/openai/types/chat/chat_completion.py">ChatCompletion</a></code>
- <code title="post /chat/completions/{completion_id}">client.chat.completions.<a href="./src/openai/resources/chat/completions/completions.py">update</a>(completion_id, \*\*<a href="src/openai/types/chat/completion_update_params.py">params</a>) -> <a href="./src/openai/types/chat/chat_completion.py">ChatCompletion</a></code>
- <code title="get /chat/completions">client.chat.completions.<a href="./src/openai/resources/chat/completions/completions.py">list</a>(\*\*<a href="src/openai/types/chat/completion_list_params.py">params</a>) -> <a href="./src/openai/types/chat/chat_completion.py">SyncCursorPage[ChatCompletion]</a></code>
- <code title="delete /chat/completions/{completion_id}">client.chat.completions.<a href="./src/openai/resources/chat/completions/completions.py">delete</a>(completion_id) -> <a href="./src/openai/types/chat/chat_completion_deleted.py">ChatCompletionDeleted</a></code>

### Messages

Methods:

- <code title="get /chat/completions/{completion_id}/messages">client.chat.completions.messages.<a href="./src/openai/resources/chat/completions/messages.py">list</a>(completion_id, \*\*<a href="src/openai/types/chat/completions/message_list_params.py">params</a>) -> <a href="./src/openai/types/chat/chat_completion_store_message.py">SyncCursorPage[ChatCompletionStoreMessage]</a></code>

# Embeddings

Types:

```python
from openai.types import CreateEmbeddingResponse, Embedding, EmbeddingModel
```

Methods:

- <code title="post /embeddings">client.embeddings.<a href="./src/openai/resources/embeddings.py">create</a>(\*\*<a href="src/openai/types/embedding_create_params.py">params</a>) -> <a href="./src/openai/types/create_embedding_response.py">CreateEmbeddingResponse</a></code>

# Files

Types:

```python
from openai.types import FileContent, FileDeleted, FileObject, FilePurpose
```

Methods:

- <code title="post /files">client.files.<a href="./src/openai/resources/files.py">create</a>(\*\*<a href="src/openai/types/file_create_params.py">params</a>) -> <a href="./src/openai/types/file_object.py">FileObject</a></code>
- <code title="get /files/{file_id}">client.files.<a href="./src/openai/resources/files.py">retrieve</a>(file_id) -> <a href="./src/openai/types/file_object.py">FileObject</a></code>
- <code title="get /files">client.files.<a href="./src/openai/resources/files.py">list</a>(\*\*<a href="src/openai/types/file_list_params.py">params</a>) -> <a href="./src/openai/types/file_object.py">SyncCursorPage[FileObject]</a></code>
- <code title="delete /files/{file_id}">client.files.<a href="./src/openai/resources/files.py">delete</a>(file_id) -> <a href="./src/openai/types/file_deleted.py">FileDeleted</a></code>
- <code title="get /files/{file_id}/content">client.files.<a href="./src/openai/resources/files.py">content</a>(file_id) -> HttpxBinaryResponseContent</code>
- <code title="get /files/{file_id}/content">client.files.<a href="./src/openai/resources/files.py">retrieve_content</a>(file_id) -> <a href="./src/openai/types/file_content.py">str</a></code>
- <code>client.files.<a href="./src/openai/resources/files.py">wait_for_processing</a>(\*args) -> FileObject</code>

# Images

Types:

```python
from openai.types import Image, ImageModel, ImagesResponse
```

Methods:

- <code title="post /images/variations">client.images.<a href="./src/openai/resources/images.py">create_variation</a>(\*\*<a href="src/openai/types/image_create_variation_params.py">params</a>) -> <a href="./src/openai/types/images_response.py">ImagesResponse</a></code>
- <code title="post /images/edits">client.images.<a href="./src/openai/resources/images.py">edit</a>(\*\*<a href="src/openai/types/image_edit_params.py">params</a>) -> <a href="./src/openai/types/images_response.py">ImagesResponse</a></code>
- <code title="post /images/generations">client.images.<a href="./src/openai/resources/images.py">generate</a>(\*\*<a href="src/openai/types/image_generate_params.py">params</a>) -> <a href="./src/openai/types/images_response.py">ImagesResponse</a></code>

# Audio

Types:

```python
from openai.types import AudioModel, AudioResponseFormat
```

## Transcriptions

Types:

```python
from openai.types.audio import (
    Transcription,
    TranscriptionInclude,
    TranscriptionSegment,
    TranscriptionStreamEvent,
    TranscriptionTextDeltaEvent,
    TranscriptionTextDoneEvent,
    TranscriptionVerbose,
    TranscriptionWord,
    TranscriptionCreateResponse,
)
```

Methods:

- <code title="post /audio/transcriptions">client.audio.transcriptions.<a href="./src/openai/resources/audio/transcriptions.py">create</a>(\*\*<a href="src/openai/types/audio/transcription_create_params.py">params</a>) -> <a href="./src/openai/types/audio/transcription_create_response.py">TranscriptionCreateResponse</a></code>

## Translations

Types:

```python
from openai.types.audio import Translation, TranslationVerbose, TranslationCreateResponse
```

Methods:

- <code title="post /audio/translations">client.audio.translations.<a href="./src/openai/resources/audio/translations.py">create</a>(\*\*<a href="src/openai/types/audio/translation_create_params.py">params</a>) -> <a href="./src/openai/types/audio/translation_create_response.py">TranslationCreateResponse</a></code>

## Speech

Types:

```python
from openai.types.audio import SpeechModel
```

Methods:

- <code title="post /audio/speech">client.audio.speech.<a href="./src/openai/resources/audio/speech.py">create</a>(\*\*<a href="src/openai/types/audio/speech_create_params.py">params</a>) -> HttpxBinaryResponseContent</code>

# Moderations

Types:

```python
from openai.types import (
    Moderation,
    ModerationImageURLInput,
    ModerationModel,
    ModerationMultiModalInput,
    ModerationTextInput,
    ModerationCreateResponse,
)
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

## Methods

Types:

```python
from openai.types.fine_tuning import (
    DpoHyperparameters,
    DpoMethod,
    ReinforcementHyperparameters,
    ReinforcementMethod,
    SupervisedHyperparameters,
    SupervisedMethod,
)
```

## Jobs

Types:

```python
from openai.types.fine_tuning import (
    FineTuningJob,
    FineTuningJobEvent,
    FineTuningJobWandbIntegration,
    FineTuningJobWandbIntegrationObject,
    FineTuningJobIntegration,
)
```

Methods:

- <code title="post /fine_tuning/jobs">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">create</a>(\*\*<a href="src/openai/types/fine_tuning/job_create_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>
- <code title="get /fine_tuning/jobs/{fine_tuning_job_id}">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">retrieve</a>(fine_tuning_job_id) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>
- <code title="get /fine_tuning/jobs">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">list</a>(\*\*<a href="src/openai/types/fine_tuning/job_list_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">SyncCursorPage[FineTuningJob]</a></code>
- <code title="post /fine_tuning/jobs/{fine_tuning_job_id}/cancel">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">cancel</a>(fine_tuning_job_id) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>
- <code title="get /fine_tuning/jobs/{fine_tuning_job_id}/events">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">list_events</a>(fine_tuning_job_id, \*\*<a href="src/openai/types/fine_tuning/job_list_events_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job_event.py">SyncCursorPage[FineTuningJobEvent]</a></code>
- <code title="post /fine_tuning/jobs/{fine_tuning_job_id}/pause">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">pause</a>(fine_tuning_job_id) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>
- <code title="post /fine_tuning/jobs/{fine_tuning_job_id}/resume">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs/jobs.py">resume</a>(fine_tuning_job_id) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>

### Checkpoints

Types:

```python
from openai.types.fine_tuning.jobs import FineTuningJobCheckpoint
```

Methods:

- <code title="get /fine_tuning/jobs/{fine_tuning_job_id}/checkpoints">client.fine_tuning.jobs.checkpoints.<a href="./src/openai/resources/fine_tuning/jobs/checkpoints.py">list</a>(fine_tuning_job_id, \*\*<a href="src/openai/types/fine_tuning/jobs/checkpoint_list_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/jobs/fine_tuning_job_checkpoint.py">SyncCursorPage[FineTuningJobCheckpoint]</a></code>

## Checkpoints

### Permissions

Types:

```python
from openai.types.fine_tuning.checkpoints import (
    PermissionCreateResponse,
    PermissionRetrieveResponse,
    PermissionDeleteResponse,
)
```

Methods:

- <code title="post /fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions">client.fine_tuning.checkpoints.permissions.<a href="./src/openai/resources/fine_tuning/checkpoints/permissions.py">create</a>(fine_tuned_model_checkpoint, \*\*<a href="src/openai/types/fine_tuning/checkpoints/permission_create_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/checkpoints/permission_create_response.py">SyncPage[PermissionCreateResponse]</a></code>
- <code title="get /fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions">client.fine_tuning.checkpoints.permissions.<a href="./src/openai/resources/fine_tuning/checkpoints/permissions.py">retrieve</a>(fine_tuned_model_checkpoint, \*\*<a href="src/openai/types/fine_tuning/checkpoints/permission_retrieve_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/checkpoints/permission_retrieve_response.py">PermissionRetrieveResponse</a></code>
- <code title="delete /fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions/{permission_id}">client.fine_tuning.checkpoints.permissions.<a href="./src/openai/resources/fine_tuning/checkpoints/permissions.py">delete</a>(permission_id, \*, fine_tuned_model_checkpoint) -> <a href="./src/openai/types/fine_tuning/checkpoints/permission_delete_response.py">PermissionDeleteResponse</a></code>

## Alpha

### Graders

Types:

```python
from openai.types.fine_tuning.alpha import GraderRunResponse, GraderValidateResponse
```

Methods:

- <code title="post /fine_tuning/alpha/graders/run">client.fine_tuning.alpha.graders.<a href="./src/openai/resources/fine_tuning/alpha/graders.py">run</a>(\*\*<a href="src/openai/types/fine_tuning/alpha/grader_run_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/alpha/grader_run_response.py">GraderRunResponse</a></code>
- <code title="post /fine_tuning/alpha/graders/validate">client.fine_tuning.alpha.graders.<a href="./src/openai/resources/fine_tuning/alpha/graders.py">validate</a>(\*\*<a href="src/openai/types/fine_tuning/alpha/grader_validate_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/alpha/grader_validate_response.py">GraderValidateResponse</a></code>

# Graders

## GraderModels

Types:

```python
from openai.types.graders import (
    LabelModelGrader,
    MultiGrader,
    PythonGrader,
    ScoreModelGrader,
    StringCheckGrader,
    TextSimilarityGrader,
)
```

# VectorStores

Types:

```python
from openai.types import (
    AutoFileChunkingStrategyParam,
    FileChunkingStrategy,
    FileChunkingStrategyParam,
    OtherFileChunkingStrategyObject,
    StaticFileChunkingStrategy,
    StaticFileChunkingStrategyObject,
    StaticFileChunkingStrategyObjectParam,
    VectorStore,
    VectorStoreDeleted,
    VectorStoreSearchResponse,
)
```

Methods:

- <code title="post /vector_stores">client.vector_stores.<a href="./src/openai/resources/vector_stores/vector_stores.py">create</a>(\*\*<a href="src/openai/types/vector_store_create_params.py">params</a>) -> <a href="./src/openai/types/vector_store.py">VectorStore</a></code>
- <code title="get /vector_stores/{vector_store_id}">client.vector_stores.<a href="./src/openai/resources/vector_stores/vector_stores.py">retrieve</a>(vector_store_id) -> <a href="./src/openai/types/vector_store.py">VectorStore</a></code>
- <code title="post /vector_stores/{vector_store_id}">client.vector_stores.<a href="./src/openai/resources/vector_stores/vector_stores.py">update</a>(vector_store_id, \*\*<a href="src/openai/types/vector_store_update_params.py">params</a>) -> <a href="./src/openai/types/vector_store.py">VectorStore</a></code>
- <code title="get /vector_stores">client.vector_stores.<a href="./src/openai/resources/vector_stores/vector_stores.py">list</a>(\*\*<a href="src/openai/types/vector_store_list_params.py">params</a>) -> <a href="./src/openai/types/vector_store.py">SyncCursorPage[VectorStore]</a></code>
- <code title="delete /vector_stores/{vector_store_id}">client.vector_stores.<a href="./src/openai/resources/vector_stores/vector_stores.py">delete</a>(vector_store_id) -> <a href="./src/openai/types/vector_store_deleted.py">VectorStoreDeleted</a></code>
- <code title="post /vector_stores/{vector_store_id}/search">client.vector_stores.<a href="./src/openai/resources/vector_stores/vector_stores.py">search</a>(vector_store_id, \*\*<a href="src/openai/types/vector_store_search_params.py">params</a>) -> <a href="./src/openai/types/vector_store_search_response.py">SyncPage[VectorStoreSearchResponse]</a></code>

## Files

Types:

```python
from openai.types.vector_stores import VectorStoreFile, VectorStoreFileDeleted, FileContentResponse
```

Methods:

- <code title="post /vector_stores/{vector_store_id}/files">client.vector_stores.files.<a href="./src/openai/resources/vector_stores/files.py">create</a>(vector_store_id, \*\*<a href="src/openai/types/vector_stores/file_create_params.py">params</a>) -> <a href="./src/openai/types/vector_stores/vector_store_file.py">VectorStoreFile</a></code>
- <code title="get /vector_stores/{vector_store_id}/files/{file_id}">client.vector_stores.files.<a href="./src/openai/resources/vector_stores/files.py">retrieve</a>(file_id, \*, vector_store_id) -> <a href="./src/openai/types/vector_stores/vector_store_file.py">VectorStoreFile</a></code>
- <code title="post /vector_stores/{vector_store_id}/files/{file_id}">client.vector_stores.files.<a href="./src/openai/resources/vector_stores/files.py">update</a>(file_id, \*, vector_store_id, \*\*<a href="src/openai/types/vector_stores/file_update_params.py">params</a>) -> <a href="./src/openai/types/vector_stores/vector_store_file.py">VectorStoreFile</a></code>
- <code title="get /vector_stores/{vector_store_id}/files">client.vector_stores.files.<a href="./src/openai/resources/vector_stores/files.py">list</a>(vector_store_id, \*\*<a href="src/openai/types/vector_stores/file_list_params.py">params</a>) -> <a href="./src/openai/types/vector_stores/vector_store_file.py">SyncCursorPage[VectorStoreFile]</a></code>
- <code title="delete /vector_stores/{vector_store_id}/files/{file_id}">client.vector_stores.files.<a href="./src/openai/resources/vector_stores/files.py">delete</a>(file_id, \*, vector_store_id) -> <a href="./src/openai/types/vector_stores/vector_store_file_deleted.py">VectorStoreFileDeleted</a></code>
- <code title="get /vector_stores/{vector_store_id}/files/{file_id}/content">client.vector_stores.files.<a href="./src/openai/resources/vector_stores/files.py">content</a>(file_id, \*, vector_store_id) -> <a href="./src/openai/types/vector_stores/file_content_response.py">SyncPage[FileContentResponse]</a></code>
- <code>client.vector_stores.files.<a href="./src/openai/resources/vector_stores/files.py">create_and_poll</a>(\*args) -> VectorStoreFile</code>
- <code>client.vector_stores.files.<a href="./src/openai/resources/vector_stores/files.py">poll</a>(\*args) -> VectorStoreFile</code>
- <code>client.vector_stores.files.<a href="./src/openai/resources/vector_stores/files.py">upload</a>(\*args) -> VectorStoreFile</code>
- <code>client.vector_stores.files.<a href="./src/openai/resources/vector_stores/files.py">upload_and_poll</a>(\*args) -> VectorStoreFile</code>

## FileBatches

Types:

```python
from openai.types.vector_stores import VectorStoreFileBatch
```

Methods:

- <code title="post /vector_stores/{vector_store_id}/file_batches">client.vector_stores.file_batches.<a href="./src/openai/resources/vector_stores/file_batches.py">create</a>(vector_store_id, \*\*<a href="src/openai/types/vector_stores/file_batch_create_params.py">params</a>) -> <a href="./src/openai/types/vector_stores/vector_store_file_batch.py">VectorStoreFileBatch</a></code>
- <code title="get /vector_stores/{vector_store_id}/file_batches/{batch_id}">client.vector_stores.file_batches.<a href="./src/openai/resources/vector_stores/file_batches.py">retrieve</a>(batch_id, \*, vector_store_id) -> <a href="./src/openai/types/vector_stores/vector_store_file_batch.py">VectorStoreFileBatch</a></code>
- <code title="post /vector_stores/{vector_store_id}/file_batches/{batch_id}/cancel">client.vector_stores.file_batches.<a href="./src/openai/resources/vector_stores/file_batches.py">cancel</a>(batch_id, \*, vector_store_id) -> <a href="./src/openai/types/vector_stores/vector_store_file_batch.py">VectorStoreFileBatch</a></code>
- <code title="get /vector_stores/{vector_store_id}/file_batches/{batch_id}/files">client.vector_stores.file_batches.<a href="./src/openai/resources/vector_stores/file_batches.py">list_files</a>(batch_id, \*, vector_store_id, \*\*<a href="src/openai/types/vector_stores/file_batch_list_files_params.py">params</a>) -> <a href="./src/openai/types/vector_stores/vector_store_file.py">SyncCursorPage[VectorStoreFile]</a></code>
- <code>client.vector_stores.file_batches.<a href="./src/openai/resources/vector_stores/file_batches.py">create_and_poll</a>(\*args) -> VectorStoreFileBatch</code>
- <code>client.vector_stores.file_batches.<a href="./src/openai/resources/vector_stores/file_batches.py">poll</a>(\*args) -> VectorStoreFileBatch</code>
- <code>client.vector_stores.file_batches.<a href="./src/openai/resources/vector_stores/file_batches.py">upload_and_poll</a>(\*args) -> VectorStoreFileBatch</code>

# Beta

## Realtime

Types:

```python
from openai.types.beta.realtime import (
    ConversationCreatedEvent,
    ConversationItem,
    ConversationItemContent,
    ConversationItemCreateEvent,
    ConversationItemCreatedEvent,
    ConversationItemDeleteEvent,
    ConversationItemDeletedEvent,
    ConversationItemInputAudioTranscriptionCompletedEvent,
    ConversationItemInputAudioTranscriptionDeltaEvent,
    ConversationItemInputAudioTranscriptionFailedEvent,
    ConversationItemRetrieveEvent,
    ConversationItemTruncateEvent,
    ConversationItemTruncatedEvent,
    ConversationItemWithReference,
    ErrorEvent,
    InputAudioBufferAppendEvent,
    InputAudioBufferClearEvent,
    InputAudioBufferClearedEvent,
    InputAudioBufferCommitEvent,
    InputAudioBufferCommittedEvent,
    InputAudioBufferSpeechStartedEvent,
    InputAudioBufferSpeechStoppedEvent,
    RateLimitsUpdatedEvent,
    RealtimeClientEvent,
    RealtimeResponse,
    RealtimeResponseStatus,
    RealtimeResponseUsage,
    RealtimeServerEvent,
    ResponseAudioDeltaEvent,
    ResponseAudioDoneEvent,
    ResponseAudioTranscriptDeltaEvent,
    ResponseAudioTranscriptDoneEvent,
    ResponseCancelEvent,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseCreateEvent,
    ResponseCreatedEvent,
    ResponseDoneEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseFunctionCallArgumentsDoneEvent,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
    SessionCreatedEvent,
    SessionUpdateEvent,
    SessionUpdatedEvent,
    TranscriptionSessionUpdate,
    TranscriptionSessionUpdatedEvent,
)
```

### Sessions

Types:

```python
from openai.types.beta.realtime import Session, SessionCreateResponse
```

Methods:

- <code title="post /realtime/sessions">client.beta.realtime.sessions.<a href="./src/openai/resources/beta/realtime/sessions.py">create</a>(\*\*<a href="src/openai/types/beta/realtime/session_create_params.py">params</a>) -> <a href="./src/openai/types/beta/realtime/session_create_response.py">SessionCreateResponse</a></code>

### TranscriptionSessions

Types:

```python
from openai.types.beta.realtime import TranscriptionSession
```

Methods:

- <code title="post /realtime/transcription_sessions">client.beta.realtime.transcription_sessions.<a href="./src/openai/resources/beta/realtime/transcription_sessions.py">create</a>(\*\*<a href="src/openai/types/beta/realtime/transcription_session_create_params.py">params</a>) -> <a href="./src/openai/types/beta/realtime/transcription_session.py">TranscriptionSession</a></code>

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
    RunStepInclude,
    ToolCall,
    ToolCallDelta,
    ToolCallDeltaObject,
    ToolCallsStepDetails,
)
```

Methods:

- <code title="get /threads/{thread_id}/runs/{run_id}/steps/{step_id}">client.beta.threads.runs.steps.<a href="./src/openai/resources/beta/threads/runs/steps.py">retrieve</a>(step_id, \*, thread_id, run_id, \*\*<a href="src/openai/types/beta/threads/runs/step_retrieve_params.py">params</a>) -> <a href="./src/openai/types/beta/threads/runs/run_step.py">RunStep</a></code>
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
    RefusalContentBlock,
    RefusalDeltaBlock,
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

# Uploads

Types:

```python
from openai.types import Upload
```

Methods:

- <code title="post /uploads">client.uploads.<a href="./src/openai/resources/uploads/uploads.py">create</a>(\*\*<a href="src/openai/types/upload_create_params.py">params</a>) -> <a href="./src/openai/types/upload.py">Upload</a></code>
- <code title="post /uploads/{upload_id}/cancel">client.uploads.<a href="./src/openai/resources/uploads/uploads.py">cancel</a>(upload_id) -> <a href="./src/openai/types/upload.py">Upload</a></code>
- <code title="post /uploads/{upload_id}/complete">client.uploads.<a href="./src/openai/resources/uploads/uploads.py">complete</a>(upload_id, \*\*<a href="src/openai/types/upload_complete_params.py">params</a>) -> <a href="./src/openai/types/upload.py">Upload</a></code>

## Parts

Types:

```python
from openai.types.uploads import UploadPart
```

Methods:

- <code title="post /uploads/{upload_id}/parts">client.uploads.parts.<a href="./src/openai/resources/uploads/parts.py">create</a>(upload_id, \*\*<a href="src/openai/types/uploads/part_create_params.py">params</a>) -> <a href="./src/openai/types/uploads/upload_part.py">UploadPart</a></code>

# Responses

Types:

```python
from openai.types.responses import (
    ComputerTool,
    EasyInputMessage,
    FileSearchTool,
    FunctionTool,
    Response,
    ResponseAudioDeltaEvent,
    ResponseAudioDoneEvent,
    ResponseAudioTranscriptDeltaEvent,
    ResponseAudioTranscriptDoneEvent,
    ResponseCodeInterpreterCallCodeDeltaEvent,
    ResponseCodeInterpreterCallCodeDoneEvent,
    ResponseCodeInterpreterCallCompletedEvent,
    ResponseCodeInterpreterCallInProgressEvent,
    ResponseCodeInterpreterCallInterpretingEvent,
    ResponseCodeInterpreterToolCall,
    ResponseCompletedEvent,
    ResponseComputerToolCall,
    ResponseComputerToolCallOutputItem,
    ResponseComputerToolCallOutputScreenshot,
    ResponseContent,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseCreatedEvent,
    ResponseError,
    ResponseErrorEvent,
    ResponseFailedEvent,
    ResponseFileSearchCallCompletedEvent,
    ResponseFileSearchCallInProgressEvent,
    ResponseFileSearchCallSearchingEvent,
    ResponseFileSearchToolCall,
    ResponseFormatTextConfig,
    ResponseFormatTextJSONSchemaConfig,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseFunctionCallArgumentsDoneEvent,
    ResponseFunctionToolCall,
    ResponseFunctionToolCallItem,
    ResponseFunctionToolCallOutputItem,
    ResponseFunctionWebSearch,
    ResponseInProgressEvent,
    ResponseIncludable,
    ResponseIncompleteEvent,
    ResponseInput,
    ResponseInputAudio,
    ResponseInputContent,
    ResponseInputFile,
    ResponseInputImage,
    ResponseInputItem,
    ResponseInputMessageContentList,
    ResponseInputMessageItem,
    ResponseInputText,
    ResponseItem,
    ResponseOutputAudio,
    ResponseOutputItem,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseOutputMessage,
    ResponseOutputRefusal,
    ResponseOutputText,
    ResponseReasoningItem,
    ResponseReasoningSummaryPartAddedEvent,
    ResponseReasoningSummaryPartDoneEvent,
    ResponseReasoningSummaryTextDeltaEvent,
    ResponseReasoningSummaryTextDoneEvent,
    ResponseRefusalDeltaEvent,
    ResponseRefusalDoneEvent,
    ResponseStatus,
    ResponseStreamEvent,
    ResponseTextAnnotationDeltaEvent,
    ResponseTextConfig,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
    ResponseUsage,
    ResponseWebSearchCallCompletedEvent,
    ResponseWebSearchCallInProgressEvent,
    ResponseWebSearchCallSearchingEvent,
    Tool,
    ToolChoiceFunction,
    ToolChoiceOptions,
    ToolChoiceTypes,
    WebSearchTool,
)
```

Methods:

- <code title="post /responses">client.responses.<a href="./src/openai/resources/responses/responses.py">create</a>(\*\*<a href="src/openai/types/responses/response_create_params.py">params</a>) -> <a href="./src/openai/types/responses/response.py">Response</a></code>
- <code title="get /responses/{response_id}">client.responses.<a href="./src/openai/resources/responses/responses.py">retrieve</a>(response_id, \*\*<a href="src/openai/types/responses/response_retrieve_params.py">params</a>) -> <a href="./src/openai/types/responses/response.py">Response</a></code>
- <code title="delete /responses/{response_id}">client.responses.<a href="./src/openai/resources/responses/responses.py">delete</a>(response_id) -> None</code>

## InputItems

Types:

```python
from openai.types.responses import ResponseItemList
```

Methods:

- <code title="get /responses/{response_id}/input_items">client.responses.input_items.<a href="./src/openai/resources/responses/input_items.py">list</a>(response_id, \*\*<a href="src/openai/types/responses/input_item_list_params.py">params</a>) -> <a href="./src/openai/types/responses/response_item.py">SyncCursorPage[ResponseItem]</a></code>

# Evals

Types:

```python
from openai.types import (
    EvalCustomDataSourceConfig,
    EvalStoredCompletionsDataSourceConfig,
    EvalCreateResponse,
    EvalRetrieveResponse,
    EvalUpdateResponse,
    EvalListResponse,
    EvalDeleteResponse,
)
```

Methods:

- <code title="post /evals">client.evals.<a href="./src/openai/resources/evals/evals.py">create</a>(\*\*<a href="src/openai/types/eval_create_params.py">params</a>) -> <a href="./src/openai/types/eval_create_response.py">EvalCreateResponse</a></code>
- <code title="get /evals/{eval_id}">client.evals.<a href="./src/openai/resources/evals/evals.py">retrieve</a>(eval_id) -> <a href="./src/openai/types/eval_retrieve_response.py">EvalRetrieveResponse</a></code>
- <code title="post /evals/{eval_id}">client.evals.<a href="./src/openai/resources/evals/evals.py">update</a>(eval_id, \*\*<a href="src/openai/types/eval_update_params.py">params</a>) -> <a href="./src/openai/types/eval_update_response.py">EvalUpdateResponse</a></code>
- <code title="get /evals">client.evals.<a href="./src/openai/resources/evals/evals.py">list</a>(\*\*<a href="src/openai/types/eval_list_params.py">params</a>) -> <a href="./src/openai/types/eval_list_response.py">SyncCursorPage[EvalListResponse]</a></code>
- <code title="delete /evals/{eval_id}">client.evals.<a href="./src/openai/resources/evals/evals.py">delete</a>(eval_id) -> <a href="./src/openai/types/eval_delete_response.py">EvalDeleteResponse</a></code>

## Runs

Types:

```python
from openai.types.evals import (
    CreateEvalCompletionsRunDataSource,
    CreateEvalJSONLRunDataSource,
    EvalAPIError,
    RunCreateResponse,
    RunRetrieveResponse,
    RunListResponse,
    RunDeleteResponse,
    RunCancelResponse,
)
```

Methods:

- <code title="post /evals/{eval_id}/runs">client.evals.runs.<a href="./src/openai/resources/evals/runs/runs.py">create</a>(eval_id, \*\*<a href="src/openai/types/evals/run_create_params.py">params</a>) -> <a href="./src/openai/types/evals/run_create_response.py">RunCreateResponse</a></code>
- <code title="get /evals/{eval_id}/runs/{run_id}">client.evals.runs.<a href="./src/openai/resources/evals/runs/runs.py">retrieve</a>(run_id, \*, eval_id) -> <a href="./src/openai/types/evals/run_retrieve_response.py">RunRetrieveResponse</a></code>
- <code title="get /evals/{eval_id}/runs">client.evals.runs.<a href="./src/openai/resources/evals/runs/runs.py">list</a>(eval_id, \*\*<a href="src/openai/types/evals/run_list_params.py">params</a>) -> <a href="./src/openai/types/evals/run_list_response.py">SyncCursorPage[RunListResponse]</a></code>
- <code title="delete /evals/{eval_id}/runs/{run_id}">client.evals.runs.<a href="./src/openai/resources/evals/runs/runs.py">delete</a>(run_id, \*, eval_id) -> <a href="./src/openai/types/evals/run_delete_response.py">RunDeleteResponse</a></code>
- <code title="post /evals/{eval_id}/runs/{run_id}">client.evals.runs.<a href="./src/openai/resources/evals/runs/runs.py">cancel</a>(run_id, \*, eval_id) -> <a href="./src/openai/types/evals/run_cancel_response.py">RunCancelResponse</a></code>

### OutputItems

Types:

```python
from openai.types.evals.runs import OutputItemRetrieveResponse, OutputItemListResponse
```

Methods:

- <code title="get /evals/{eval_id}/runs/{run_id}/output_items/{output_item_id}">client.evals.runs.output_items.<a href="./src/openai/resources/evals/runs/output_items.py">retrieve</a>(output_item_id, \*, eval_id, run_id) -> <a href="./src/openai/types/evals/runs/output_item_retrieve_response.py">OutputItemRetrieveResponse</a></code>
- <code title="get /evals/{eval_id}/runs/{run_id}/output_items">client.evals.runs.output_items.<a href="./src/openai/resources/evals/runs/output_items.py">list</a>(run_id, \*, eval_id, \*\*<a href="src/openai/types/evals/runs/output_item_list_params.py">params</a>) -> <a href="./src/openai/types/evals/runs/output_item_list_response.py">SyncCursorPage[OutputItemListResponse]</a></code>
