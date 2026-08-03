# Plan: completeness-critic diverse-critic panel (v0.2.0)

Source brief: docs/spec-toolkit/specs/2026-06-12-completeness-critic-diverse-panel.md
Total tasks: 5
Critical-path depth: 1 (≤5)   ← all tasks Dependencies:none; they are logically disjoint sections of ONE file
Execution order: sequential (file-contention floor — all 5 edit the same SKILL.md, so SDD serializes them; no semantic dependency chain)
Plan-document-reviewer verdict: PASS (2026-06-12, 11/14 checks; 12-14 N/A, 15 advisory did not fire)

## Notes

- **All 5 tasks edit the single file `spec-toolkit/skills/completeness-critic/SKILL.md`.**
  They touch **disjoint sections** (lens interrogation / output discipline / honesty rails /
  design note / frontmatter), so there is **no semantic dependency** between them — every
  task is `Dependencies: none`. But because `Files touched` overlaps (same file), they are
  **NOT** parallel-dispatch-safe: every task is `Independent: false` and SDD runs them one
  implementer at a time (sequential floor). Critical-path **depth = 1** (no Dependencies
  chain); the serialization is a file-contention constraint, not a logical chain.
- **Acceptance is a grep diagnostic**, not a unit test: this is a prose skill file with no
  test harness. RED = the target string is absent before the edit; GREEN = present after.
  Each implementer must also confirm the skill-folder-structure hook stays green (no new
  subfolders) and SKILL.md stays under the ~6,000-token body ceiling (CLAUDE.md convention).
- nfr_security's promotion to load-bearing #1 is folded into T1 (same lens-list section) to
  avoid two tasks editing the same prose twice.

## Task 1 — Panel-dispatch reframe of the lens interrogation section

- Description: Rewrite `§The multi-lens fixed interrogation checklist` so the 5 fixed lenses
  run as a **dispatched panel** — one critic subagent **per lens with fresh context**
  (portable fan-out phrased abstractly: "dispatch one subagent per lens", like
  deep-research's convention, NOT bound to one harness), each carrying a **distinct persona**
  (malicious user / confused first-timer / 3am on-call ops / compliance auditor / competitor
  probing edges) and, where it helps, a **distinct input view** (draft-only vs
  original-requirements-only to catch "requirements entail X, draft dropped it"). Findings
  are **UNIONed** then deduped + re-seeded (existing loop). Replace the single-agent
  "run them as separate passes … blind to the others" framing (SKILL.md:82-84). In the same
  rewrite, **promote the NFR/security lens to load-bearing #1** with an explicit note that a
  generic omissions-hunt is structurally blind to it (experiment H4); permissions/data-boundary
  secondary. Tighten the overlapping `§Dual role` prose (SKILL.md:46-58) so it does not
  duplicate the new panel framing.
- Module: spec-toolkit/skills/completeness-critic/SKILL.md
- Files touched: spec-toolkit/skills/completeness-critic/SKILL.md
- Context paths:
  - spec-toolkit/skills/completeness-critic/SKILL.md
  - docs/spec-toolkit/specs/2026-06-12-completeness-critic-diverse-panel.md
  - docs/spec-toolkit/design/2026-06-12-diverse-critic-decorrelation-and-experiment.md
- Acceptance:
  - RED: `grep -i "dispatch one .*subagent per lens\|persona" spec-toolkit/skills/completeness-critic/SKILL.md` returns nothing (panel framing absent today).
  - GREEN: the lens section instructs dispatching one fresh-context critic subagent per lens with a distinct persona + input view + UNION of findings; the old "run them as separate passes" single-agent line is gone; NFR/security is marked load-bearing #1. greps for `persona`, `subagent per lens`, `union`, and `load-bearing` (near nfr/security) all succeed.
- Dependencies: none
- Independent: false
- Brief item covered: "Panel dispatch (the core)" + "nfr_security = load-bearing #1" (brief §Smallest End State items 1-2).

## Task 2 — Overlap-rate diagnostic rule + round-summary line

- Description: Add a short **overlap-rate diagnostic** rule: after each round, judge pairwise
  finding-overlap across the panel qualitatively — **high overlap (~>70%) → "panel not diverse
  enough, add a more orthogonal lens"**, with the **explicit honesty rail: high overlap signals
  redundancy, NOT near-completeness** (the exact capture-recapture misread). Add a matching line
  to `§Output discipline — round summary` (SKILL.md:174-185) so the round summary reports the
  overlap judgment + whether the panel was diverse enough. Keep it qualitative prose (no script,
  no computed metric).
- Module: spec-toolkit/skills/completeness-critic/SKILL.md
- Files touched: spec-toolkit/skills/completeness-critic/SKILL.md
- Context paths:
  - spec-toolkit/skills/completeness-critic/SKILL.md
  - docs/spec-toolkit/design/2026-06-12-diverse-critic-decorrelation-and-experiment.md
- Acceptance:
  - RED: `grep -i "overlap" spec-toolkit/skills/completeness-critic/SKILL.md` returns nothing.
  - GREEN: an overlap-diagnostic rule exists stating high overlap = redundancy NOT near-completeness, and the round-summary section reports the overlap judgment. greps for `overlap`, `not diverse enough` (or equivalent), and `NOT` near `complete`/`near-complete` succeed.
- Dependencies: none
- Independent: false
- Brief item covered: "Overlap-rate diagnostic" (brief §Smallest End State item 3).

## Task 3 — Reject capture-recapture completeness estimate (honesty rail)

- Description: Add a new honesty rule (extend `§Ban claiming "complete"`, SKILL.md:147-152, or a
  sibling subsection) **banning any capture-recapture point estimate / completeness percentage**.
  State the mechanism: same-base-model critics are positively correlated (find the same, miss the
  same) → the estimator reads high overlap as "nearly exhausted" → **systematically under-counts
  the residual → false completeness** (the most dangerous honesty failure). This reinforces the
  existing word-level "ban complete" rail with a statistical-level rail. Reference the experiment
  (`design §Part C H2`) as the evidence.
- Module: spec-toolkit/skills/completeness-critic/SKILL.md
- Files touched: spec-toolkit/skills/completeness-critic/SKILL.md
- Context paths:
  - spec-toolkit/skills/completeness-critic/SKILL.md
  - docs/spec-toolkit/design/2026-06-12-diverse-critic-decorrelation-and-experiment.md
- Acceptance:
  - RED: `grep -i "capture-recapture\|completeness percentage\|completeness %" spec-toolkit/skills/completeness-critic/SKILL.md` returns nothing.
  - GREEN: a rule bans the capture-recapture / completeness-% estimate and explains the correlated-critics → under-count → false-completeness mechanism. greps for `capture-recapture` and `under` (under-count/under-estimate) and `false completeness` (or equivalent) succeed.
- Dependencies: none
- Independent: false
- Brief item covered: "Reject the completeness estimate" (brief §Smallest End State item 4).

## Task 4 — Lens deletability design note (Bitter Lesson)

- Description: Add a one-paragraph design note: each lens is designed **deletable** — a future
  stronger model that subsumes a lens unaided can have it removed without redesign; re-baseline
  the panel periodically (cite the two-kinds-of-scaffolding / Bitter-Lesson reasoning — the panel
  is verification scaffolding kept regardless of model strength, but each *individual lens* is a
  crutch that may be subsumed). Place it near the panel definition or as a short standalone note.
- Module: spec-toolkit/skills/completeness-critic/SKILL.md
- Files touched: spec-toolkit/skills/completeness-critic/SKILL.md
- Context paths:
  - spec-toolkit/skills/completeness-critic/SKILL.md
  - docs/spec-toolkit/research/2026-06-12-sdd-harness-bitter-lesson.md
- Acceptance:
  - RED: `grep -i "deletable\|bitter lesson" spec-toolkit/skills/completeness-critic/SKILL.md` returns nothing.
  - GREEN: a note states each lens is designed deletable / re-baseline periodically, grounded in the Bitter-Lesson two-kinds-of-scaffolding reasoning. greps for `deletable` and `Bitter Lesson` succeed.
- Dependencies: none
- Independent: false
- Brief item covered: "Lens deletability (Bitter Lesson)" (brief §Smallest End State item 5).

## Task 5 — Frontmatter version bump + description update

- Description: Bump the frontmatter `version: 0.1.0 → 0.2.0` and update the `description:` so it
  reflects the diverse-critic **panel** (decorrelated lenses, persona/input-view per critic,
  union, overlap diagnostic) rather than the old single-agent sweep — without changing the
  description's activation triggers (still routes on "spec draft for gaps / completeness / blind
  spots"). Keep the description one coherent sentence-set; do not bloat.
- Module: spec-toolkit/skills/completeness-critic/SKILL.md
- Files touched: spec-toolkit/skills/completeness-critic/SKILL.md
- Context paths:
  - spec-toolkit/skills/completeness-critic/SKILL.md
- Acceptance:
  - RED: `grep "version: 0.2.0" spec-toolkit/skills/completeness-critic/SKILL.md` returns nothing (still 0.1.0).
  - GREEN: `grep "version: 0.2.0"` succeeds AND the description mentions the panel / decorrelated lenses while preserving the gap/completeness/blind-spots activation triggers.
- Dependencies: none
- Independent: false
- Brief item covered: "Version bump 0.1.0 → 0.2.0" (brief §Smallest End State final line).
