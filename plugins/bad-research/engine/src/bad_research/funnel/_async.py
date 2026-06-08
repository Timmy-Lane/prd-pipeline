"""acall — the sync/async reconciliation seam (Plan 07 post-review note).

The seams this funnel composes are SYNCHRONOUS in production:
  - Plan 03 WebSearchProvider.search_ex(q) -> list[WebResult]   (blocking httpx)
  - Plan 04 fetch_tiered(url, *, tier_max, ...) -> WebResult     (asyncio.run-wrapped browse)

The funnel runs them concurrently, so it must NOT `await` them directly
(`await sync_fn()` raises TypeError). It also must work against the async test
fakes. `acall` bridges both: await the result of a coroutine function, otherwise
offload the blocking call to a worker thread so it never stalls the event loop.

Route EVERY seam call (search_ex, fetch_tiered) through this helper.
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable
from typing import Any


async def acall(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Await fn if it's a coroutine function; otherwise run the blocking call in
    a worker thread (asyncio.to_thread)."""
    if inspect.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    return await asyncio.to_thread(fn, *args, **kwargs)
