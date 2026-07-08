---
name: per-task-review-misses-duplicated-fallback-fix
description: A defensive fix at one call site of a shared dict-shape contract can PASS individual per-task review while sibling call sites of the same contract stay unfixed — only whole-branch cross-task-coherence review catches the gap
type: gotcha
origin: deep-deep-research bake-off round-2 bugfixes branch (2026-07-08)
---

In `research-toolkit:deep-deep-research`, a claim dict's source-URL field
had no schema-enforced key name. Fixing the resulting KeyError crash in
one reader (`prompts.py`'s `verify_prompt()`) with
`claim.get("sourceUrl") or claim.get("url", "")` individually PASSed both
spec-reviewer and code-quality-reviewer, because each was correctly
scoped to that one file's diff. But the same claim dicts flow onward
into three more call sites in a sibling file (`synthesis.py`), which
still read the bare, unfallbacked key — so a `url`-keyed claim now
survived the (fixed) crash but silently lost its URL one stage later.
Only the whole-branch review's `cross-task-coherence` dimension, which
reads the diff across all tasks together, surfaced it.

**Why:** per-task/per-module review is deliberately narrow-scoped —
that is what makes it fast and precise — so it structurally cannot see
that a data shape it just patched flows through files outside its own
diff. This is the same systemic risk as
[[cross-module-field-contracts-execute-probes]], observed here without
any build-assembly step: any shared dict/object shape read at multiple
call sites is a candidate, not just build-concatenated modules.

**How to apply:** when a fix changes how a shared data shape is *read*
(adds a fallback, tolerates a missing/renamed key, relaxes a type
check), grep the whole repo/package for other read-sites of the same
field before declaring the task done — don't rely on per-task review
scope to catch it. At minimum, never skip the whole-branch review step
just because every individual task already PASSed; that step's unique
value is exactly this class of gap.
