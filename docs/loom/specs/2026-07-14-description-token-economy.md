# Brief: Description token-economy — Pocock rules port + standard reconciliation + loom-* sweep

Date: 2026-07-14
Origin: user goal「降低 token 成本＋agent 寫的 description 都太長」→ Pocock 最新方法檢視 arc 方案 A（user-approved option (b) two-tier calibrated by industry measurement）.

## Problem

Every session pays standing context cost for ALL skill descriptions; loom-* alone
carries 10,770 chars across 26 skills, 12 of them over the house 250-char cap
(worst: 1,081 = 4.3×). Future descriptions keep growing because the standing
rules are self-contradictory and never enforced at authoring time:

| Rule location | Number stated | Status |
|---|---|---|
| skill-creator-advance SKILL.md §House description standard | target ≤150 / hard cap 250 | drifted vs reference |
| skill-creator-advance references/description-design.md Principle 5 | 100–250 / ceiling ~500 | drifted vs body |
| domain-teams CHK-SKL-001 | ≤250 + 30-word floor | gate-time only; loom-* never passed through it |
| PR #506 live evidence (research-toolkit) | longer + trigger-worded descriptions raised firing 2/13→5/13 | collides with any tight cap |

**Root fact (industry research, 2026-07-14)**: the 250 figure descends from a
Claude Code listing cap introduced in v2.1.86 and RESCINDED in v2.1.105
(raised to 1,536 combined description+when_to_use). Our house cap is
stale-fact drift. Official guidance has NO recommended length — only the
1,024-char spec max and the 1,536 listing truncation.

## Users

- kouko + any future agent session authoring or editing a skill via
  skill-dev-toolkit (skill-creator-advance) — weak-to-strong model tiers.
- Every session in this repo (and any repo with these plugins) paying the
  standing description cost.

## Industry grounding (measured 2026-07-14, n=88 shipped skills)

- Medians: obra/superpowers 106 / mattpocock 156 / anthropics official 304 /
  planning-with-files 339. Community norm 80–250.
- EN+JA community tiering agrees: 60+ skills in collection → ≤130 chars
  (this repo's listing has 130+ skills → tightest tier applies).
- Conditional/router skills legitimately run 400–1,000+ (Anthropic's own
  `claude-api` is 1,068 — over their own spec max). A single cap penalizes
  exactly the kind that needs length.
- NO source anywhere ships trigger-accuracy data — our firing-corpus A/B is
  ahead of industry practice and is the guard for this change.

## Decision (user-approved: option (b) two-tier)

1. **Reconcile the standard into ONE SSOT** — `description-design.md`
   Principle 5 becomes the number authority:
   - Normal skills: **target ≤150 chars** (Pocock median 156 / community
     large-collection tier ≤130 neighborhood); 250 becomes a soft lint line,
     NOT a hard cap.
   - Router / CONDITIONAL skills: **exception band ≤500**, admission
     requires a firing-evidence note (cite corpus run or live A/B) — no
     evidence, no exception.
   - Record the 250-rescission provenance (v2.1.86→v2.1.105) so the number
     never re-fossilizes.
   - SCA SKILL.md body + CHK-SKL-001 point at the SSOT; body edit net ≤0
     words (4,497/4,500 — 3 words headroom).
2. **Port Pocock's quality rules** (HOW to cut, complementing the caps'
   HOW MUCH) into `description-design.md`: one trigger per branch /
   synonyms = duplication / cut identity already in the body, plus the
   context-load vs cognitive-load framing. Explicit carve-out: the existing
   Principle 6 multilingual keyword belt (中/日 triggers) is NOT
   synonym-duplication — distinct routing surfaces stay.
3. **Sweep loom-* over-cap descriptions** under the new standard, guarded by
   firing-corpus A/B:
   - Corpus-covered skills: baseline run → rewrite → re-run, no regression.
   - Uncovered top offenders (loom-discovery ×3, loom-pipeline ×2): EXTEND
     direct-ask.jsonl with 3–5 entries each FIRST, then sweep.
4. **Cold-reader dogfood** the new rule text (quality floor: a cold agent
   authors one description under the new rules and lands in-band).

## Smallest End State

- `description-design.md` = single number authority, Pocock rules folded in,
  drift resolved; SCA body + CHK-SKL-001 consistent with it.
- All 26 loom-* descriptions in-band (normal ≤150-ish, router/CONDITIONAL
  ≤500 w/ evidence notes); firing A/B shows no trigger regression.
- Corpus covers loom-discovery + loom-pipeline.

## Current State Evidence

- Forward: SCA body cites the standard at
  `skill-dev-toolkit/skills/skill-creator-advance/SKILL.md:96,100-108,435-451`
  (§Description Best Practices pointer + §House description standard);
  optimization loop consumes it at `:464`.
- Reverse (SSOT direction): `references/description-design.md` is the design
  reference (2,333 words, §Six principles at :57–163); the RATIONALE doc
  `docs/skill-mining/2026-06-19-skill-description-standard.md` is cited at
  SKILL.md:438 — it predates the v2.1.105 rescission (stale ancestor).
- Error: no mechanical enforcement anywhere; CHK-SKL-001
  (`domain-teams/skills/skill-team/checklists/skill-completeness-checklist.md:16`)
  fires only in skill-team gates.
- Data: loom-* description lengths measured 2026-07-14 — top offenders
  using-loom-discovery 1,081 / using-loom-pipeline 1,049 / loom-memory 1,005 /
  user-insights 927 / business-value 632 / product-principles 585 /
  ui-verification 582; total 10,770 chars.
- Boundary: firing corpus `docs/loom/firing-corpus/{direct-ask,goal-oriented,near-miss,research-asks}.jsonl`
  covers design-side stations + loom-code router + research-toolkit; NO
  coverage for loom-discovery / loom-pipeline (the heaviest offenders).
  Harness: `loom-code/scripts/loom_firing_harness.py` (trap #6: fired-skill
  grading alone can miss design-side recommendation surfacing — transcript
  check applies to goal-oriented reuse, not this arc's direct-ask extension).

## Alternatives considered (researched, rejected)

- (a) Single 250 hard cap: directly contradicted by shipped practice
  (Anthropic's own conditional skills 400–1,000+) and #506 evidence. Rejected.
- (c) Quality rules only, no number reconciliation: leaves three
  contradictory numbers drifting; next authoring agent still guesses. Rejected.
- Full Pocock description minimalism (~106–156 median across the board):
  assumes strong-model + small collection; our 130+ skill listing and
  multilingual triggering need the two-tier shape. Adapted, not adopted.

## What Becomes Obsolete

- The three-way number contradiction (SCA body 150/250 vs reference 100–250/500
  vs CHK-SKL-001 250) — replaced by one SSOT + pointers.
- The stale 250-as-hard-cap fact and its rationale doc's unqualified authority
  (rationale doc gets a dated supersession note, not deletion).

## Out of Scope

- Repo-wide sweep of non-loom plugins (investing-toolkit etc.) — methodology
  ships now, sweep rides next touches.
- New CI mechanical gate for description length (CHK-SKL-001 remains the
  gate-layer check; revisit only if authoring-time violations recur post-ship).
- Body word-count budgets (CHK-SKL-010) — different lever, untouched.
- `when_to_use` frontmatter field adoption — separate design question.

## Open Questions

- None blocking. Per-skill judgment (which trigger words are load-bearing)
  resolves inside the sweep tasks via A/B evidence.

## Design-side on-ramp

N/A — tooling/process increment, Axis 0 negative guard applied (silent skip).
