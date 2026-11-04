# Polling runtime preparation

This additive step prepares the vector-store runtime used by the separately reviewed
Castiron polling helpers. Public resource facades stay unchanged. It does not enable
new generator configuration or claim a reduction in mixed generated/handwritten files.
The baseline is public openai-python commit
`2d58e828cfda3f6ffe7b9f9b2f9f7305dbdb028a`.

## Runtime boundary

`src/openai/lib/_vector_stores.py` gains synchronous and asynchronous counterparts for:

- `create_and_poll_vector_store_file`
- `upload_vector_store_file`
- `upload_and_poll_vector_store_file`
- `create_and_poll_vector_store_file_batch`
- `upload_and_poll_vector_store_file_batch`

Their signatures and bodies preserve the released facade behavior. The internal first
parameter is the resource instance. Calls through resource methods remain overrideable;
caller streams, attributes, request options, return objects, and raised errors retain
their existing ownership and identity. Existing IDs precede uploaded IDs. The sync
executor still waits for submitted work before propagating errors. Asyncio retains
`gather` behavior; Trio retains nursery cancellation. No new validation, upload limits,
transport, credentials, runtime dependency, or Python-version requirement is added.

## Verification and follow-up

`tests/lib/test_vector_store_runtime.py` runs the same contracts against the released
facades and the extracted functions. Coverage includes all ten signatures, existing
file polling deadlines, forwarding and override hooks, upload ownership, concurrency
limits, ordering, failures, cancellation, and unsupported runtimes. Batch upload tests
exercise both asyncio and Trio. Only tests bind the extracted functions to resource
classes in this preparatory change.

After the preceding upload/Agent/Beta/Live generated SDK candidate is established,
land this runtime preparation through SDK CODEOWNER review and green CI. Then generate
a separate candidate enabling these seven reviewed method configuration paths:

- `/resources/files/methods/retrieve/python_polling_helper`
- `/resources/vector_stores/subresources/files/methods/create/python_polling_helper`
- `/resources/vector_stores/subresources/files/methods/retrieve/python_polling_helper`
- `/resources/vector_stores/subresources/file_batches/methods/create/python_polling_helper`
- `/resources/vector_stores/subresources/file_batches/methods/retrieve/python_polling_helper`
- `/resources/videos/methods/create/python_polling_helper`
- `/resources/videos/methods/retrieve/python_polling_helper`

Use immutable compiler/API/config inputs and the normal Castiron private checkpoint
workflow. Preserve all public signatures, overloads, positional arguments, defaults,
decorators, and return types. Re-run runtime parity and existing file/video/vector-store
contracts against that generated candidate. Measure remaining custom patch lines using
its real generation snapshot before updating the transition inventory. Public promotion
must follow normal review and CI; do not mask patch accounting or copy generated changes
into a public checkout independently of their checkpoint.
