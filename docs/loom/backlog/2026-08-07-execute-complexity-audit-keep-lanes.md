---
name: 2026-08-07-execute-complexity-audit-keep-lanes
description: Execute the ten KEEP / KEEP-WITH-CAVEAT items from the 2026-08-07 family complexity audit, in four arcs
status: SHIPPED
origin: 2026-08-07 family complexity audit + proposal-critique triage (docs/loom/audits/2026-08-07-family-complexity-audit.md)
---

Ten triaged items, recommended as four arcs in this order (rationale and
per-item caveats in the audit doc's Triage and Impact sections):

1. Mechanical dedup arc — RESHAPED by 2026-08-07 recon (arc-1 brief:
   docs/loom/specs/2026-08-07-loom-mechanical-dedup-arc1.md) from
   "relocate into distribute.py SSOT" to "pin with drift-guard tests".
   This arc ships: T1 state-anchor carrier-inventory test (B1 was NOT 7
   byte-identical hand-copies — recon found 12 grep hits across 9 files,
   none byte-identical, so relocation would rewrite rendered prose;
   pinned by scripts/test_state_anchor_carrier_inventory.py instead of
   consolidating); T2 brief-before-asking anchor-sentence lockstep test
   (C2 — the shared trigger sentence is already word-identical across
   the 4 design-side router SKILL.md files, though loom-discovery's copy
   wraps differently; the lockstep normalizes whitespace then requires
   equality, deliberately tolerating a pure re-wrap); T3 router-card
   rule-token presence test (D2
   — each of the 5 load-bearing rules' anchor TITLE token (rule 5 =
   "Research before asking") present in BOTH hooks/router-card.md and
   using-loom-code/SKILL.md's rules block; router-card additionally
   names `dev-workflow:brief-before-asking` inline in rule 5 — a
   deliberate divergence the test tolerates, not part of the pinned
   token set), plus CI trigger wiring for the cross-plugin paths the
   tests read and a session-start comment update naming the T3 guard.
   B2 tdd-standard.md dropped from this arc — recon found it already
   distribute.py-managed (ROUTE copy + verify-drift.py byte-check); the
   audit's "not managed" premise was false. No relocation, no
   rendered-text changes; behavior-neutral.
2. Legislation arc — E1 deletion-first review dimension via the
   _reviewer-discipline SSOT; E3 record this audit's recipe as a
   human-triggered, proposal-only prune runbook. Runs before the prose
   arc so that arc dogfoods the new dimension.
3. D1 — generate docs/loom/memory/README.md's `## Index` (7,761-word
   hand-mirror today) the way backlog_index.py already generates
   BACKLOG.md. Separate PR: touches the store charter's stated
   maintenance procedure, needs a plugin-wide contradiction sweep.
4. Prose slim arc — split into 4a (shipping now) and a deferred A1.
   4a: A2 extract requesting-docs-review's convergence block
   (1,446 w; cap headroom 72 w today, so any net-adding edit over
   72 words must slim first — the tightest cap pressure in the
   family); A3 downgrade writing-plans' hypothetical wrong-bind
   reversal protocol (44 w — the earlier 315 w figure included
   neighboring text) to one line. Deferred: A1 collapse finishing
   Step 8's five ONCE-checklists (974 w of bullets at the arc-3 state;
   collapse saves ~400-600 w, semantics preserved), held behind
   PR #674's merge. Weak-model cold-reads mandatory;
   44 test files + 6 production scripts name these skills (grep of
   `*.py` under `loom-*/scripts`, `loom-*/tests`, `scripts/`; measured
   at e610f7c4 — this branch's own new test file makes it 45+6 at
   merge).

Expected impact of arcs 1-3 plus arc 4a (arc 4's A1 remains deferred
behind PR #674): ~-1,150 w from arc 4a (A2+A3, shipping now); A1's
deferred ~400-600 w follows post-#674 — the old aggregate ~-1,900 w
figure conflated both waves. Maintenance tax on the four cross-file
rules
gains machine-readable drift guards (arc 1 pins carriers/tokens rather
than consolidating to one source — see item 1 above), and the family
gains its first standing
anti-complexity loop (E1 + E3). Does not shorten the mandatory happy
path — those gates were judged load-bearing.

SHIPPED evidence: arc 1 = PR #670 (drift-guard tests); arc 2 = PR #672
(loom-code 0.66.0, deletion-first + runbook); arc 3 = PR #674
(index generation, loom-code 0.66.1 / loom-pipeline 0.15.0); arc 4a =
PR #675 (loom-code 0.67.0, A2+A3); A1 = branch
refactor/loom-arc4b-finishing-collapse (loom-code 0.68.0, the five
ONCE-bullets → one close-out table, −401 w) — the deferred tail lands,
all ten triaged items closed.
