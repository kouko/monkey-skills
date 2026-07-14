---
name: durable-store-mirrors-cache-util-not-imports-it
description: A new durable/append-only store in an analysis skill must NOT reuse data-markets' cache_util — resolve_cache_dir returns the EVICTABLE cache dir (wrong for irreplaceable history: root under XDG_DATA_HOME instead) and a direct cross-skill import breaches the analysis↔data-markets layer boundary (the repo pattern is subprocess, not import); mirror the sanitize + atomic-write PATTERN in self-contained helpers.
type: practice
origin: 2026-07-14 session — investing-toolkit analysis-kpi slice 1 (bitemporal KPI store); caught in brainstorming grounding + whole-branch review
---

When adding a NEW persistence layer to an `analysis-*` skill in investing-toolkit,
the instinct is to reuse `data-markets/scripts/cache_util.py` (it already owns
dir-resolution + key-sanitization + atomic writes). For a DURABLE store
(append-only series, bitemporal history) that instinct is wrong on two counts:

1. **`resolve_cache_dir()` returns the CACHE dir** (`~/.cache`, XDG_CACHE_HOME) —
   designed to be evicted. A bitemporal / append-only store holds irreplaceable
   history that must survive cache eviction, so it must root under the DATA dir
   (`~/.local/share`, `XDG_DATA_HOME`) instead. Reusing the cache resolver would
   put history somewhere built to be cleared.
2. **A direct `import cache_util` from an analysis skill breaches the layer
   boundary.** `grep` confirms `import cache_util` appears ONLY within
   data-markets (same-dir clients); analysis skills reach data-markets by
   **subprocess** (e.g. `analysis-comps/scripts/etf_aggregator.py` subprocesses
   `pack.py`), never by importing its modules across the skill boundary.

**Why:** cache-vs-data-dir is a durability contract, not a cosmetic path choice —
a cleared cache silently drops the series; and cross-skill import is how the
data(I/O)↔analysis(compute) layer split erodes into coupling.

**How to apply:** for a durable store in an analysis skill, write self-contained
helpers that MIRROR cache_util's `_UNSAFE_KEY_CHARS` sanitization (path-escape
defense) + atomic tmp+rename write, rooted under an `XDG_DATA_HOME` ladder with
an env override for tests — do NOT `import cache_util` and do NOT reuse its TTL
cache envelope (a durable series never expires). Flag the small duplication as a
Rule-of-Three candidate (extract a shared module only when a THIRD durable store
appears). Related: [[fixtures-mirror-producer-shape]], [[shared-classifier-over-open-dialects-needs-allowlist]].
