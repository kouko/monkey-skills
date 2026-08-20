---
name: 2026-07-31-cache-util-load-cache-breaks-its-never-raises-contract
description: cache_util.load_cache breaks its own "Never raises" contract on a non-mapping payload
status: open
origin: Task B's round-2 code-quality review (branch `feat-us-quarterly-statement-series`, 2026-07-31), found by probing shapes the new raw-filing cache's own six recovery rows do not cover.
start: next touch of `cache_util.py`, or the first report of a cache entry that will not self-heal. Cheap enough to ride along with any unrelated edit to that file.
---

- Start: next touch of `cache_util.py`, or the first report of a cache entry
  that will not self-heal. Cheap enough to ride along with any unrelated edit
  to that file.
- Origin: Task B's round-2 code-quality review (branch
  `feat-us-quarterly-statement-series`, 2026-07-31), found by probing shapes
  the new raw-filing cache's own six recovery rows do not cover.
- The defect: `load_cache`'s docstring promises "Never raises"
  (`cache_util.py:186`), but `out = dict(envelope.get("data", {}))`
  (`cache_util.py:218`) raises when `data` is valid JSON that is not a mapping
  — measured: a string, a list, a number and null each raise `ValueError` or
  `TypeError` out of the function. **Verified 2026-07-31 by opening both lines.**
- Why it matters beyond one caller: every cache consumer relies on that
  fail-open contract, and the raw-filing cache added in Task B has NO TTL — so
  an entry in this shape never self-heals and never expires. It is permanent.
- Why it is not urgent: `save_cache` writes atomically (tmp + rename), so a
  torn write yields invalid JSON, which IS covered (that path returns None and
  refetches). Reaching this shape needs a hand-edit or a foreign writer.
- Fix shape: wrap the `dict(...)` in the same `except (TypeError, ValueError):
  return None` the function already uses for its timestamp parse — the
  fail-open behaviour the docstring already promises. One line, no new policy.
- NOT introduced by Task B, which relied on the documented contract in good
  faith; recorded here rather than widening that branch's scope.
