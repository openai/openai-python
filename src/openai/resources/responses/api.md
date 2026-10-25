# Responses

Types:

```python
from openai.types.responses import (
    ApplyPatchTool,
    CompactedResponse,
    ComputerAction,
    ComputerActionList,
    ComputerTool,
    ComputerUsePreviewTool,
    ContainerAuto,
    ContainerNetworkPolicyAllowlist,
    ContainerNetworkPolicyDisabled,
    ContainerNetworkPolicyDomainSecret,
    ContainerReference,
    CustomTool,
    EasyInputMessage,
    FileSearchTool,
    FunctionShellTool,
    FunctionTool,
    ImageDetail,
    InlineSkill,
    InlineSkillSource,
    LocalEnvironment,
    LocalSkill,
    McpToolCallError,
    NamespaceTool,
    Response,
    ResponseApplyPatchToolCall,
    ResponseApplyPatchToolCallOutput,
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
    ResponseCompactionCompactingEvent,
    ResponseCompactionItem,
    ResponseCompactionItemParam,
    ResponseCompletedEvent,
    ResponseComputerToolCall,
    ResponseComputerToolCallOutputItem,
    ResponseComputerToolCallOutputScreenshot,
    ResponseConfigurationUpdateItem,
    ResponseConfigurationUpdateItemParam,
    ResponseContainerReference,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseConversationParam,
    ResponseCreatedEvent,
    ResponseCustomToolCall,
    ResponseCustomToolCallInputDeltaEvent,
    ResponseCustomToolCallInputDoneEvent,
    ResponseCustomToolCallItem,
    ResponseCustomToolCallOutput,
    ResponseCustomToolCallOutputItem,
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
    ResponseFunctionCallOutputItem,
    ResponseFunctionCallOutputItemList,
    ResponseFunctionShellCallOutputContent,
    ResponseFunctionShellToolCall,
    ResponseFunctionShellToolCallOutput,
    ResponseFunctionToolCall,
    ResponseFunctionToolCallItem,
    ResponseFunctionToolCallOutputItem,
    ResponseFunctionWebSearch,
    ResponseImageGenCallCompletedEvent,
    ResponseImageGenCallGeneratingEvent,
    ResponseImageGenCallInProgressEvent,
    ResponseImageGenCallPartialImageEvent,
    ResponseInProgressEvent,
    ResponseIncludable,
    ResponseIncompleteEvent,
    ResponseInput,
    ResponseInputAudio,
    ResponseInputContent,
    ResponseInputFile,
    ResponseInputFileContent,
    ResponseInputImage,
    ResponseInputImageContent,
    ResponseInputItem,
    ResponseInputMessageContentList,
    ResponseInputMessageItem,
    ResponseInputText,
    ResponseInputTextContent,
    ResponseItem,
    ResponseLocalEnvironment,
    ResponseMcpCallArgumentsDeltaEvent,
    ResponseMcpCallArgumentsDoneEvent,
    ResponseMcpCallCompletedEvent,
    ResponseMcpCallFailedEvent,
    ResponseMcpCallInProgressEvent,
    ResponseMcpListToolsCompletedEvent,
    ResponseMcpListToolsFailedEvent,
    ResponseMcpListToolsInProgressEvent,
    ResponseOutputItem,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseOutputMessage,
    ResponseOutputRefusal,
    ResponseOutputText,
    ResponseOutputTextAnnotationAddedEvent,
    ResponsePrompt,
    ResponseQueuedEvent,
    ResponseReasoningItem,
    ResponseReasoningSummaryPartAddedEvent,
    ResponseReasoningSummaryPartDoneEvent,
    ResponseReasoningSummaryTextDeltaEvent,
    ResponseReasoningSummaryTextDoneEvent,
    ResponseReasoningTextDeltaEvent,
    ResponseReasoningTextDoneEvent,
    ResponseRefusalDeltaEvent,
    ResponseRefusalDoneEvent,
    ResponseShellCallCommandAddedEvent,
    ResponseShellCallCommandDeltaEvent,
    ResponseShellCallCommandDoneEvent,
    ResponseShellCallOutputContentDeltaEvent,
    ResponseShellCallOutputContentDoneEvent,
    ResponseStatus,
    ResponseSteerAcceptedEvent,
    ResponseSteerErrorCode,
    ResponseSteerEvent,
    ResponseSteerFailedEvent,
    ResponseSteerInput,
    ResponseSteerInputContent,
    ResponseSteerPendingEvent,
    ResponseSteerPendingReason,
    ResponseSteerRequiredInput,
    ResponseStreamEvent,
    ResponseTextConfig,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
    ResponseToolSearchCall,
    ResponseToolSearchOutputItem,
    ResponseToolSearchOutputItemParam,
    ResponseUsage,
    ResponseWebSearchCallCompletedEvent,
    ResponseWebSearchCallInProgressEvent,
    ResponseWebSearchCallSearchingEvent,
    ResponsesClientEvent,
    ResponsesServerEvent,
    ServiceTier,
    SkillReference,
    Tool,
    ToolChoiceAllowed,
    ToolChoiceApplyPatch,
    ToolChoiceCustom,
    ToolChoiceFunction,
    ToolChoiceMcp,
    ToolChoiceOptions,
    ToolChoiceShell,
    ToolChoiceTypes,
    ToolSearchOutputNamespaceTool,
    ToolSearchTool,
    WebSearchPreviewTool,
    WebSearchTool,
)
```

Methods:

- <code title="post /responses">client.responses.<a href="./src/openai/resources/responses/responses.py">create</a>(\*\*<a href="src/openai/types/responses/response_create_params.py">params</a>) -> <a href="./src/openai/types/responses/response.py">Response</a></code>
- <code title="get /responses/{response_id}">client.responses.<a href="./src/openai/resources/responses/responses.py">retrieve</a>(response_id, \*\*<a href="src/openai/types/responses/response_retrieve_params.py">params</a>) -> <a href="./src/openai/types/responses/response.py">Response</a></code>
- <code title="delete /responses/{response_id}">client.responses.<a href="./src/openai/resources/responses/responses.py">delete</a>(response_id) -> None</code>
- <code title="post /responses/{response_id}/cancel">client.responses.<a href="./src/openai/resources/responses/responses.py">cancel</a>(response_id) -> <a href="./src/openai/types/responses/response.py">Response</a></code>
- <code title="post /responses/compact">client.responses.<a href="./src/openai/resources/responses/responses.py">compact</a>(\*\*<a href="src/openai/types/responses/response_compact_params.py">params</a>) -> <a href="./src/openai/types/responses/compacted_response.py">CompactedResponse</a></code>
- <code>client.responses.<a href="responses.py">parse</a>(\*, text_format=..., access_programs=..., background=..., context_management=..., conversation=..., include=..., input=..., instructions=..., max_output_tokens=..., max_tool_calls=..., metadata=..., model=..., moderation=..., parallel_tool_calls=..., previous_response_id=..., prompt=..., prompt_cache_key=..., prompt_cache_options=..., prompt_cache_retention=..., reasoning=..., safety_identifier=..., service_tier=..., store=..., stream=..., stream_options=..., temperature=..., text=..., tool_choice=..., tools=..., top_logprobs=..., top_p=..., truncation=..., user=..., verbosity=..., extra_headers=..., extra_query=..., extra_body=..., timeout=...) -> ParsedResponse[TextFormatT]</code>
- <code>client.responses.<a href="responses.py">stream</a>(\*, response_id=..., input=..., model=..., access_programs=..., background=..., context_management=..., text_format=..., tools=..., conversation=..., include=..., instructions=..., max_output_tokens=..., max_tool_calls=..., metadata=..., parallel_tool_calls=..., moderation=..., previous_response_id=..., prompt=..., prompt_cache_key=..., prompt_cache_options=..., prompt_cache_retention=..., reasoning=..., safety_identifier=..., service_tier=..., store=..., stream_options=..., temperature=..., text=..., tool_choice=..., top_logprobs=..., top_p=..., truncation=..., user=..., starting_after=..., extra_headers=..., extra_query=..., extra_body=..., timeout=...) -> ResponseStreamManager[TextFormatT]</code>

## InputItems

Types:

```python
from openai.types.responses import ResponseItemList
```

Methods:

- <code title="get /responses/{response_id}/input_items">client.responses.input_items.<a href="./src/openai/resources/responses/input_items.py">list</a>(response_id, \*\*<a href="src/openai/types/responses/input_item_list_params.py">params</a>) -> <a href="./src/openai/types/responses/response_item.py">SyncCursorPage[ResponseItem]</a></code>

## InputTokens

Types:

```python
from openai.types.responses import InputTokenCountResponse
```

Methods:

- <code title="post /responses/input_tokens">client.responses.input_tokens.<a href="./src/openai/resources/responses/input_tokens.py">count</a>(\*\*<a href="src/openai/types/responses/input_token_count_params.py">params</a>) -> <a href="./src/openai/types/responses/input_token_count_response.py">InputTokenCountResponse</a></code>
