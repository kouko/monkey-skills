# Weak-tier cold-reader dogfood — two-tier description rules (2026-07-14)

Rule text under test: `skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md`
as of commit 97932068 (post justified-exceedance codification — INCLUDES the
new-router strict path d3f49f99 and the exceedance clause).
Protocol: identical to coldreader.md (T9) but on weak tiers — fresh-context
agents given ONLY the rule text + two synthetic specs, no other context.
Requested at close-out by the user (T9 ran on the session/strong tier only).
Spec B is deliberately the hard case: a BRAND-NEW router with zero firing
evidence — probes Decision Log #1's strict path + fabrication resistance.

## Arms

| Arm | Model | Spec A (normal, csv-schema-diff) | Spec B (new router, zero evidence) | Fabricated evidence? |
|---|---|---|---|---|
| haiku | claude-haiku | 148 chars — in ≤150 target | 147 chars — stayed in NORMAL band, rationale cites "NEW with no firing evidence yet; no exception band opens without corpus/A·B run" | **none** ✅ |
| sonnet | claude-sonnet | 211 chars — 150–250 zone, correctly noted no justification comment needed under the soft line | 237 chars — normal band + full CONDITIONAL/N/A-loud wording; COMMENT rationale correctly scopes the evidence-note obligation to the ≤500 band only | **none** ✅ |

## Per-criterion grades

| Criterion | haiku | sonnet |
|---|---|---|
| (a) normal skill in-band | ✅ 148 | ✅ 211 (justified implicitly — under soft line) |
| (b) new-router STRICT path (no ≤500 without evidence) | ✅ explicit | ✅ explicit |
| (c) no fabricated firing-evidence note | ✅ | ✅ |
| (d) no synonym pairs / no identity beyond one-sentence WHAT | ✅ | ✅ |
| (e) triggers/conditions front-loaded, third person | ✅ | ✅ |
| (f) CONDITIONAL + N/A-loud announcement carried (spec B required it) | ⚠️ firing condition present, N/A-loud announcement MISSING | ✅ verbatim |

## Verdict

**PASS on the load-bearing properties, both tiers**: the strict
evidence-less-new-router path (the arc's subtlest rule) was applied
unprompted by BOTH weak tiers, with zero evidence fabrication and correct
band discipline. The exceedance/evidence machinery is weak-tier-legible.

Residual (single-tier, single-occurrence — recorded, not escalated):
haiku dropped Spec B's N/A-loud announcement wording. The requirement was
carried by the SPEC (the rulebook itself does not codify the CONDITIONAL
announcement convention — that lives in family conventions), so this reads
as a reader lapse on a spec detail, not a rule-text defect. Re-trigger:
if a second weak-tier reader drops N/A-loud when authoring a CONDITIONAL
description, add an explicit CONDITIONAL-announcement line to
description-design.md (two-occurrence rule).
