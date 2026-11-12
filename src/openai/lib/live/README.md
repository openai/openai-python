# Live WebSocket lifecycle

`client.live.connect()` and `client.live.forks.connect(session_id=...)` leave
startup to the caller: send `connection.session.start(...)` and wait for
`session.started`. A sideband connection created by
`client.live.sideband.connect(session_id=...)` attaches to an existing session.
It does not send a start or require a new `session.started`; an attachment's
short replay is not a complete session snapshot.

Direct `recv()` and `recv_bytes()` calls report transport errors to their
caller. Iterator reconnection is available only when an `on_reconnecting`
callback was explicitly supplied. The callback controls retry and can update
credentials or query parameters. A new socket is not proof that the previous
Live session, recording, or application state was restored. Applications own
their recovery decision and any necessary startup or state reconstruction.
Don't use multiple physical readers: a dispatcher owns the read loop while it
runs. Detaching or closing one transcript grouper doesn't cancel another
observer or the connection.

All modes preserve the manager's caller-configured `max_queue_size`, including
if the queue was empty at connection time. Only messages that haven't been
attempted on a socket remain eligible for flushing after a retry. A direct send
exception is raised to its caller and cannot prove the server didn't receive
that message. A failure while flushing an already queued message still logs a
warning, as before; it cannot be raised at the original queueing call. Neither
failed attempt is automatically retried. Unattempted pre-open messages and
messages explicitly queued during recovery remain in order within their
existing budget. No automatic session reopening or restoration is implied.

Treat each wire error as an event to handle, not as a successful session result.
In particular, preserve `session_storage_failed` if `session.closed` follows;
the close doesn't mean that recording storage succeeded. Unknown events and
fields are preserved for callers that need them.
