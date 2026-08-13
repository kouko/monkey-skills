---
name: 2026-08-13-close-out-open-question-gate-is-prose-orchestrated-not-hook-enforced
description: close-out enforcement for an unresolved OQ-<n> ships as a Step 8 prose table row, not a hook-mechanized check
status: OPEN
origin: 2026-08-13 open-question-dispatch-gate arc kickoff decision, recorded in docs/loom/plans/2026-08-13-open-question-dispatch-gate.md §Notes
start: the first branch that closes with an unresolved OQ-<n> despite the Step 8 table row, or the next loom_gate_markers.py touch, whichever comes first
---

- Start: the first branch that closes with an unresolved OQ-<n> despite the
  Step 8 table row, or the next loom_gate_markers.py touch, whichever comes
  first
- Origin: 2026-08-13 open-question-dispatch-gate arc kickoff decision,
  recorded in docs/loom/plans/2026-08-13-open-question-dispatch-gate.md
  §Notes

  The §Notes entry is titled "Kickoff decision: close-out enforcement
  strength".
- What: the close-out enforcement for an unresolved open question (an
  `OQ-<n>` entry left `[OPEN]`) ships in this arc as a row in
  `finishing-a-development-branch`'s Step 8 sub-checks table — prose an
  orchestrator follows, invoking `check_open_questions.py` against the
  branch's plan and STOPping on a non-zero exit (Task 5 of the arc's plan).
  This is deliberately NOT hook-enforced: the real process-level
  enforcement point, `loom-code/hooks/git-guard.py` (a registered
  PreToolUse hook), only checks marker-file existence and freshness and is
  blind to plan content — it cannot see whether a plan's `## Open
  Questions` section holds an `[OPEN]` entry. A prose row can be skipped by
  an orchestrator that skims Step 8; a hook cannot be skimmed.
- Mechanized alternative (considered, not taken): fold the open-questions
  check into `loom_gate_markers.py`'s `review-pass` / `verified --run`
  mint path, so an unresolved question blocks the mint mechanically
  instead of via prose. Not taken this arc because that file's own
  docstring declares it frozen, and every field it writes is asserted by
  `test_loom_gate_markers.py` — folding in a new check touches a contract
  surface with more blast radius than this arc's scope covers.
- Next step when this fires: land the `loom_gate_markers.py` mint-path
  check (or, if the actual failure mode turns out to be the hook's
  content-blindness rather than an orchestrator skipping the table row,
  harden `git-guard.py` instead), then retire this entry.
