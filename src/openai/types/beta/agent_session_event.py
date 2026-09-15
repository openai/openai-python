# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .agent_session_idle_event import AgentSessionIdleEvent
from .agent_session_error_event import AgentSessionErrorEvent
from .agent_session_failed_event import AgentSessionFailedEvent
from .agent_session_created_event import AgentSessionCreatedEvent
from .agent_session_in_progress_event import AgentSessionInProgressEvent
from .agent_session_turn_failed_event import AgentSessionTurnFailedEvent
from .agent_session_turn_created_event import AgentSessionTurnCreatedEvent
from .agent_session_turn_cancelled_event import AgentSessionTurnCancelledEvent
from .agent_session_turn_completed_event import AgentSessionTurnCompletedEvent
from .agent_session_turn_item_done_event import AgentSessionTurnItemDoneEvent
from .agent_session_requires_action_event import AgentSessionRequiresActionEvent
from .agent_session_subagent_active_event import AgentSessionSubagentActiveEvent
from .agent_session_subagent_closed_event import AgentSessionSubagentClosedEvent
from .agent_session_turn_item_added_event import AgentSessionTurnItemAddedEvent
from .agent_session_subagent_created_event import AgentSessionSubagentCreatedEvent
from .agent_session_turn_in_progress_event import AgentSessionTurnInProgressEvent
from .agent_session_environment_ready_event import AgentSessionEnvironmentReadyEvent
from .agent_session_environment_failed_event import AgentSessionEnvironmentFailedEvent
from .agent_session_environment_pending_event import AgentSessionEnvironmentPendingEvent
from .agent_session_environment_connected_event import AgentSessionEnvironmentConnectedEvent
from .agent_session_turn_output_text_done_event import AgentSessionTurnOutputTextDoneEvent
from .agent_session_turn_content_part_done_event import AgentSessionTurnContentPartDoneEvent
from .agent_session_turn_output_text_delta_event import AgentSessionTurnOutputTextDeltaEvent
from .agent_session_turn_content_part_added_event import AgentSessionTurnContentPartAddedEvent
from .agent_session_environment_disconnected_event import AgentSessionEnvironmentDisconnectedEvent
from .agent_output_command_execution_output_delta_event import AgentOutputCommandExecutionOutputDeltaEvent
from .agent_session_turn_reasoning_summary_part_done_event import AgentSessionTurnReasoningSummaryPartDoneEvent
from .agent_session_turn_reasoning_summary_text_done_event import AgentSessionTurnReasoningSummaryTextDoneEvent
from .agent_session_turn_reasoning_summary_part_added_event import AgentSessionTurnReasoningSummaryPartAddedEvent
from .agent_session_turn_reasoning_summary_text_delta_event import AgentSessionTurnReasoningSummaryTextDeltaEvent

__all__ = ["AgentSessionEvent"]

AgentSessionEvent: TypeAlias = Annotated[
    Union[
        AgentSessionErrorEvent,
        AgentSessionEnvironmentReadyEvent,
        AgentOutputCommandExecutionOutputDeltaEvent,
        AgentSessionCreatedEvent,
        AgentSessionTurnCreatedEvent,
        AgentSessionTurnInProgressEvent,
        AgentSessionTurnCompletedEvent,
        AgentSessionTurnFailedEvent,
        AgentSessionTurnCancelledEvent,
        AgentSessionTurnItemAddedEvent,
        AgentSessionIdleEvent,
        AgentSessionInProgressEvent,
        AgentSessionRequiresActionEvent,
        AgentSessionFailedEvent,
        AgentSessionEnvironmentPendingEvent,
        AgentSessionEnvironmentConnectedEvent,
        AgentSessionEnvironmentDisconnectedEvent,
        AgentSessionEnvironmentFailedEvent,
        AgentSessionSubagentCreatedEvent,
        AgentSessionSubagentActiveEvent,
        AgentSessionSubagentClosedEvent,
        AgentSessionTurnItemDoneEvent,
        AgentSessionTurnContentPartAddedEvent,
        AgentSessionTurnContentPartDoneEvent,
        AgentSessionTurnOutputTextDeltaEvent,
        AgentSessionTurnOutputTextDoneEvent,
        AgentSessionTurnReasoningSummaryPartAddedEvent,
        AgentSessionTurnReasoningSummaryPartDoneEvent,
        AgentSessionTurnReasoningSummaryTextDeltaEvent,
        AgentSessionTurnReasoningSummaryTextDoneEvent,
    ],
    PropertyInfo(discriminator="type"),
]
