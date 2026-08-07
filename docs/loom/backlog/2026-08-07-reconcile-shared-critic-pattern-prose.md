---
name: 2026-08-07-reconcile-shared-critic-pattern-prose
description: The two sanctioned co-writer critics restate the writer-vs-judge pattern in ~500 words of parallel but diverging prose
status: PARKED
origin: 2026-08-07 family complexity audit (docs/loom/audits/2026-08-07-family-complexity-audit.md, item C3)
start: the next semantic change to the sanctioned co-writer critic pattern (any change that must land in both critics)
---

loom-interface-design:design-critic and loom-spec:completeness-critic
share the sanctioned co-writer pattern (provenance-tagged additions,
two-valued verdict, writer≠judge rationale, Bitter-Lesson section) but
the prose is written twice and has already diverged in emphasis and
citations (compare design-critic/SKILL.md:37-45,249-281 with
completeness-critic/SKILL.md:21-45,152-168,424-447). The script side is
already SSOT'd (mint_critic_verdict.py lockstep ast test); the prose is
not.

Parked because (a) reconciling diverged exemption-adjacent prose is the
polarity-flip risk class, and (b) a shared reference file across two
plugins breaks plugin self-containment — the right mechanism is probably
a lockstep prose pin, not a shared file. Decide the mechanism when the
start condition forces both texts open anyway.
