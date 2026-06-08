"""Shared Server-Sent-Events helper: run a worker that emits events, stream them."""
from __future__ import annotations

import json
import queue
import threading
from collections.abc import Callable

from fastapi.responses import StreamingResponse

_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"}


def sse_response(work: Callable[[Callable[[dict], None]], None]) -> StreamingResponse:
    """`work(emit)` runs in a daemon thread; call emit(event_dict) to stream events.
    A `None` sentinel ends the stream. Exceptions become an error event."""
    q: "queue.Queue" = queue.Queue()

    def runner() -> None:
        try:
            work(lambda ev: q.put(ev))
        except Exception as exc:  # noqa: BLE001 — surface to the stream
            q.put({"type": "error", "detail": str(exc)})
        finally:
            q.put(None)

    threading.Thread(target=runner, daemon=True).start()

    def gen():
        yield "retry: 3000\n\n"
        while True:
            ev = q.get()
            if ev is None:
                break
            yield f"data: {json.dumps(ev)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream", headers=_HEADERS)
