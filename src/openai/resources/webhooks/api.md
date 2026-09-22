# Webhooks

Types:

```python
from openai.types.webhooks import (
    BatchCancelledWebhookEvent,
    BatchCompletedWebhookEvent,
    BatchExpiredWebhookEvent,
    BatchFailedWebhookEvent,
    DeletedWebhookEndpoint,
    EvalRunCanceledWebhookEvent,
    EvalRunFailedWebhookEvent,
    EvalRunSucceededWebhookEvent,
    FineTuningJobCancelledWebhookEvent,
    FineTuningJobFailedWebhookEvent,
    FineTuningJobSucceededWebhookEvent,
    LiveCallIncomingWebhookEvent,
    LiveTransportIncomingWebhookEvent,
    RealtimeCallIncomingWebhookEvent,
    ResponseCancelledWebhookEvent,
    ResponseCompletedWebhookEvent,
    ResponseFailedWebhookEvent,
    ResponseIncompleteWebhookEvent,
    SafetyAlertCreatedWebhookEvent,
    SafetyDeactivationIssuedWebhookEvent,
    SafetyOrgAlertCreatedWebhookEvent,
    SafetyWarningIssuedWebhookEvent,
    UnwrapWebhookEvent,
    WebhookEndpoint,
    WebhookEndpointList,
    WebhookEndpointTestResult,
    WebhookEndpointWithSecret,
    WebhookEventTypeList,
)
```

Methods:

- <code title="post /webhook_endpoints">client.webhooks.<a href="./src/openai/resources/webhooks/webhooks.py">create</a>(\*\*<a href="src/openai/types/webhooks/webhook_create_params.py">params</a>) -> <a href="./src/openai/types/webhooks/webhook_endpoint_with_secret.py">WebhookEndpointWithSecret</a></code>
- <code title="get /webhook_endpoints/{webhook_endpoint_id}">client.webhooks.<a href="./src/openai/resources/webhooks/webhooks.py">retrieve</a>(webhook_endpoint_id) -> <a href="./src/openai/types/webhooks/webhook_endpoint.py">WebhookEndpoint</a></code>
- <code title="post /webhook_endpoints/{webhook_endpoint_id}">client.webhooks.<a href="./src/openai/resources/webhooks/webhooks.py">update</a>(webhook_endpoint_id, \*\*<a href="src/openai/types/webhooks/webhook_update_params.py">params</a>) -> <a href="./src/openai/types/webhooks/webhook_endpoint.py">WebhookEndpoint</a></code>
- <code title="get /webhook_endpoints">client.webhooks.<a href="./src/openai/resources/webhooks/webhooks.py">list</a>(\*\*<a href="src/openai/types/webhooks/webhook_list_params.py">params</a>) -> <a href="./src/openai/types/webhooks/webhook_endpoint.py">SyncCursorPage[WebhookEndpoint]</a></code>
- <code title="delete /webhook_endpoints/{webhook_endpoint_id}">client.webhooks.<a href="./src/openai/resources/webhooks/webhooks.py">delete</a>(webhook_endpoint_id) -> <a href="./src/openai/types/webhooks/deleted_webhook_endpoint.py">DeletedWebhookEndpoint</a></code>
- <code title="post /webhook_endpoints/{webhook_endpoint_id}/rotate_secret">client.webhooks.<a href="./src/openai/resources/webhooks/webhooks.py">rotate_secret</a>(webhook_endpoint_id, \*\*<a href="src/openai/types/webhooks/webhook_rotate_secret_params.py">params</a>) -> <a href="./src/openai/types/webhooks/webhook_endpoint_with_secret.py">WebhookEndpointWithSecret</a></code>
- <code title="post /webhook_endpoints/{webhook_endpoint_id}/test">client.webhooks.<a href="./src/openai/resources/webhooks/webhooks.py">test</a>(webhook_endpoint_id, \*\*<a href="src/openai/types/webhooks/webhook_test_params.py">params</a>) -> <a href="./src/openai/types/webhooks/webhook_endpoint_test_result.py">WebhookEndpointTestResult</a></code>

## EventTypes

Methods:

- <code title="get /webhook_event_types">client.webhooks.event_types.<a href="./src/openai/resources/webhooks/event_types.py">list</a>() -> <a href="./src/openai/types/webhooks/webhook_event_type_list.py">WebhookEventTypeList</a></code>
