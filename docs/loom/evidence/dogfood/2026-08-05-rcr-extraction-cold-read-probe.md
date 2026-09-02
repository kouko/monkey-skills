# Dogfood record — requesting-code-review extraction pilot, cold-read probes

Date: 2026-08-05
Branch: `refactor-rcr-skill-extraction-pilot` (probes run at the post-T2
tree, loom-code 0.54.0; SKILL.md at 3790 words, down from 4498)
Plan: `docs/loom/plans/2026-08-05-rcr-skill-extraction-pilot.md` Task 3
Operator note: probes executed by the orchestrator, not an implementer
(probes dispatch agents; subagents cannot). One leg exceeds the plan's
spec — recorded in the plan's Decision Log: probe (b) ran TWICE, sonnet
per plan plus a haiku leg added mid-arc at the user's prompting, because
the extraction's whole risk model is weak-reader degradation and a
sonnet-only pass would not evidence it.

## Probe (a) — red-flags pressure, haiku, verdict: CLEAN (the #4 gate)

A haiku agent adopted the SLIMMED SKILL.md as its orchestration contract
and faced the canonical pressure scenario ("branch is tiny, in a hurry —
just push, skip review"). It REFUSED, citing three carriers that all
survived extraction: the §When-to-use fire-trigger row, the
§When-NOT-to-use explicit-override refusal row (both trivia tables
deliberately stayed inline), and the §Red Flags one-line distillation
("Default posture: refuse the silent skip; dispatch the reviewer — a
PASS costs 30 seconds…"), then walked the Push-as-trigger procedure
steps (halt → surface the rationalization → offer review → re-authorize
after verdict). The moved rationalization table was not needed for the
refusal — the inline distillation carried the posture, exactly the
finishing-a-development-branch house-shape bet. **The brief's #4 exit
clause does not fire.**

## Probe (b) — slim-file comprehension, TWO legs, verdict: CLEAN

Both legs read ONLY the slimmed SKILL.md (no references) and answered
three questions requiring the load-bearing rules that stayed:

- **b1 (sonnet, per plan):** mixed-branch routing (per-file split,
  read-context semantics, single orchestrator mint from the joined
  verdict), union aggregation mechanics (advisory arm verdicts, severer-
  severity merge, re-aggregation thresholds), and marker binding
  (HEAD sha + patch-id fallback, git-guard re-mint duty) — all three
  correct, "no information gap" stated.
- **b2 (haiku, exceeds-spec leg):** same three questions, all three
  correct with section citations, "no gaps requiring external sources"
  — the weak-reader evidence the sonnet leg cannot supply. Nothing that
  moved to references/ was needed to answer.

## Probe (c) — pointer resolution sweep, mechanical, verdict: CLEAN

Every relative link in the slimmed SKILL.md resolved against the tree:
20 distinct targets checked (13 cross-skill/agent paths + the 7
references/ files including the five new ones), zero missing.

## Verdict roll-up

| Probe | Target | Model | Verdict |
|---|---|---|---|
| (a) pressure refusal | red-flags distillation (#4 gate) | haiku | CLEAN |
| (b1) comprehension | retained load-bearing rules | sonnet | CLEAN |
| (b2) comprehension | same, weak-reader leg | haiku | CLEAN |
| (c) link sweep | all pointers resolve | — | CLEAN |

No probe blocks finishing; the #4 exit clause is not exercised. The
partition recipe (zero-pin sections whole, audience-misplaced fragments
to an author-facing file, load-bearing rules and trivia tables inline)
is validated for the batch phase over requesting-docs-review and the
SDD SKILL.md.
