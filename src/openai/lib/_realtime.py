from __future__ import annotations

# Compatibility aliases for the former handwritten call-creation implementation.
# Multipart and raw SDP serialization now come from the generated resources.
from openai.resources.realtime.calls import Calls as _Calls, AsyncCalls as _AsyncCalls

__all__ = ["_Calls", "_AsyncCalls"]
