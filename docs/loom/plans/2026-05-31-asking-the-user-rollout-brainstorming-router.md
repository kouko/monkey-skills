# Plan: asking-the-user three-gate rollout to brainstorming + router (Pattern ③)

Source brief: docs/loom/specs/2026-05-31-asking-the-user-rollout-brainstorming-router.md
Total tasks: 4   ← uncapped; width is fine
Critical-path depth: 3 (≤5)   ← T1 → T3 → T4
Execution order: parallel-where-possible (Task 1 ∥ Task 2; Task 3 after 1; Task 4 after all)
Plan-document-reviewer verdict: PASS (2026-05-31, 14/14)

## Task 1 — brainstorming: native gate-③ phrasing + ①/② cross-ref
- Description: In `brainstorming/SKILL.md`, augment the existing "ask at most one axis
  per `AskUserQuestion` call" guidance (in the §5-axis intro) with the THREE gate-③
  phrasing rules brainstorming currently lacks, written natively/tailored to the
  axis-question context: (a) **open with a one-line state anchor INSIDE the
  `AskUserQuestion` `question` field** (not only chat prose above it); (b)
  **outcome-not-mechanism** (each option says what the user gets, not internal
  machinery); (c) **numbers carry their meaning** (translate raw counts/symbols). Add
  ONE sentence naming that gate ① already lives in Axis 1 (the "confident JTBD read →
  don't re-ask" rule) and gate ② in Axis 4 (research-then-"My take: Recommend"), so the
  three gates read as a coherent set. Do NOT re-add rules brainstorming already has
  (≤4-options, one-axis-per-call, plain-language-summary). Do NOT add a `## Asking the
  user` block or reference SDD's file (Pattern ③ — native only).
- Module: code-toolkit/skills/brainstorming/SKILL.md
- Files touched: code-toolkit/skills/brainstorming/SKILL.md
- Context paths:
  - docs/loom/specs/2026-05-31-asking-the-user-rollout-brainstorming-router.md
  - code-toolkit/skills/brainstorming/SKILL.md
  - code-toolkit/skills/subagent-driven-development/SKILL.md  (gate-③ rule wording to mirror, tailored)
- Acceptance:
  - RED: `grep -ci "state anchor\|outcome, not mechanism\|numbers carry" brainstorming/SKILL.md` returns 0.
  - GREEN: the 3 gate-③ rules present near the one-axis-per-call guidance (state-anchor-
    inside-`question`-field, outcome-not-mechanism, numbers-carry-meaning); one sentence
    maps ①→Axis 1 and ②→Axis 4; no `## Asking the user` heading added; no reference to
    another skill's file (`grep -c "subagent-driven-development/SKILL.md\|requesting-code-review/SKILL.md"` stays 0 in the new text); ≤4-options / one-axis / plain-summary NOT
    duplicated; SKILL.md body within ~6,000-token budget (`wc -w`); validate-skill-folder hook clean.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State item 1 (brainstorming native gate-③ + ①/② cross-ref).

## Task 2 — router: one-line downstream-gates pointer in rule #5
- Description: In `using-code-toolkit/SKILL.md` rule #5 ("Research before asking", which
  is gate ② at the routing level), append a one-line pointer that the full asking-the-user
  discipline — gate ① (whether to ask: skip reversible/inferable; confirm outward) and
  gate ③ (plain phrasing) — is enforced in the downstream skills (`brainstorming` /
  `subagent-driven-development` / `requesting-code-review`). One sentence; no block, no
  duplication of the gate definitions (pointer only).
- Module: code-toolkit/skills/using-code-toolkit/SKILL.md
- Files touched: code-toolkit/skills/using-code-toolkit/SKILL.md
- Context paths:
  - docs/loom/specs/2026-05-31-asking-the-user-rollout-brainstorming-router.md
  - code-toolkit/skills/using-code-toolkit/SKILL.md
- Acceptance:
  - RED: `grep -ci "gate ①\|gates ①\|asking-the-user discipline\|enforced in" using-code-toolkit/SKILL.md` returns 0.
  - GREEN: rule #5 carries a one-line pointer naming gates ①/③ enforced in brainstorming /
    SDD / requesting-code-review; rule #5's existing research-before-asking text intact;
    no full gate block added; token budget intact; hook clean.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State item 2 (router one-line downstream pointer).

## Task 3 — #355 brief: Cross-skill rollout SSOT note
- Description: Append a short "Cross-skill rollout" section to the existing concept-SSOT
  doc `docs/loom/specs/2026-05-31-asking-the-user-three-gate-redesign.md`,
  recording where each of the 4 skills carries the three gates and how each tailors them:
  SDD (full block, all 3 gates), requesting-code-review (lighter gate ② + verdict-boundary
  note), brainstorming (① via Axis 1, ② via Axis 4, ③ native phrasing rules), router
  (gate ② via rule #5 + downstream pointer). This keeps the mirror-principle concept SSOT
  current — no new SSOT doc created.
- Module: docs/loom/specs/2026-05-31-asking-the-user-three-gate-redesign.md
- Files touched: docs/loom/specs/2026-05-31-asking-the-user-three-gate-redesign.md
- Context paths:
  - docs/loom/specs/2026-05-31-asking-the-user-rollout-brainstorming-router.md
  - docs/loom/specs/2026-05-31-asking-the-user-three-gate-redesign.md
- Acceptance:
  - RED: `grep -ci "Cross-skill rollout" 2026-05-31-asking-the-user-three-gate-redesign.md` returns 0.
  - GREEN: a "Cross-skill rollout" note present listing all 4 skills + their gate carriage/
    tailoring, consistent with Task 1's actual brainstorming change.
- Dependencies: Task 1 completes first
- Independent: false  # doc-mirrors-the-change: the note records how brainstorming (Task 1)
    carries gate ③; disjoint file from Task 1, but a genuine doc-mirrors-code semantic
    dependency — deliberately sequential per the disjoint≠independent guard.
- Brief item covered: Smallest End State item 3 (augment existing #355 brief as concept SSOT).

## Task 4 — Version bump 0.14.1 → 0.15.0 + CHANGELOG
- Description: Bump code-toolkit `0.14.1` → `0.15.0` (minor — additive asking-the-user
  guidance in a skill, consistent with PR #355's 0.13.0 minor) in plugin.json, and add a
  `[0.15.0]` CHANGELOG entry describing the Pattern-③ rollout (brainstorming native gate-③
  + ①/② cross-ref; router pointer; #355 brief as concept SSOT), noting NO cross-skill
  reference / NO distribute-script / NO copied block. No prior-version backfill.
- Module: release metadata (plugin manifest + changelog)
- Files touched: code-toolkit/.claude-plugin/plugin.json, code-toolkit/CHANGELOG.md
- Context paths:
  - code-toolkit/.claude-plugin/plugin.json
  - code-toolkit/CHANGELOG.md
  - docs/loom/specs/2026-05-31-asking-the-user-rollout-brainstorming-router.md
- Acceptance:
  - RED: `grep '"version": "0.14.1"' plugin.json` matches; no `[0.15.0]` in CHANGELOG.
  - GREEN: plugin.json version `0.15.0` (valid JSON); CHANGELOG `[0.15.0]` entry naming the
    Pattern-③ rollout + the skill-independence approach + brief pointer.
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: false
- Brief item covered: Open Question 1 (version bump 0.14.1 → 0.15.0).

## Notes
- Wave 1: Task 1 ∥ Task 2 (disjoint files — brainstorming/SKILL.md vs using-code-toolkit/
  SKILL.md — no semantic dep → both `Independent: true`). Critical-path depth = T1 → T3 →
  T4 = 3.
- Task 3 is `Independent: false` despite a disjoint file: it records Task 1's brainstorming
  change (doc-mirrors-code), so it's sequenced after T1 per the disjoint≠independent guard.
- Doc-only skills: no pytest; acceptance = grep-diagnostic + validate-skill-folder hook +
  token budget. Behavioral validation (new gate-③ rules don't contradict brainstorming's
  existing one-axis/≤4 guidance) is a review-stage check.
- Pattern ③ invariants the reviewers must enforce: NO `## Asking the user` block added to
  brainstorming; NO cross-skill file reference; NO distribute-script; NO re-adding rules
  brainstorming already has.
