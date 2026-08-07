---
name: a-shared-index-file-is-regenerated-from-entries-never-hand-merged
description: Committed index files that mirror many entry files (BACKLOG.md, the memory store's §Index) are a structural source of rebase/merge conflicts — resolve by REGENERATING from the entry files with the store's generator, never by hand-picking conflict hunks; hand-merging reintroduces exactly the drift the generator exists to prevent
type: process
origin: US-quarterly arc PR #665 (two live rebase-conflict incidents on shared indexes, 2026-08-07) + loom arc 3 (memory §Index generation shipped, same date)
---

A committed index that is a projection of many entry files conflicts
whenever two branches each add or edit entries: both sides rewrite
neighboring lines of the same generated block. Resolving such a conflict
by picking hunks re-creates the exact class of drift (missing lines,
stale descriptions, wrong order) that the index's validator exists to
catch — and it does so at the moment of least attention, mid-rebase.

**Why:** the index is derived state. Merging derived state by hand is
merging the OUTPUT of a function instead of its inputs; the entry files
merge cleanly (different files), so the only conflicted artifact is one
nobody should be editing by hand at all.

**How to apply:** on any conflict in a generated index file, take either
side wholesale (or delete the section), finish the rebase/merge of the
ENTRY files, then run the store's generator and stage the result —
`python3 scripts/backlog_index.py --write` for docs/loom/BACKLOG.md,
`python3 scripts/check_loom_memory_integrity.py --write` for
docs/loom/memory/README.md's §Index — and re-run the matching validator
before committing.
