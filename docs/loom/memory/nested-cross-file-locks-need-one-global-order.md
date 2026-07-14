---
name: nested-cross-file-locks-need-one-global-order
description: When one function HOLDS lock A while acquiring lock B (nested cross-file/cross-store locks), it is deadlock-free ONLY if every code path acquires them in the same global order — no path may take them B-then-A. Sequential use (release A, THEN acquire B) is not nesting and never deadlocks; prefer it, and when you must nest, prove the global order by checking every sibling that touches both locks.
type: practice
origin: 2026-07-14 session — investing-toolkit analysis-kpi slice 3 (kpi_schema.confirm holds the schema-file lock while adjudicating through review_queue's queue-file lock); verified in code review
---

The operational-kpi `analysis-kpi` skill has three file-per-key durable stores,
each with its own `fcntl.flock` per file (kpi-store series, review-queue,
kpi-schema). `kpi_schema.confirm` acquires the SCHEMA-file lock and, while
holding it, calls `review_queue.adjudicate` which acquires the QUEUE-file lock
— a NESTED lock (schema→queue). Nesting two different locks is where classic
lock-ordering deadlock lives: if any other path acquires them queue→schema, two
concurrent callers can each hold one and wait forever for the other.

**Why:** flock is a real OS lock; a consistent GLOBAL acquisition order is the
standard (and only simple) way to guarantee no cycle. The safe cases are easy to
miss: `propose`/`amend` also touch both stores but they RELEASE the schema lock
in `finally` BEFORE calling `review_queue.enqueue` (sequential, not nested), so
they never hold both — that is why the branch is deadlock-free even though three
functions touch two locks.

**How to apply:** prefer SEQUENTIAL lock use — finish (and release) store-A's
locked read-modify-write, then do store-B's — which cannot deadlock. When you
genuinely must NEST (hold A across a B-locking call, e.g. to keep an
adjudicate-then-flip atomic under one lock), pick ONE global order and, before
shipping, grep every function that touches EITHER lock and confirm none acquires
them in the reverse order. State the chosen order in the docstring so the next
editor preserves it. Related: [[assertion-must-encode-the-property-it-claims]]
(a deadlock-freedom claim should be backed by the enumerated no-reverse-path
check, not assumed).
