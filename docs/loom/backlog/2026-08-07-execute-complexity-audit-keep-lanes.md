---
name: 2026-08-07-execute-complexity-audit-keep-lanes
description: Execute the ten KEEP / KEEP-WITH-CAVEAT items from the 2026-08-07 family complexity audit, in four arcs
status: OPEN
origin: 2026-08-07 family complexity audit + proposal-critique triage (docs/loom/audits/2026-08-07-family-complexity-audit.md)
---

Ten triaged items, recommended as four arcs in this order (rationale and
per-item caveats in the audit doc's Triage and Impact sections):

1. Mechanical dedup arc — B1 state-anchor wording into distribute.py
   SSOT (7 hand-copied files today); B2 tdd-standard.md byte-identical
   fork into distribute.py; C2 brief-before-asking clause (near-verbatim
   ×4 in design-side routers — the trigger tail is byte-identical, the
   fork-noun varies, so C2 needs a parameterized carrier or a one-time
   wording normalization) to one source; D2 router-card five rules into
   verify-drift.py coverage. Behavior-neutral except C2's wording
   normalization; existing machinery throughout.
2. Legislation arc — E1 deletion-first review dimension via the
   _reviewer-discipline SSOT; E3 record this audit's recipe as a
   human-triggered, proposal-only prune runbook. Runs before the prose
   arc so that arc dogfoods the new dimension.
3. D1 — generate docs/loom/memory/README.md's `## Index` (7,761-word
   hand-mirror today) the way backlog_index.py already generates
   BACKLOG.md. Separate PR: touches the store charter's stated
   maintenance procedure, needs a plugin-wide contradiction sweep.
4. Prose slim arc — A2 extract requesting-docs-review's convergence
   block (1,424 w; cap headroom 72 w today, so any net-adding edit
   over 72 words must slim first — the tightest cap pressure in the
   family); A1 collapse finishing Step 8's five ONCE-checklists
   (1,123 w, semantics preserved); A3 downgrade writing-plans'
   hypothetical wrong-bind reversal protocol (315 w) to one line.
   Weak-model cold-reads mandatory; 50 test files name these skills
   (grep of `*.py` under `loom-*/scripts`, `loom-*/tests`, `scripts/`).

Expected impact if all four land: ~-1,900 words across the three
heaviest SKILL.md bodies, maintenance tax on four cross-file rules drops
to single-source, and the family gains its first standing
anti-complexity loop (E1 + E3). Does not shorten the mandatory happy
path — those gates were judged load-bearing.
