Source: `requesting-code-review/SKILL.md` — maintainer-facing evidence extracted from §Verdict structure and §Process — serves `requesting-code-review`.

# Design evidence — author-facing, do NOT load at runtime

This file is author-facing: it exists for maintainers reviewing or redesigning this skill's panel-width and aggregation decisions. Runtime agents executing `requesting-code-review` do NOT load this file at runtime — the rules these fragments qualify already stay inline in SKILL.md; only the supporting citations and archaeology live here.

## Exit clause (originally §Verdict structure)

**Exit clause**: if false positives start accumulating, or the two arms are persistently byte-redundant (no incremental recall from the second arm), re-evaluate panel width against the G4 baseline.

## Panel union — supporting evidence (originally the tail of the §Verdict structure "Panel union" note)

The rule sentence itself ("each arm's own `verdict:` is advisory only — the gate verdict is produced by applying the aggregation rule above to the union of both arms' findings, never by picking one arm's verdict") stays inline in SKILL.md — it is pinned. This is its evidence tail: Evidence: G4 A/B — a single-Sonnet verdict missed the correct call 1-of-2 times, while union-aggregation over both arms reproduced the correct verdict with zero false positives across all 4 tested arms (`docs/loom/dogfood/2026-07-06-g4-sonnet-vs-fable-ab.md`).

## Process Step 2 — model-inherit calibration note

The rule it qualifies ("Do not pin a model on either dispatch — reviewers inherit the session model by design: that keeps the panel's tier matched to whatever the session actually runs") stays inline in SKILL.md §Process Step 2. Its calibration parenthetical: G4's evidence was measured on exactly the inherit configuration (see §Aggregation rule's "Panel union" note; G4's honesty clause cautions against extrapolating across tiers or diff types).

## Process Step 3 — union-merge supporting evidence

The rule it qualifies ("no cross-arm adjudication layer is needed") stays inline in SKILL.md §Process Step 3. Its supporting parenthetical: zero false positives measured across G4's 4 arms, report §Scorecard, plus the two same-day panel deployments recorded in PR #503/#504.
