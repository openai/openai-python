# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import typing as _t
import importlib as _importlib

if _t.TYPE_CHECKING:
    from . import (
        beta as beta,
        chat as chat,
        admin as admin,
        audio as audio,
        batch as batch,
        evals as evals,
        image as image,
        model as model,
        skill as skill,
        video as video,
        shared as shared,
        skills as skills,
        upload as upload,
        graders as graders,
        uploads as uploads,
        realtime as realtime,
        webhooks as webhooks,
        embedding as embedding,
        responses as responses,
        chat_model as chat_model,
        completion as completion,
        containers as containers,
        moderation as moderation,
        skill_list as skill_list,
        video_size as video_size,
        audio_model as audio_model,
        batch_error as batch_error,
        batch_usage as batch_usage,
        file_object as file_object,
        fine_tuning as fine_tuning,
        image_model as image_model,
        video_model as video_model,
        file_content as file_content,
        file_deleted as file_deleted,
        file_purpose as file_purpose,
        vector_store as vector_store,
        conversations as conversations,
        deleted_skill as deleted_skill,
        model_deleted as model_deleted,
        shared_params as shared_params,
        vector_stores as vector_stores,
        video_seconds as video_seconds,
        embedding_model as embedding_model,
        images_response as images_response,
        completion_usage as completion_usage,
        eval_list_params as eval_list_params,
        file_list_params as file_list_params,
        moderation_model as moderation_model,
        batch_list_params as batch_list_params,
        completion_choice as completion_choice,
        image_edit_params as image_edit_params,
        skill_list_params as skill_list_params,
        video_edit_params as video_edit_params,
        video_list_params as video_list_params,
        video_model_param as video_model_param,
        eval_create_params as eval_create_params,
        eval_list_response as eval_list_response,
        eval_update_params as eval_update_params,
        file_create_params as file_create_params,
        video_create_error as video_create_error,
        video_remix_params as video_remix_params,
        batch_create_params as batch_create_params,
        skill_create_params as skill_create_params,
        skill_update_params as skill_update_params,
        video_create_params as video_create_params,
        video_extend_params as video_extend_params,
        batch_request_counts as batch_request_counts,
        eval_create_response as eval_create_response,
        eval_delete_response as eval_delete_response,
        eval_update_response as eval_update_response,
        upload_create_params as upload_create_params,
        vector_store_deleted as vector_store_deleted,
        audio_response_format as audio_response_format,
        container_list_params as container_list_params,
        image_generate_params as image_generate_params,
        video_delete_response as video_delete_response,
        eval_retrieve_response as eval_retrieve_response,
        file_chunking_strategy as file_chunking_strategy,
        image_gen_stream_event as image_gen_stream_event,
        upload_complete_params as upload_complete_params,
        websocket_reconnection as websocket_reconnection,
        container_create_params as container_create_params,
        container_list_response as container_list_response,
        embedding_create_params as embedding_create_params,
        image_edit_stream_event as image_edit_stream_event,
        completion_create_params as completion_create_params,
        content_provenance_check as content_provenance_check,
        moderation_create_params as moderation_create_params,
        vector_store_list_params as vector_store_list_params,
        container_create_response as container_create_response,
        create_embedding_response as create_embedding_response,
        image_gen_completed_event as image_gen_completed_event,
        image_edit_completed_event as image_edit_completed_event,
        moderation_create_response as moderation_create_response,
        vector_store_create_params as vector_store_create_params,
        vector_store_search_params as vector_store_search_params,
        vector_store_update_params as vector_store_update_params,
        container_retrieve_response as container_retrieve_response,
        image_input_reference_param as image_input_reference_param,
        moderation_text_input_param as moderation_text_input_param,
        file_chunking_strategy_param as file_chunking_strategy_param,
        vector_store_search_response as vector_store_search_response,
        video_get_character_response as video_get_character_response,
        websocket_connection_options as websocket_connection_options,
        image_create_variation_params as image_create_variation_params,
        image_gen_partial_image_event as image_gen_partial_image_event,
        static_file_chunking_strategy as static_file_chunking_strategy,
        video_create_character_params as video_create_character_params,
        video_download_content_params as video_download_content_params,
        eval_custom_data_source_config as eval_custom_data_source_config,
        image_edit_partial_image_event as image_edit_partial_image_event,
        video_create_character_response as video_create_character_response,
        moderation_image_url_input_param as moderation_image_url_input_param,
        auto_file_chunking_strategy_param as auto_file_chunking_strategy_param,
        moderation_multi_modal_input_param as moderation_multi_modal_input_param,
        other_file_chunking_strategy_object as other_file_chunking_strategy_object,
        static_file_chunking_strategy_param as static_file_chunking_strategy_param,
        static_file_chunking_strategy_object as static_file_chunking_strategy_object,
        content_provenance_check_create_params as content_provenance_check_create_params,
        eval_stored_completions_data_source_config as eval_stored_completions_data_source_config,
        static_file_chunking_strategy_object_param as static_file_chunking_strategy_object_param,
    )
    from .batch import Batch as Batch
    from .image import Image as Image
    from .model import Model as Model
    from .skill import Skill as Skill
    from .video import Video as Video
    from .shared import (
        Metadata as Metadata,
        AllModels as AllModels,
        ChatModel as ChatModel,
        Reasoning as Reasoning,
        ErrorObject as ErrorObject,
        CompoundFilter as CompoundFilter,
        OAuthErrorCode as OAuthErrorCode,
        ResponsesModel as ResponsesModel,
        ReasoningEffort as ReasoningEffort,
        ComparisonFilter as ComparisonFilter,
        FunctionDefinition as FunctionDefinition,
        FunctionParameters as FunctionParameters,
        ResponseFormatText as ResponseFormatText,
        CustomToolInputFormat as CustomToolInputFormat,
        ResponseFormatJSONObject as ResponseFormatJSONObject,
        ResponseFormatJSONSchema as ResponseFormatJSONSchema,
        ResponseFormatTextPython as ResponseFormatTextPython,
        ResponseFormatTextGrammar as ResponseFormatTextGrammar,
    )
    from .upload import Upload as Upload
    from .embedding import Embedding as Embedding
    from .chat_model import ChatModel as ChatModel
    from .completion import Completion as Completion
    from .moderation import Moderation as Moderation
    from .skill_list import SkillList as SkillList
    from .video_size import VideoSize as VideoSize
    from .audio_model import AudioModel as AudioModel
    from .batch_error import BatchError as BatchError
    from .batch_usage import BatchUsage as BatchUsage
    from .file_object import FileObject as FileObject
    from .image_model import ImageModel as ImageModel
    from .video_model import VideoModel as VideoModel
    from .file_content import FileContent as FileContent
    from .file_deleted import FileDeleted as FileDeleted
    from .file_purpose import FilePurpose as FilePurpose
    from .vector_store import VectorStore as VectorStore
    from .deleted_skill import DeletedSkill as DeletedSkill
    from .model_deleted import ModelDeleted as ModelDeleted
    from .video_seconds import VideoSeconds as VideoSeconds
    from .embedding_model import EmbeddingModel as EmbeddingModel
    from .images_response import ImagesResponse as ImagesResponse
    from .completion_usage import CompletionUsage as CompletionUsage
    from .eval_list_params import EvalListParams as EvalListParams
    from .file_list_params import FileListParams as FileListParams
    from .moderation_model import ModerationModel as ModerationModel
    from .batch_list_params import BatchListParams as BatchListParams
    from .completion_choice import CompletionChoice as CompletionChoice
    from .image_edit_params import ImageEditParams as ImageEditParams
    from .skill_list_params import SkillListParams as SkillListParams
    from .video_edit_params import VideoEditParams as VideoEditParams
    from .video_list_params import VideoListParams as VideoListParams
    from .video_model_param import VideoModelParam as VideoModelParam
    from .eval_create_params import EvalCreateParams as EvalCreateParams
    from .eval_list_response import EvalListResponse as EvalListResponse
    from .eval_update_params import EvalUpdateParams as EvalUpdateParams
    from .file_create_params import FileCreateParams as FileCreateParams
    from .video_create_error import VideoCreateError as VideoCreateError
    from .video_remix_params import VideoRemixParams as VideoRemixParams
    from .batch_create_params import BatchCreateParams as BatchCreateParams
    from .skill_create_params import SkillCreateParams as SkillCreateParams
    from .skill_update_params import SkillUpdateParams as SkillUpdateParams
    from .video_create_params import VideoCreateParams as VideoCreateParams
    from .video_extend_params import VideoExtendParams as VideoExtendParams
    from .batch_request_counts import BatchRequestCounts as BatchRequestCounts
    from .eval_create_response import EvalCreateResponse as EvalCreateResponse
    from .eval_delete_response import EvalDeleteResponse as EvalDeleteResponse
    from .eval_update_response import EvalUpdateResponse as EvalUpdateResponse
    from .upload_create_params import UploadCreateParams as UploadCreateParams
    from .vector_store_deleted import VectorStoreDeleted as VectorStoreDeleted
    from .audio_response_format import AudioResponseFormat as AudioResponseFormat
    from .container_list_params import ContainerListParams as ContainerListParams
    from .image_generate_params import ImageGenerateParams as ImageGenerateParams
    from .video_delete_response import VideoDeleteResponse as VideoDeleteResponse
    from .eval_retrieve_response import EvalRetrieveResponse as EvalRetrieveResponse
    from .file_chunking_strategy import FileChunkingStrategy as FileChunkingStrategy
    from .image_gen_stream_event import ImageGenStreamEvent as ImageGenStreamEvent
    from .upload_complete_params import UploadCompleteParams as UploadCompleteParams
    from .websocket_reconnection import (
        ReconnectingEvent as ReconnectingEvent,
        ReconnectingOverrides as ReconnectingOverrides,
    )
    from .container_create_params import ContainerCreateParams as ContainerCreateParams
    from .container_list_response import ContainerListResponse as ContainerListResponse
    from .embedding_create_params import EmbeddingCreateParams as EmbeddingCreateParams
    from .image_edit_stream_event import ImageEditStreamEvent as ImageEditStreamEvent
    from .completion_create_params import CompletionCreateParams as CompletionCreateParams
    from .content_provenance_check import ContentProvenanceCheck as ContentProvenanceCheck
    from .moderation_create_params import ModerationCreateParams as ModerationCreateParams
    from .vector_store_list_params import VectorStoreListParams as VectorStoreListParams
    from .container_create_response import ContainerCreateResponse as ContainerCreateResponse
    from .create_embedding_response import CreateEmbeddingResponse as CreateEmbeddingResponse
    from .image_gen_completed_event import ImageGenCompletedEvent as ImageGenCompletedEvent
    from .image_edit_completed_event import ImageEditCompletedEvent as ImageEditCompletedEvent
    from .moderation_create_response import ModerationCreateResponse as ModerationCreateResponse
    from .vector_store_create_params import VectorStoreCreateParams as VectorStoreCreateParams
    from .vector_store_search_params import VectorStoreSearchParams as VectorStoreSearchParams
    from .vector_store_update_params import VectorStoreUpdateParams as VectorStoreUpdateParams
    from .container_retrieve_response import ContainerRetrieveResponse as ContainerRetrieveResponse
    from .image_input_reference_param import ImageInputReferenceParam as ImageInputReferenceParam
    from .moderation_text_input_param import ModerationTextInputParam as ModerationTextInputParam
    from .file_chunking_strategy_param import FileChunkingStrategyParam as FileChunkingStrategyParam
    from .vector_store_search_response import VectorStoreSearchResponse as VectorStoreSearchResponse
    from .video_get_character_response import VideoGetCharacterResponse as VideoGetCharacterResponse
    from .websocket_connection_options import (
        WebSocketConnectionOptions as WebSocketConnectionOptions,
        WebsocketConnectionOptions as WebsocketConnectionOptions,
    )
    from .image_create_variation_params import ImageCreateVariationParams as ImageCreateVariationParams
    from .image_gen_partial_image_event import ImageGenPartialImageEvent as ImageGenPartialImageEvent
    from .static_file_chunking_strategy import StaticFileChunkingStrategy as StaticFileChunkingStrategy
    from .video_create_character_params import VideoCreateCharacterParams as VideoCreateCharacterParams
    from .video_download_content_params import VideoDownloadContentParams as VideoDownloadContentParams
    from .eval_custom_data_source_config import EvalCustomDataSourceConfig as EvalCustomDataSourceConfig
    from .image_edit_partial_image_event import ImageEditPartialImageEvent as ImageEditPartialImageEvent
    from .video_create_character_response import VideoCreateCharacterResponse as VideoCreateCharacterResponse
    from .moderation_image_url_input_param import ModerationImageURLInputParam as ModerationImageURLInputParam
    from .auto_file_chunking_strategy_param import AutoFileChunkingStrategyParam as AutoFileChunkingStrategyParam
    from .moderation_multi_modal_input_param import ModerationMultiModalInputParam as ModerationMultiModalInputParam
    from .other_file_chunking_strategy_object import OtherFileChunkingStrategyObject as OtherFileChunkingStrategyObject
    from .static_file_chunking_strategy_param import StaticFileChunkingStrategyParam as StaticFileChunkingStrategyParam
    from .static_file_chunking_strategy_object import (
        StaticFileChunkingStrategyObject as StaticFileChunkingStrategyObject,
    )
    from .content_provenance_check_create_params import (
        ContentProvenanceCheckCreateParams as ContentProvenanceCheckCreateParams,
    )
    from .eval_stored_completions_data_source_config import (
        EvalStoredCompletionsDataSourceConfig as EvalStoredCompletionsDataSourceConfig,
    )
    from .static_file_chunking_strategy_object_param import (
        StaticFileChunkingStrategyObjectParam as StaticFileChunkingStrategyObjectParam,
    )

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "Batch": (".batch", "Batch"),
    "Image": (".image", "Image"),
    "Model": (".model", "Model"),
    "Skill": (".skill", "Skill"),
    "Video": (".video", "Video"),
    "Metadata": (".shared", "Metadata"),
    "AllModels": (".shared", "AllModels"),
    "ChatModel": (".shared", "ChatModel"),
    "Reasoning": (".shared", "Reasoning"),
    "ErrorObject": (".shared", "ErrorObject"),
    "CompoundFilter": (".shared", "CompoundFilter"),
    "OAuthErrorCode": (".shared", "OAuthErrorCode"),
    "ResponsesModel": (".shared", "ResponsesModel"),
    "ReasoningEffort": (".shared", "ReasoningEffort"),
    "ComparisonFilter": (".shared", "ComparisonFilter"),
    "FunctionDefinition": (".shared", "FunctionDefinition"),
    "FunctionParameters": (".shared", "FunctionParameters"),
    "ResponseFormatText": (".shared", "ResponseFormatText"),
    "CustomToolInputFormat": (".shared", "CustomToolInputFormat"),
    "ResponseFormatJSONObject": (".shared", "ResponseFormatJSONObject"),
    "ResponseFormatJSONSchema": (".shared", "ResponseFormatJSONSchema"),
    "ResponseFormatTextPython": (".shared", "ResponseFormatTextPython"),
    "ResponseFormatTextGrammar": (".shared", "ResponseFormatTextGrammar"),
    "Upload": (".upload", "Upload"),
    "Embedding": (".embedding", "Embedding"),
    "Completion": (".completion", "Completion"),
    "Moderation": (".moderation", "Moderation"),
    "SkillList": (".skill_list", "SkillList"),
    "VideoSize": (".video_size", "VideoSize"),
    "AudioModel": (".audio_model", "AudioModel"),
    "BatchError": (".batch_error", "BatchError"),
    "BatchUsage": (".batch_usage", "BatchUsage"),
    "FileObject": (".file_object", "FileObject"),
    "ImageModel": (".image_model", "ImageModel"),
    "VideoModel": (".video_model", "VideoModel"),
    "FileContent": (".file_content", "FileContent"),
    "FileDeleted": (".file_deleted", "FileDeleted"),
    "FilePurpose": (".file_purpose", "FilePurpose"),
    "VectorStore": (".vector_store", "VectorStore"),
    "DeletedSkill": (".deleted_skill", "DeletedSkill"),
    "ModelDeleted": (".model_deleted", "ModelDeleted"),
    "VideoSeconds": (".video_seconds", "VideoSeconds"),
    "EmbeddingModel": (".embedding_model", "EmbeddingModel"),
    "ImagesResponse": (".images_response", "ImagesResponse"),
    "CompletionUsage": (".completion_usage", "CompletionUsage"),
    "EvalListParams": (".eval_list_params", "EvalListParams"),
    "FileListParams": (".file_list_params", "FileListParams"),
    "ModerationModel": (".moderation_model", "ModerationModel"),
    "BatchListParams": (".batch_list_params", "BatchListParams"),
    "CompletionChoice": (".completion_choice", "CompletionChoice"),
    "ImageEditParams": (".image_edit_params", "ImageEditParams"),
    "SkillListParams": (".skill_list_params", "SkillListParams"),
    "VideoEditParams": (".video_edit_params", "VideoEditParams"),
    "VideoListParams": (".video_list_params", "VideoListParams"),
    "VideoModelParam": (".video_model_param", "VideoModelParam"),
    "EvalCreateParams": (".eval_create_params", "EvalCreateParams"),
    "EvalListResponse": (".eval_list_response", "EvalListResponse"),
    "EvalUpdateParams": (".eval_update_params", "EvalUpdateParams"),
    "FileCreateParams": (".file_create_params", "FileCreateParams"),
    "VideoCreateError": (".video_create_error", "VideoCreateError"),
    "VideoRemixParams": (".video_remix_params", "VideoRemixParams"),
    "BatchCreateParams": (".batch_create_params", "BatchCreateParams"),
    "SkillCreateParams": (".skill_create_params", "SkillCreateParams"),
    "SkillUpdateParams": (".skill_update_params", "SkillUpdateParams"),
    "VideoCreateParams": (".video_create_params", "VideoCreateParams"),
    "VideoExtendParams": (".video_extend_params", "VideoExtendParams"),
    "BatchRequestCounts": (".batch_request_counts", "BatchRequestCounts"),
    "EvalCreateResponse": (".eval_create_response", "EvalCreateResponse"),
    "EvalDeleteResponse": (".eval_delete_response", "EvalDeleteResponse"),
    "EvalUpdateResponse": (".eval_update_response", "EvalUpdateResponse"),
    "UploadCreateParams": (".upload_create_params", "UploadCreateParams"),
    "VectorStoreDeleted": (".vector_store_deleted", "VectorStoreDeleted"),
    "AudioResponseFormat": (".audio_response_format", "AudioResponseFormat"),
    "ContainerListParams": (".container_list_params", "ContainerListParams"),
    "ImageGenerateParams": (".image_generate_params", "ImageGenerateParams"),
    "VideoDeleteResponse": (".video_delete_response", "VideoDeleteResponse"),
    "EvalRetrieveResponse": (".eval_retrieve_response", "EvalRetrieveResponse"),
    "FileChunkingStrategy": (".file_chunking_strategy", "FileChunkingStrategy"),
    "ImageGenStreamEvent": (".image_gen_stream_event", "ImageGenStreamEvent"),
    "UploadCompleteParams": (".upload_complete_params", "UploadCompleteParams"),
    "ReconnectingEvent": (".websocket_reconnection", "ReconnectingEvent"),
    "ReconnectingOverrides": (".websocket_reconnection", "ReconnectingOverrides"),
    "ContainerCreateParams": (".container_create_params", "ContainerCreateParams"),
    "ContainerListResponse": (".container_list_response", "ContainerListResponse"),
    "EmbeddingCreateParams": (".embedding_create_params", "EmbeddingCreateParams"),
    "ImageEditStreamEvent": (".image_edit_stream_event", "ImageEditStreamEvent"),
    "CompletionCreateParams": (".completion_create_params", "CompletionCreateParams"),
    "ContentProvenanceCheck": (".content_provenance_check", "ContentProvenanceCheck"),
    "ModerationCreateParams": (".moderation_create_params", "ModerationCreateParams"),
    "VectorStoreListParams": (".vector_store_list_params", "VectorStoreListParams"),
    "ContainerCreateResponse": (".container_create_response", "ContainerCreateResponse"),
    "CreateEmbeddingResponse": (".create_embedding_response", "CreateEmbeddingResponse"),
    "ImageGenCompletedEvent": (".image_gen_completed_event", "ImageGenCompletedEvent"),
    "ImageEditCompletedEvent": (".image_edit_completed_event", "ImageEditCompletedEvent"),
    "ModerationCreateResponse": (".moderation_create_response", "ModerationCreateResponse"),
    "VectorStoreCreateParams": (".vector_store_create_params", "VectorStoreCreateParams"),
    "VectorStoreSearchParams": (".vector_store_search_params", "VectorStoreSearchParams"),
    "VectorStoreUpdateParams": (".vector_store_update_params", "VectorStoreUpdateParams"),
    "ContainerRetrieveResponse": (".container_retrieve_response", "ContainerRetrieveResponse"),
    "ImageInputReferenceParam": (".image_input_reference_param", "ImageInputReferenceParam"),
    "ModerationTextInputParam": (".moderation_text_input_param", "ModerationTextInputParam"),
    "FileChunkingStrategyParam": (".file_chunking_strategy_param", "FileChunkingStrategyParam"),
    "VectorStoreSearchResponse": (".vector_store_search_response", "VectorStoreSearchResponse"),
    "VideoGetCharacterResponse": (".video_get_character_response", "VideoGetCharacterResponse"),
    "WebSocketConnectionOptions": (".websocket_connection_options", "WebSocketConnectionOptions"),
    "WebsocketConnectionOptions": (".websocket_connection_options", "WebsocketConnectionOptions"),
    "ImageCreateVariationParams": (".image_create_variation_params", "ImageCreateVariationParams"),
    "ImageGenPartialImageEvent": (".image_gen_partial_image_event", "ImageGenPartialImageEvent"),
    "StaticFileChunkingStrategy": (".static_file_chunking_strategy", "StaticFileChunkingStrategy"),
    "VideoCreateCharacterParams": (".video_create_character_params", "VideoCreateCharacterParams"),
    "VideoDownloadContentParams": (".video_download_content_params", "VideoDownloadContentParams"),
    "EvalCustomDataSourceConfig": (".eval_custom_data_source_config", "EvalCustomDataSourceConfig"),
    "ImageEditPartialImageEvent": (".image_edit_partial_image_event", "ImageEditPartialImageEvent"),
    "VideoCreateCharacterResponse": (".video_create_character_response", "VideoCreateCharacterResponse"),
    "ModerationImageURLInputParam": (".moderation_image_url_input_param", "ModerationImageURLInputParam"),
    "AutoFileChunkingStrategyParam": (".auto_file_chunking_strategy_param", "AutoFileChunkingStrategyParam"),
    "ModerationMultiModalInputParam": (".moderation_multi_modal_input_param", "ModerationMultiModalInputParam"),
    "OtherFileChunkingStrategyObject": (".other_file_chunking_strategy_object", "OtherFileChunkingStrategyObject"),
    "StaticFileChunkingStrategyParam": (".static_file_chunking_strategy_param", "StaticFileChunkingStrategyParam"),
    "StaticFileChunkingStrategyObject": (".static_file_chunking_strategy_object", "StaticFileChunkingStrategyObject"),
    "ContentProvenanceCheckCreateParams": (
        ".content_provenance_check_create_params",
        "ContentProvenanceCheckCreateParams",
    ),
    "EvalStoredCompletionsDataSourceConfig": (
        ".eval_stored_completions_data_source_config",
        "EvalStoredCompletionsDataSourceConfig",
    ),
    "StaticFileChunkingStrategyObjectParam": (
        ".static_file_chunking_strategy_object_param",
        "StaticFileChunkingStrategyObjectParam",
    ),
}

__all__ = [
    "AllModels",
    "AudioModel",
    "AudioResponseFormat",
    "AutoFileChunkingStrategyParam",
    "Batch",
    "BatchCreateParams",
    "BatchError",
    "BatchListParams",
    "BatchRequestCounts",
    "BatchUsage",
    "ChatModel",
    "ComparisonFilter",
    "Completion",
    "CompletionChoice",
    "CompletionCreateParams",
    "CompletionUsage",
    "CompoundFilter",
    "ContainerCreateParams",
    "ContainerCreateResponse",
    "ContainerListParams",
    "ContainerListResponse",
    "ContainerRetrieveResponse",
    "ContentProvenanceCheck",
    "ContentProvenanceCheckCreateParams",
    "CreateEmbeddingResponse",
    "CustomToolInputFormat",
    "DeletedSkill",
    "Embedding",
    "EmbeddingCreateParams",
    "EmbeddingModel",
    "ErrorObject",
    "EvalCreateParams",
    "EvalCreateResponse",
    "EvalCustomDataSourceConfig",
    "EvalDeleteResponse",
    "EvalListParams",
    "EvalListResponse",
    "EvalRetrieveResponse",
    "EvalStoredCompletionsDataSourceConfig",
    "EvalUpdateParams",
    "EvalUpdateResponse",
    "FileChunkingStrategy",
    "FileChunkingStrategyParam",
    "FileContent",
    "FileCreateParams",
    "FileDeleted",
    "FileListParams",
    "FileObject",
    "FilePurpose",
    "FunctionDefinition",
    "FunctionParameters",
    "Image",
    "ImageCreateVariationParams",
    "ImageEditCompletedEvent",
    "ImageEditParams",
    "ImageEditPartialImageEvent",
    "ImageEditStreamEvent",
    "ImageGenCompletedEvent",
    "ImageGenPartialImageEvent",
    "ImageGenStreamEvent",
    "ImageGenerateParams",
    "ImageInputReferenceParam",
    "ImageModel",
    "ImagesResponse",
    "Metadata",
    "Model",
    "ModelDeleted",
    "Moderation",
    "ModerationCreateParams",
    "ModerationCreateResponse",
    "ModerationImageURLInputParam",
    "ModerationModel",
    "ModerationMultiModalInputParam",
    "ModerationTextInputParam",
    "OAuthErrorCode",
    "OtherFileChunkingStrategyObject",
    "Reasoning",
    "ReasoningEffort",
    "ReconnectingEvent",
    "ReconnectingOverrides",
    "ResponseFormatJSONObject",
    "ResponseFormatJSONSchema",
    "ResponseFormatText",
    "ResponseFormatTextGrammar",
    "ResponseFormatTextPython",
    "ResponsesModel",
    "Skill",
    "SkillCreateParams",
    "SkillList",
    "SkillListParams",
    "SkillUpdateParams",
    "StaticFileChunkingStrategy",
    "StaticFileChunkingStrategyObject",
    "StaticFileChunkingStrategyObjectParam",
    "StaticFileChunkingStrategyParam",
    "Upload",
    "UploadCompleteParams",
    "UploadCreateParams",
    "VectorStore",
    "VectorStoreCreateParams",
    "VectorStoreDeleted",
    "VectorStoreListParams",
    "VectorStoreSearchParams",
    "VectorStoreSearchResponse",
    "VectorStoreUpdateParams",
    "Video",
    "VideoCreateCharacterParams",
    "VideoCreateCharacterResponse",
    "VideoCreateError",
    "VideoCreateParams",
    "VideoDeleteResponse",
    "VideoDownloadContentParams",
    "VideoEditParams",
    "VideoExtendParams",
    "VideoGetCharacterResponse",
    "VideoListParams",
    "VideoModel",
    "VideoModelParam",
    "VideoRemixParams",
    "VideoSeconds",
    "VideoSize",
    "WebSocketConnectionOptions",
    "WebsocketConnectionOptions",
    "admin",
    "audio",
    "audio_model",
    "audio_response_format",
    "auto_file_chunking_strategy_param",
    "batch",
    "batch_create_params",
    "batch_error",
    "batch_list_params",
    "batch_request_counts",
    "batch_usage",
    "beta",
    "chat",
    "chat_model",
    "completion",
    "completion_choice",
    "completion_create_params",
    "completion_usage",
    "container_create_params",
    "container_create_response",
    "container_list_params",
    "container_list_response",
    "container_retrieve_response",
    "containers",
    "content_provenance_check",
    "content_provenance_check_create_params",
    "conversations",
    "create_embedding_response",
    "deleted_skill",
    "embedding",
    "embedding_create_params",
    "embedding_model",
    "eval_create_params",
    "eval_create_response",
    "eval_custom_data_source_config",
    "eval_delete_response",
    "eval_list_params",
    "eval_list_response",
    "eval_retrieve_response",
    "eval_stored_completions_data_source_config",
    "eval_update_params",
    "eval_update_response",
    "evals",
    "file_chunking_strategy",
    "file_chunking_strategy_param",
    "file_content",
    "file_create_params",
    "file_deleted",
    "file_list_params",
    "file_object",
    "file_purpose",
    "fine_tuning",
    "graders",
    "image",
    "image_create_variation_params",
    "image_edit_completed_event",
    "image_edit_params",
    "image_edit_partial_image_event",
    "image_edit_stream_event",
    "image_gen_completed_event",
    "image_gen_partial_image_event",
    "image_gen_stream_event",
    "image_generate_params",
    "image_input_reference_param",
    "image_model",
    "images_response",
    "model",
    "model_deleted",
    "moderation",
    "moderation_create_params",
    "moderation_create_response",
    "moderation_image_url_input_param",
    "moderation_model",
    "moderation_multi_modal_input_param",
    "moderation_text_input_param",
    "other_file_chunking_strategy_object",
    "realtime",
    "responses",
    "shared",
    "shared_params",
    "skill",
    "skill_create_params",
    "skill_list",
    "skill_list_params",
    "skill_update_params",
    "skills",
    "static_file_chunking_strategy",
    "static_file_chunking_strategy_object",
    "static_file_chunking_strategy_object_param",
    "static_file_chunking_strategy_param",
    "upload",
    "upload_complete_params",
    "upload_create_params",
    "uploads",
    "vector_store",
    "vector_store_create_params",
    "vector_store_deleted",
    "vector_store_list_params",
    "vector_store_search_params",
    "vector_store_search_response",
    "vector_store_update_params",
    "vector_stores",
    "video",
    "video_create_character_params",
    "video_create_character_response",
    "video_create_error",
    "video_create_params",
    "video_delete_response",
    "video_download_content_params",
    "video_edit_params",
    "video_extend_params",
    "video_get_character_response",
    "video_list_params",
    "video_model",
    "video_model_param",
    "video_remix_params",
    "video_seconds",
    "video_size",
    "webhooks",
    "websocket_connection_options",
    "websocket_reconnection",
]


def __getattr__(name: str) -> object:
    if name in _LAZY_EXPORTS:
        module_name, attr_name = _LAZY_EXPORTS[name]
        module = _importlib.import_module(module_name, package=__package__)
        val = getattr(module, attr_name)
        globals()[name] = val
        return val
    try:
        module = _importlib.import_module(f".{name}", package=__package__)
        globals()[name] = module
        return module
    except ModuleNotFoundError:
        pass
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(list(globals().keys()) + list(__all__)))
