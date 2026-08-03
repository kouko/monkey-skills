# Plan: completeness-critic v0.2.1 — panel dogfood hardening

Source brief: docs/spec-toolkit/specs/2026-06-12-completeness-critic-v0.2.1-panel-hardening.md
Total tasks: 3
Critical-path depth: 1 (≤5)   ← all tasks Dependencies:none; disjoint sections of ONE file
Execution order: sequential (file-contention floor — all 3 edit the same SKILL.md)
Plan-document-reviewer verdict: PASS (2026-06-12, 14/14 checks; 12-14 N/A, 15 advisory did not fire)

## Notes

- **All 3 tasks edit `spec-toolkit/skills/completeness-critic/SKILL.md`** on disjoint sections (loop-until-dry / write-back+consolidation / overlap-line+frontmatter). No semantic dependency → every task `Dependencies: none`; but `Files touched` overlaps (same file) → every task `Independent: false`, SDD serializes. Depth = 1.
- Acceptance = grep diagnostic (prose skill file, no unit test). RED = target absent before; GREEN = present after. Implementers must keep flat-folder + ~6,000-token body ceiling, and **not run git commit/add** (orchestrator owns commits).

## Task 1 — F-1: loop-until-dry cost off-ramp for the panel

- Description: Rewrite `## loop-until-dry` so the round/termination rule is reconciled with the panel's per-round cost. Changes: (a) **name the cost explicitly** — a panel round = N fresh-context subagent dispatches, so a blanket re-sweep is expensive; (b) re-seeding becomes **targeted, not blanket** — after round 1, re-dispatch **only the lens(es) whose re-seeded gaps open a genuinely new object/actor/state-class**; (c) escalate to a **full** second panel round only when a re-seed surfaces a new defect *class*, NOT on a blanket K=2-dry re-run of all 5 critics; (d) keep **K=2 consecutive dry rounds as the logical stop**, but bound the *mechanism* to "re-run a lens only when its input actually changed". Add an explicit anti-pattern: silently skipping the loop to save cost (the dogfood F-1 / pairwise-bypass failure).
- Module: spec-toolkit/skills/completeness-critic/SKILL.md
- Files touched: spec-toolkit/skills/completeness-critic/SKILL.md
- Context paths:
  - spec-toolkit/skills/completeness-critic/SKILL.md
  - docs/spec-toolkit/dogfood/2026-06-12-completeness-critic-panel-dogfood.md
  - docs/spec-toolkit/specs/2026-06-12-completeness-critic-v0.2.1-panel-hardening.md
- Acceptance:
  - RED: `grep -iE "targeted re-seed|only the lens|re-run a lens only when" SKILL.md` returns nothing (loop is still the blanket-K=2 inherited rule).
  - GREEN: `## loop-until-dry` names the panel-round cost (N subagents), makes re-seeding targeted (re-run only the lens whose input changed / that opens a new class), keeps K=2-dry as the logical stop, and bans skipping-the-loop-to-save-cost. greps for `targeted` (or "only the lens"), `K = 2`/`K=2` (logical stop preserved), and `subagent` (cost named) all succeed.
- Dependencies: none
- Independent: false
- Brief item covered: "F-1 — loop cost off-ramp" (brief §Smallest End State item 1).

## Task 2 — F-2: consolidation (dedup + rank) step before write-back

- Description: Add a short **consolidation step** between the panel's UNION and `## How you write back`. It must: (a) **dedup semantically across lenses** (the same gap found by 2–4 critics collapses to one); (b) **rank by (severity × number-of-lenses-that-found-it)** — state that cross-lens convergence is the precision signal (a gap multiple lenses independently hit is load-bearing); (c) re-seed **only the ranked load-bearing set** as `critic-found` + candidate GIVEN/WHEN/THEN scenarios; (d) the long tail goes under blind-spots / residue, **never padded into the spec**. Keep it qualitative (no script). Make `## How you write back` consume the consolidated set, not the raw union.
- Module: spec-toolkit/skills/completeness-critic/SKILL.md
- Files touched: spec-toolkit/skills/completeness-critic/SKILL.md
- Context paths:
  - spec-toolkit/skills/completeness-critic/SKILL.md
  - docs/spec-toolkit/dogfood/2026-06-12-completeness-critic-panel-dogfood.md
- Acceptance:
  - RED: `grep -iE "consolidat|cross-lens convergence|rank.*severity" SKILL.md` returns nothing.
  - GREEN: a consolidation step exists (dedup across lenses → rank by severity × cross-lens convergence → re-seed only the load-bearing set, tail to blind-spots), and write-back consumes the consolidated set. greps for `consolidat`, `convergence`, and `rank` (near severity) all succeed; no `scripts/` added.
- Dependencies: none
- Independent: false
- Brief item covered: "F-2 — consolidation step before write-back" (brief §Smallest End State item 2).

## Task 3 — F-3: overlap forcing line + version bump 0.2.1

- Description: (a) Add ONE line making the overlap-rate judgment a **reported** item in `## Output discipline — round summary` (the round summary must state the overlap judgment + whether the panel was diverse enough — turning the advisory diagnostic into a reported step). (b) Bump frontmatter `version: 0.2.0 → 0.2.1`. Do not touch other body sections.
- Module: spec-toolkit/skills/completeness-critic/SKILL.md
- Files touched: spec-toolkit/skills/completeness-critic/SKILL.md
- Context paths:
  - spec-toolkit/skills/completeness-critic/SKILL.md
- Acceptance:
  - RED: `grep "version: 0.2.1" SKILL.md` returns nothing (still 0.2.0).
  - GREEN: `grep "version: 0.2.1"` succeeds AND `grep "version: 0.2.0"` returns nothing AND the round-summary section reports the overlap judgment (grep -i "overlap" in the round-summary region succeeds, framed as a reported item).
- Dependencies: none
- Independent: false
- Brief item covered: "F-3 — overlap forcing line" + "Version 0.2.0 → 0.2.1" (brief §Smallest End State item 3 + version line).
