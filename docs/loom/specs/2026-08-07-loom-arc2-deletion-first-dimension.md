# Brief — arc 2: deletion-first review dimension (E1) + complexity-prune runbook (E3)

Date: 2026-08-07 · Branch: `feat/loom-arc2-deletion-first-dimension` @ 012a4c8a
Origin: docs/loom/backlog/2026-08-07-execute-complexity-audit-keep-lanes.md (arc 2)
+ docs/loom/audits/2026-08-07-family-complexity-audit.md (E1 :59, E3 :69).
Endpoint: continuous per user /goal「繼續做下去吧」(2026-08-07) — auto-advance
stage to stage, PR-open is the terminal stop, never auto-merge; halt on any
re-scope/STOP-contract event. Design-side on-ramp: N/A (internal tooling, no
product surface; backlog ready check ran at arc-1 kickoff — seed is the
execute entry's arc-2 item).

## Problem

Over-engineering findings currently have no dedicated signal: YAGNI exists
as pass/fail baseline Rule 2 ("Simplicity First", _baseline.md:17-20) and as
severity rows folded INSIDE the architecture dimension
(rubrics/arch-gate.md:54-69 — speculative solutions 🔴, over-abstraction 🟡),
so a branch can ship speculative machinery buried as one 🟡 among many
architecture findings, with no per-dimension score forcing the reviewer to
look. The complexity audit legislated the fix (two in-repo occurrences +
external research): a scored **deletion-first** dimension riding the two
code reviewers — no new station, no new round. E3 companion: the audit's
own recipe becomes a human-triggered, proposal-only runbook so the
mechanism-prune loop outlives this session. Research caveat baked in: LLM reviewers systematically over-correct on
requirement-conformance judgment ("Are LLMs reliable code reviewers? —
systematic overcorrection in requirement conformance judgement",
Automated Software Engineering (Springer), 2026,
https://link.springer.com/article/10.1007/s10515-026-00638-5), so the
dimension must require a CONCRETE simpler alternative per finding — no
vague "this feels heavy" flags.

Recon correction to the audit's E1 wording: dimension definitions are
hand-authored per-agent delta sections, NOT distribute-managed
(code-quality-reviewer.md:406-420, code-reviewer.md:414-427; managed blocks
end earlier) — and _reviewer-discipline.md fans to all four reviewers,
which would leak the dimension to spec/docs-reviewer (audit scopes E1 to
the two code reviewers only). So E1 follows the two prior
dimension-addition precedents (external-surface-grounding 2026-05-22,
deliberate-simplification 2026-06-22): spec doc + per-agent hand edits +
a drift pin test (arc-1's token-pin pattern guards the two copies).

## Users

Reviewers (the two code-review agents) get a scoring obligation; branch
authors get over-engineering surfaced as its own verdict line; E2's parked
re-trigger ("complexity findings recur across ≥2 arcs despite E1") gets a
countable signal (findings tagged `deletion-first`); future maintainers get
a repeatable prune recipe (E3).

## Smallest End State

1. **Dimension** `deletion-first` added to code-quality-reviewer (7→8) and
   code-reviewer (10→11): frontmatter counts, role lines (also fixing
   code-reviewer.md:10's pre-existing stale "7-dimension scores"),
   `dimension_scores:` enums, Dimensions tables, plus one expanded section
   per agent defining the check: for each NEW abstraction/config/flag/
   extension point in scope — does it have ≥2 concrete users NOW, was it
   asked for, and can the reviewer name a smaller shape that does the same
   job? **A finding REQUIRES the named smaller shape** (anti-over-correction
   guard); well-motivated complexity with the motivation visible in
   code/task text is a PASS, not a note.
2. **Rubric move, not copy**: arch-gate.md's YAGNI/Speculative-Generality
   rows (:54-69 region) move to a `deletion-first` scoring section (same
   file, own heading scoped to the new dimension) so one defect class is
   scored once; architecture keeps structural/boundary/coupling rows. Edit
   lands in the code-team CANONICAL copy + `distribute.py` run in the same
   commit (knowledge-layer workflow), verify-drift green.
3. **Pin test** (repo-root scripts/, arc-1 pattern): the dimension's anchor
   tokens present in BOTH agent files' dimension tables + the enum lines —
   guards the two hand-authored copies against drift.
4. **requesting-code-review/SKILL.md** `dimension_scores:` example block
   (:121-130) gains `deletion-first:` AND the already-missing
   `deliberate-simplification:` (pre-existing gap, fixed while the block is
   open).
5. **E3 runbook** at docs/loom/references/complexity-prune-runbook.md:
   trigger (human-invoked; suggested cadence: when mechanism growth is
   felt, or ~quarterly), the four-arm read-only audit recipe, load-bearing
   do-not-touch discipline, proposal-critique triage, outputs (audit doc +
   PARKED/OPEN backlog entries), pointer to the 2026-08-07 audit + arcs as
   the worked example. Explicitly NOT a skill (audit E3 caveat).
6. Ride-along: T2 one-word fix — scripts/test_brief_clause_lockstep.py
   mutation test perturbs ROUTER_FILES[1] instead of ROUTER_FILES[0]
   (arc-1 carried debt, reviewer-dictated).
7. loom-code 0.66.0 (minor — behavior-adding): manifests pair + CHANGELOG +
   version-pin test rewrite per house convention.

## Current State Evidence

- Forward: reviewers load their agent .md as system prompt; dimension
  tables at code-quality-reviewer.md:342-420 (enum :352, table :406-420)
  and code-reviewer.md:357/:414-427; verdict blocks flow to SDD verdict
  table and finishing's gate aggregation.
- Reverse (SSOT): distribute.py manages three agent blocks
  (baseline-v1 :188-194, reviewer-discipline-v1 :207-212 → 4 reviewers,
  rule-sheet-v1 :221) — dimension text is OUTSIDE all of them; rubrics/
  standards are ROUTE-managed functional copies (canonical:
  domain-teams/skills/code-team/, workflow: edit canonical → run
  distribute.py same commit → verify-drift.py CI).
- Error: no test pins dimension COUNTS; docs-reviewer's 5-dim enum is
  pinned (test_docs_reviewer_agent.py:158-183 — untouched, dimension stays
  out of docs/spec reviewers); dimension-section pin precedent:
  test_code_reviewer_principles_derivation.py. Coherence CI does not read
  agents/*.md (check-plugin-description-skill-coherence.py:205-229).
- Data: existing YAGNI text — _baseline.md:17-20 (Rule 2),
  arch-gate.md:54-69 (🔴🔴🟡🟡 rows), pragmatic-principles.md:76-113
  (§YAGNI + Rule of Three); deliberate-simplification's D9
  (code-reviewer.md:476-539) is marker-format auditing only — no overlap
  with the new dimension's over-engineering judgment.
- Boundary: scoped to loom-code's two code reviewers; docs-reviewer,
  spec-reviewer, and design-side critics untouched. Plugin at branch base:
  loom-code 0.65.2.

## Decision

Ship the dimension + rubric move + pin test + SKILL example fix + E3
runbook + T2 ride-along + 0.66.0 bump. Do NOT create a new distribute
block or standard file for the dimension (two hand-authored sections + a
pin test is less machinery than a new SSOT fan-out for two targets); do
NOT touch spec/docs reviewers or design-side critics; do NOT build E3 as
a skill; do NOT add plan-time budget fields (E2 stays PARKED behind its
re-trigger).

## Out of Scope

- E2 plan-time complexity budgets (PARKED, re-trigger recorded)
- Any change to docs-reviewer / spec-reviewer / design-side critic verdicts
- distribute.py extensions or new managed-block types
- Retro-scoring past branches; the dimension applies from merge forward
- arch-gate rows other than the YAGNI/Speculative-Generality move

## Alternatives Considered (Axis 4)

Triaged at the audit (proposal-critique matrix + EN research): new review
station (rejected — new machinery, over-correction risk), plan-time budget
fields (DEFER as E2 behind evidence), reviewer dimension (chosen — rides
existing rounds). In-repo precedent: the last two dimension additions
shipped exactly this shape and stuck. Space is narrow and pre-decided with
recorded reasoning; no fresh research owed.

## What Becomes Obsolete (Axis 5)

- arch-gate's YAGNI rows AS architecture-dimension content (moved, deleted
  from the architecture section in the same edit — no double-scoring)
- code-reviewer.md:10's stale "7-dimension scores" phrase
- The rcr SKILL.md example block's missing-dimension gap
- The audit's "Recommended execution order" arc-2 line completes → backlog
  execute entry updates at close-out (backlog-close check will evaluate)

## Open Questions

- None blocking. Dimension NAME pinned here: `deletion-first` (kebab-case,
  matches sibling naming; the audit's own vocabulary).
