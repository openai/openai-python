# Completions

Types:

```python
from openai.types import Completion, CompletionChoice, CompletionUsage
```

Methods:

- <code title="post /completions">client.completions.<a href="./src/openai/resources/completions.py">create</a>(\*\*<a href="src/openai/types/completion_create_params.py">params</a>) -> <a href="./src/openai/types/completion.py">Completion</a></code>

# Chat

## Completions

Types:

```python
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionRole,
)
```

Methods:

- <code title="post /chat/completions">client.chat.completions.<a href="./src/openai/resources/chat/completions.py">create</a>(\*\*<a href="src/openai/types/chat/completion_create_params.py">params</a>) -> <a href="./src/openai/types/chat/chat_completion.py">ChatCompletion</a></code>

# Edits

Types:

```python
from openai.types import Edit
```

Methods:

- <code title="post /edits">client.edits.<a href="./src/openai/resources/edits.py">create</a>(\*\*<a href="src/openai/types/edit_create_params.py">params</a>) -> <a href="./src/openai/types/edit.py">Edit</a></code>

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
- <code title="get /files">client.files.<a href="./src/openai/resources/files.py">list</a>() -> <a href="./src/openai/types/file_object.py">SyncPage[FileObject]</a></code>
- <code title="delete /files/{file_id}">client.files.<a href="./src/openai/resources/files.py">delete</a>(file_id) -> <a href="./src/openai/types/file_deleted.py">FileDeleted</a></code>
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
from openai.types.fine_tuning import FineTuningJob, FineTuningJobEvent
```

Methods:

- <code title="post /fine_tuning/jobs">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs.py">create</a>(\*\*<a href="src/openai/types/fine_tuning/job_create_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>
- <code title="get /fine_tuning/jobs/{fine_tuning_job_id}">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs.py">retrieve</a>(fine_tuning_job_id) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>
- <code title="get /fine_tuning/jobs">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs.py">list</a>(\*\*<a href="src/openai/types/fine_tuning/job_list_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">SyncCursorPage[FineTuningJob]</a></code>
- <code title="post /fine_tuning/jobs/{fine_tuning_job_id}/cancel">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs.py">cancel</a>(fine_tuning_job_id) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job.py">FineTuningJob</a></code>
- <code title="get /fine_tuning/jobs/{fine_tuning_job_id}/events">client.fine_tuning.jobs.<a href="./src/openai/resources/fine_tuning/jobs.py">list_events</a>(fine_tuning_job_id, \*\*<a href="src/openai/types/fine_tuning/job_list_events_params.py">params</a>) -> <a href="./src/openai/types/fine_tuning/fine_tuning_job_event.py">SyncCursorPage[FineTuningJobEvent]</a></code>

# FineTunes

Types:

```python
from openai.types import FineTune, FineTuneEvent, FineTuneEventsListResponse
```

Methods:

- <code title="post /fine-tunes">client.fine_tunes.<a href="./src/openai/resources/fine_tunes.py">create</a>(\*\*<a href="src/openai/types/fine_tune_create_params.py">params</a>) -> <a href="./src/openai/types/fine_tune.py">FineTune</a></code>
- <code title="get /fine-tunes/{fine_tune_id}">client.fine_tunes.<a href="./src/openai/resources/fine_tunes.py">retrieve</a>(fine_tune_id) -> <a href="./src/openai/types/fine_tune.py">FineTune</a></code>
- <code title="get /fine-tunes">client.fine_tunes.<a href="./src/openai/resources/fine_tunes.py">list</a>() -> <a href="./src/openai/types/fine_tune.py">SyncPage[FineTune]</a></code>
- <code title="post /fine-tunes/{fine_tune_id}/cancel">client.fine_tunes.<a href="./src/openai/resources/fine_tunes.py">cancel</a>(fine_tune_id) -> <a href="./src/openai/types/fine_tune.py">FineTune</a></code>
- <code title="get /fine-tunes/{fine_tune_id}/events">client.fine_tunes.<a href="./src/openai/resources/fine_tunes.py">list_events</a>(fine_tune_id, \*\*<a href="src/openai/types/fine_tune_list_events_params.py">params</a>) -> <a href="./src/openai/types/fine_tune_events_list_response.py">FineTuneEventsListResponse</a></code>
