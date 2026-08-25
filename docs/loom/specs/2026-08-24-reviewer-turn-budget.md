# Reviewer turn budget — stop paying for 8 redundant suite runs per task

Date: 2026-08-24
Status: brief (draft — pending user sign-off before writing-plans)

## Design-side on-ramp

not fired — mechanism increment on existing reviewer contracts, no product-shaped/user-facing new work (Axis 0 negative guard). Backlog ready check RAN this session (112 open items surfaced; none about reviewer budgets or suite re-runs).

## Problem

Measured across all local reviewer transcripts (2026-07-23 → 08-23): every reviewer arm independently re-runs the full package suite to satisfy Rule R3 ("evidence you did not independently confirm → downgrade"). Per dispatch: code-reviewer 2.24 suite runs (n=398), code-quality-reviewer 2.42 (n=614), spec-reviewer 1.67 (n=607).

One SDD task therefore pays ~4 package-suite runs (implementer final run + spec + cqr), and branch close adds ~4.5 more (2 panel arms × 2.24). The suite stdout floods each reviewer's context, and every later turn drags it as cache-read — reviewer averages: code-reviewer 48 turns / 3.94M cache-read, cqr 39 / 2.94M. Suite runs and their context tail are the single largest measured reviewer cost after the tier fix (0.98.0).

## Users

kouko's loom arcs (every SDD task and branch close pays this), and consumer repos with slow suites — a 5-minute suite × 8 redundant runs is wall-clock pain, not just tokens.

## Smallest End State

1. **R3 amendment in the SSOT** (`loom-code/scripts/_reviewer-discipline.md`, distributed by `distribute.py`): a sha-bound `verified` gate marker (`.git/loom/verified.json` minted via `loom_gate_markers.py verified --run`, matching the commit under review) COUNTS as independently confirmed package-suite evidence. Citing the marker (one `loom_gate_markers.py` status/read command to confirm the sha matches) replaces re-running the package suite. No marker for the reviewed sha → R3 behaves exactly as today (fail-closed).
2. **Implementer mints the task-level marker**: after its final package-level run (already mandated by its rule 13), the implementer runs the suite THROUGH `loom_gate_markers.py verified --run` so the marker exists when the task's reviewers dispatch. One flag change in its contract, no new run.
3. **Targeted probes stay unlimited**: mutation probes and touched-test-file runs are explicitly exempt from any budget — the cqr mining showed these ARE the quality-unique catches. Only the FULL package suite re-run is replaced by marker citation.
4. **Soft tool guidance, not a hard cap**: reviewer contracts gain one line — resolve the diff via one `git diff` of the range, then targeted reads (code-reviewer currently averages 3.8 git-diff calls). Advisory wording; no mechanical enforcement in this arc.
5. Version bump + distribute + drift tests updated.

## Current State Evidence

- **Forward**: `loom-code/scripts/_reviewer-discipline.md` (§Rule R3, 641 words, SSOT) → distributed into `agents/{code-reviewer,code-quality-reviewer,spec-reviewer,docs-reviewer}.md` (code-reviewer.md:101-117) by `distribute.py` (AGENT_REVIEWER_DISCIPLINE_SSOT_REL, distribute.py:196-200); drift guarded by the reviewer-discipline drift test.
- **Reverse**: `distribute.py` owns the copy direction (SSOT → agent files); editing agent files in place is reverted — the edit lands in the SSOT and re-distributes.
- **Error**: no marker for the reviewed sha (uncommitted worktree state, mid-task review, foreign repo without loom markers) → R3 falls back to today's behavior: run it yourself or downgrade. The amendment only ADDS an evidence class, never removes one.
- **Data**: tool-call distribution from 1,937 reviewer transcripts (scan method: classify Bash commands per subagent JSONL; scratchpad `rev_tools.py`, restated in the eventual audit): suite runs/dispatch 2.24 / 2.42 / 1.67 / 0.59 (cr / cqr / spec / docs); git-diff 3.8/dispatch on code-reviewer.
- **Boundary**: `loom_gate_markers.py verified --run` already exists, binds the current HEAD sha, and mints only on real exit 0 (used at finishing Step 9c today). The amendment reuses it unchanged at task level; `verification-before-completion` remains the package-level authority at branch close.

## Alternatives Considered

My take — Recommend: marker-as-evidence (the design above). Why: it converts "run it yourself" into "verify a sha-bound mechanical receipt" — same trust chain the push gate already relies on, zero new judgment surface, fail-closed when absent. Conditional reversal: if the A/B shows budgeted reviewers miss defects the current contract catches, keep R3 as-is and accept the cost.

- **Hard turn cap (e.g. ≤25 turns per reviewer)**: rejected — blunt; would amputate mutation probes (the proven quality-unique catch mechanism) along with waste; cap-tuning becomes a new maintenance surface (repo memory: a cap raised at every touch is not a cap).
- **Reviewers trust implementer test_results outright**: rejected — that is the false-green R3 exists to kill; the marker differs because it is minted by a script from a real exit 0, not self-reported.
- **Cache-oriented batching of same-type dispatches**: rejected for this arc — local experiment showed no detectable win (docs/loom/backlog/2026-08-06-same-type-dispatch-batching-cache-experiment.md).
- (No WebSearch round: repo-internal contract mechanics; no external design space applies.)

## What Becomes Obsolete

The de-facto practice of each reviewer re-running the package suite (2.2-2.4×/dispatch) for the R3 clean-PASS. The R3 prose itself stays — only its satisfiable-evidence set widens. Nothing else is removed.

## Decision

Amend R3 in the SSOT to accept sha-bound verified markers as independently-confirmed suite evidence; implementer mints the marker through its existing final run; targeted probes stay unlimited; one-line diff-hygiene guidance. Ship behind an A/B: re-run the G4 pinned-worktree review comparison (budgeted vs current contract) and require no recall loss on the G4 seeded defects before merge.

## Out of Scope

- Hard mechanical turn/tool caps (revisit only if the soft guidance measurably fails).
- docs-reviewer changes (0.59 suite runs/dispatch — not the hotspot).
- implementer cost work (separate arc: tier measurement).
- Any change to the aggregation rules or severity classes.
- style-gating carve-out (measured non-viable 2026-08-24, see the cqr mining audit).

## Queue relation

unqueued — direct continuation of the 2026-08-24 cost-analysis arc by user request; no existing backlog entry covers reviewer suite re-runs.

## Open Questions

- OQ-1: G4 A/B harness details — reuse the pinned worktree + seeded-defect set as-is, or extend with one mutation-probe case to guard finding #3's class? (resolve at plan time)
