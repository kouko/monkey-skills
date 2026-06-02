"""Asyncio concurrency helpers mirroring Workflow-engine primitives.

gather_bounded  — parallel() semantics: run thunks under a Semaphore cap;
                  exceptions swallowed to None, order preserved.
pipeline        — pipeline() semantics: each item flows through stages in
                  series; a stage that raises drops the item to None and
                  skips remaining stages.  Items run concurrently under a
                  Semaphore cap.
"""
from __future__ import annotations

import asyncio
from typing import Any, Callable


async def gather_bounded(
    thunks: list[Callable[[], Any]],
    concurrency: int = 8,
) -> list[Any]:
    """Run zero-arg coroutine factories concurrently, bounded by *concurrency*.

    Each thunk is called to produce a coroutine.  If that coroutine raises,
    the slot resolves to ``None``.  Results are returned in the same order as
    *thunks*.
    """
    sem = asyncio.Semaphore(concurrency)
    results: list[Any] = [None] * len(thunks)

    async def run(index: int, thunk: Callable[[], Any]) -> None:
        async with sem:
            try:
                results[index] = await thunk()
            except Exception:
                results[index] = None

    await asyncio.gather(*(run(i, t) for i, t in enumerate(thunks)))
    return results


async def pipeline(
    items: list[Any],
    *stages: Callable[[Any], Any],
    concurrency: int = 8,
) -> list[Any]:
    """Pass each item through *stages* in series, items run concurrently.

    For each item:
    - ``await stage1(item)`` → feed result to ``stage2``, etc.
    - If a stage raises, the item becomes ``None`` and remaining stages
      are skipped.

    If no stages are provided, items are returned unchanged.
    Results are returned in the same order as *items*.
    """
    if not stages:
        return list(items)

    sem = asyncio.Semaphore(concurrency)
    results: list[Any] = list(items)  # initial values (overwritten below)

    async def run_item(index: int, value: Any) -> None:
        async with sem:
            current = value
            for stage in stages:
                try:
                    current = await stage(current)
                except Exception:
                    current = None
                    break
            results[index] = current

    await asyncio.gather(*(run_item(i, v) for i, v in enumerate(items)))
    return results
