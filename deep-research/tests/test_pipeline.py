"""Tests for pipeline.py asyncio helpers.

RED: gather_bounded and pipeline do not exist yet — these tests must fail.
"""
import asyncio
import pytest

from deep_research.pipeline import gather_bounded, pipeline


async def _ok(value):
    return value * 2


async def _fail():
    raise ValueError("boom")


async def _stage_add(x):
    return x + 10


async def _stage_mul(x):
    return x * 3


async def _stage_raise(x):
    raise RuntimeError("stage-error")


class TestGatherBounded:
    async def test_results_match_input_order(self):
        thunks = [lambda v=i: _ok(v) for i in range(5)]
        results = await gather_bounded(thunks, concurrency=3)
        assert results == [0, 2, 4, 6, 8]

    async def test_failing_thunk_resolves_to_none(self):
        thunks = [
            lambda: _ok(1),
            lambda: _fail(),
            lambda: _ok(3),
        ]
        results = await gather_bounded(thunks)
        assert results == [2, None, 6]

    async def test_concurrency_cap_respected(self):
        """At most `concurrency` coroutines run simultaneously."""
        running = 0
        peak = 0

        async def slow():
            nonlocal running, peak
            running += 1
            peak = max(peak, running)
            await asyncio.sleep(0)
            running -= 1
            return 1

        thunks = [slow for _ in range(10)]
        await gather_bounded(thunks, concurrency=4)
        assert peak <= 4

    async def test_empty_input(self):
        assert await gather_bounded([]) == []


class TestPipeline:
    async def test_two_stage_transforms(self):
        items = [1, 2, 3]
        # stage1: +10  stage2: *3  =>  [33, 36, 39]
        results = await pipeline(items, _stage_add, _stage_mul)
        assert results == [33, 36, 39]

    async def test_failing_stage_drops_item_to_none(self):
        items = [1, 2, 3]
        # stage1 raises for all items
        results = await pipeline(items, _stage_raise, _stage_mul)
        assert results == [None, None, None]

    async def test_partial_failure_preserves_others(self):
        call_count = 0

        async def maybe_fail(x):
            nonlocal call_count
            call_count += 1
            if x == 2:
                raise ValueError("drop me")
            return x + 10

        async def double(x):
            return x * 2

        items = [1, 2, 3]
        results = await pipeline(items, maybe_fail, double)
        # item 2 drops; remaining get +10 then *2
        assert results == [22, None, 26]
        # stage2 must NOT be called for item 2 (already dropped)
        assert call_count == 3  # stage1 called for all 3

    async def test_results_match_input_order(self):
        items = list(range(10))
        results = await pipeline(items, _stage_add)
        assert results == [i + 10 for i in range(10)]

    async def test_empty_items(self):
        assert await pipeline([], _stage_add) == []

    async def test_no_stages(self):
        items = [1, 2, 3]
        results = await pipeline(items)
        assert results == [1, 2, 3]
