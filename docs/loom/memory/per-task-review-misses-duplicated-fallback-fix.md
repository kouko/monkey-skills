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

**Second occurrence (2026-07-08, same session, loom-code branch
`loom-code-mechanical-sync-script-category`):** the same shape recurred
in pure documentation. A change extended `plan-format.md`'s
`Review-weight: mechanical` exemption with a new example category, but
`plan-document-reviewer-prompt.md`'s Check 16 — the downstream consumer
that validates whether a plan's use of that exemption is legitimate —
was left untouched. Check 16's literal wording ("gives no concrete
exact-spec quote" as a failure trigger) would have rejected the very
worked example the change shipped as its own positive case. Whole-branch
review caught it again. Generalizes the "How to apply" rule beyond code
read-sites: a documentation section's *promise* (what qualifies for X)
has downstream *consumers* (checks/rules that enforce the promise) just
like a data shape has read-sites — grep for both before declaring a
doc-only change complete, not just for code call-sites.
