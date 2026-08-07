# Brief — arc 4: A-lane prose slims (A2 / A1 / A3)

Date: 2026-08-07 · Branch: (pending — base must include PR #674's merge;
A1's file overlaps arc 3) · Origin:
docs/loom/backlog/2026-08-07-execute-complexity-audit-keep-lanes.md (arc 4)
+ docs/loom/audits/2026-08-07-family-complexity-audit.md (A1/A2/A3).
Endpoint: continuous per user /goal「繼續做下去吧」— PR-open terminal, never
auto-merge. Design-side on-ramp: N/A (refactor — negative guard; ready
check ran at arc-1 kickoff).

## Problem

The three heaviest loom-code core skills sit near the 4,500-word hard cap,
and requesting-docs-review's cap pressure (72 w headroom at audit time)
blocks future edits. The audit's KEEP/KWC verdicts: A2 extract the
convergence-contract block to a reference (pure move, ~300 w decision
surface stays inline); A1 collapse finishing's five ONCE-checklists into
one structure (semantics and fallback wording preserved); A3 downgrade the
hypothetical wrong-bind reversal protocol to a one-line note.

Recon corrections to the audit's figures (both are the audit's own
measurement-population class): the A2 block measures 1,446 w at :43-84
(audit said 1,424 — close); the A3 trigger paragraph is 44 w at
writing-plans SKILL.md:206 (audit's 315 w measured a span that included
neighboring change-folder-cascade text) — A3's cap relief is ~30 w, its
surviving value is removing an un-evidenced protocol, per its original
KEEP-WITH-CAVEAT re-add trigger (first real wrong-bind incident restores
from git history).

## Users

Future editors of the three skills (cap headroom restored where it is
binding); weak-model executors (extraction must not sever cross-referenced
rules — repo memory extraction-severing-cross-ref-needs-weak-model-test
mandates a weak-model cold-read per extraction).

## Smallest End State

1. A2: requesting-docs-review 4,428 → ~3,330 w. The Directives 1-4 block
   (:43-84, 1,446 w) moves to references/convergence-contract.md; inline
   remains the decision surface (the three hand-the-user options + the
   binding one-line summary of each directive) with an imperative
   "Read references/convergence-contract.md before running any round"
   pointer (house form). Every pin test's pinned string keeps a carrier:
   pins whose phrases move (bounded cap / auto-third-round / round-N
   handoff / delta-scoped / oscillation — list per recon) are updated to
   pin the reference file OR the surviving inline summary, preserving each
   pin's PURPOSE; never weakened.
2. A1: finishing's five ONCE-bullets (974 w at arc-3-merged state) collapse
   into one "Close-out sub-checks (orchestrator-only, ONCE per branch)"
   table — one row per check (trigger / N/A form / action / stage duty),
   per-check fallback wording preserved verbatim in the cells; target
   saving 400-600 w (4,402 → ~3,800-4,000; still above soft target —
   accepted, hard-cap headroom is the goal). Pin tests (archive-step,
   backlog-close, memory-store-integrity) keep their pinned strings via
   table cells.
3. A3: writing-plans' wrong-bind reversal paragraph (:206, 44 w) → one
   line: "A confirmed wrong-bind incident downgrades layer (i) to
   confirm-before-use — restore the full protocol from git history."
   test_writing_plans_change_binding.py's pins ("wrong-bind",
   "confirm-before-use") survive in that line.
4. Weak-model cold-read per extraction (A2 mandatory; A1 if any cell text
   separates from a cross-referenced rule): haiku executes the slimmed
   skill blind on one real case; misread = fix wording, not reader.
5. Audit-doc ride-along: correct the A-lane figures (A2 1,424→1,446;
   A3 315→44 with the population note) — the measurement-value sweep duty.
6. loom-code minor bump (three core SKILL.md bodies change) + CHANGELOG +
   version-pin rewrite.

## Current State Evidence

- A2: block :43-84 (1,446 w); references/design-evidence.md already exists
  (894 w, author-facing); pin tests enumerated —
  test_requesting_docs_review_skill.py:534,551,571-576 (bounded cap /
  once-per-branch / auto-third-round), :607-609 + test_docs_reviewer_agent.py:279
  (prose mention in a docstring, not a pin — corrected at review; no pin
  migration occurred there) (delta-scoped), :817-837 (round-N handoff /
  retained), :551-557 (oscillation).
- A1 (at arc-3 branch state, becomes main on #674 merge): Step 8 :186-291;
  five bullets :187-273 = 78+208+155+383+150 w; pins in
  test_finishing_archive_step.py (:106-135 N/A wording + once-per-branch +
  orchestrator-only + proximity :149-158), test_finishing_backlog_close.py:94,
  test_finishing_memory_store_integrity.py:17-93.
- A3: single paragraph writing-plans SKILL.md:206 (44 w); pins
  test_writing_plans_change_binding.py:103-112.
- Cap math: hard 4,500 / soft ~3,750 (test_rcr_capacity_pointer.py:10,66,69);
  projections — A2 3,328 (under both), A1 3,802-4,002 (under hard),
  A3 3,997→~3,970 (under hard).
- Extraction conventions: imperative "Read <ref> before <act>" pointer form
  (requesting-code-review SKILL.md:18 precedent); extraction-severing
  weak-model cold-read duty (repo store entry).

## Decision

Ship A2 (the load-bearing slim), A1 (structure collapse, semantics
verbatim in cells), A3 (one-line downgrade), the cold-reads, the audit
figure corrections, and the bump. Do NOT slim below what the pins carry;
do NOT touch rule semantics anywhere; do NOT extract A1's content to a
reference (collapse in place — its checks are load-bearing at point of
use); execution WAITS for PR #674's merge (A1 file overlap) — if
continuation pressure demands earlier start, split execution: A2+A3 from
main immediately (no overlap), A1 as a follow-up after merge.

## Out of Scope

- Any semantic change to the convergence contract, close-out checks, or
  binding cascade
- rdr's references/design-evidence.md (already extracted)
- The mandatory happy path's gate count (load-bearing, audit-exempt)

## Alternatives Considered (Axis 4)

Pre-triaged by the audit + E-1 slim-arc precedent (extraction with pin
preservation, weak-model cold-read, per-file pin locking — four skills
shipped this shape at #651/#652). Narrow space; no fresh research owed.

## What Becomes Obsolete (Axis 5)

- The inline convergence-contract body (moves, not deleted)
- The five separate ONCE-bullet blocks (collapse into the table)
- The wrong-bind protocol paragraph (downgrades; git history is the archive)
- The audit's stale A-lane figures

## Open Questions

- None blocking. Execution gate: PR #674 merge (or the A2+A3 split start).
