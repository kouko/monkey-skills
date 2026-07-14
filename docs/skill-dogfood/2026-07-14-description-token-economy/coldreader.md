# Cold-reader dogfood — description-design.md (two-tier token economy)

- Date: 2026-07-14
- Plan: docs/loom/plans/2026-07-14-description-token-economy.md, Task 9 (REPORT-ONLY)
- Rule text under test: `skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md` (rule text as of 52a55ce3)
- Forward note: the routed Task-2 revision (new-router evidence path) landed as d3f49f99 three minutes after this record — MISREAD-1 describes the pre-revision text, by design.
- Method: one fresh-context `general-purpose` subagent; prompt contained ONLY the full rule text + the two synthetic specs below + the instruction "author the frontmatter description: for each spec per this reference document; return both descriptions with a one-line rationale each". No plan, no brief, no hint that the two-tier standard is new.
- Grading: done by the orchestrating (dispatching) agent, not the cold reader. Char counts independently recomputed via `python3 len()` on the rendered strings.

## Synthetic specs (authored for this test; not derived from any repo skill)

### Spec A — `csv-schema-diff` (normal skill)

> A skill that compares the schemas of two CSV files — column names, inferred
> types, column order — and reports added / removed / renamed / type-changed
> columns as a Markdown diff table. Runs a bundled Python script; no LLM
> inference in the diff itself. Intended for data engineers checking whether
> a vendor's monthly CSV drop silently changed shape before loading it into
> the warehouse. The repo it ships in has users who prompt in English,
> Traditional Chinese, and Japanese.

### Spec B — `using-pipeline-recipes` (router / CONDITIONAL skill)

> A family-entry router skill for the "pipeline-recipes" plugin family. It
> does no work itself: it checks intent and routes the user to one of three
> member skills (recipe-ingest / recipe-validate / recipe-publish).
> CONDITIONAL: it must only fire when the target repo contains a
> `.pipeline-recipes/config.yaml` file — in any repo without that file it
> must loudly answer "pipeline-recipes: N/A" with the reason instead of
> routing. Same mixed-language user base (English / Traditional Chinese /
> Japanese).

## Cold agent's verbatim outputs

### Spec A description (agent-claimed 229 rendered chars; independently verified: 229)

```yaml
description: >-
  Diff two CSV file schemas — added / removed / renamed / type-changed
  columns as a Markdown table. Use before loading a vendor's CSV drop
  into the warehouse, to catch a silently changed shape.
  Triggers: CSV schema / 欄位差異 / スキーマ差分.
```

Agent rationale (verbatim): "One-sentence WHAT (outcome, not workflow — the script's steps stay in the body), then the about-to-violate symptom `Use before loading … into the warehouse` (the moment the skill is useful; after the load it's too late), natural keywords a data engineer would type (CSV, schema, vendor drop, changed shape), plus a ≤50-char 中/日 keyword belt for the mixed-language repo. 229 chars — over the 150 target only because the belt and the four-way diff enumeration each buy distinct routing; under the 250 soft line."

### Spec B description (agent-claimed 248 rendered chars; independently verified: 248)

```yaml
description: >-
  Router for the pipeline-recipes family. Use when ingesting,
  validating, or publishing a pipeline recipe. CONDITIONAL: requires
  .pipeline-recipes/config.yaml — else loudly answers
  'pipeline-recipes: N/A' with the reason. Triggers: recipe / 配方 / レシピ.
```

Agent rationale (verbatim): "One trigger verb per routing branch (ingest / validate / publish — naming the verbs, not the member-skill workflow, avoids synonym duplication), and the CONDITIONAL gate + loud-N/A behavior lives in the description because on a no-fire the body never loads — the description is the only place that contract can execute; kept at 248, inside the normal 250 soft line, because the router exception band (≤500) requires firing evidence and a brand-new skill has none — widen it only after a corpus run or live A/B justifies it."

Agent's own closing flag (verbatim): "neither spec names a close sibling skill, so no explicit negative trigger ('Do NOT use for X') was added — if the repo later gains e.g. a full-data CSV diff skill, Spec A's description should grow one."

## Per-criterion grades (graded by orchestrator, in-band against the rule text)

| # | Criterion | Spec A | Spec B | Notes |
|---|---|---|---|---|
| a | Normal ≤150 (or ≤250 with justification) | PASS | n/a | 229 > 150 target but < 250 soft line; explicit justification given (belt + four-way enumeration buy distinct routing). Matches Principle 5's "target / soft lint line" framing. |
| b | Router ≤500 AND firing-evidence note/placeholder | n/a | PASS per rule text — see MISREAD-1 | 248 ≤ 500 but carries NO evidence note. Agent's reading: evidence is the *admission ticket to the exception band*; a new skill has no evidence, so it must stay ≤250 and may widen only after a corpus run / live A/B. Compliant with the rule as written ("no evidence, no exception"). |
| c | No English synonym pairs among triggers | PASS | PASS | A: single trigger surface "CSV schema" (the added/removed/renamed/type-changed enumeration is WHAT, not trigger variants). B: ingest / validate / publish = one verb per routing branch. Belts are the sanctioned carve-out. |
| d | No identity restatement beyond one-sentence WHAT | PASS | PASS (borderline noted) | A: sentence 1 = WHAT, rest = WHEN + triggers. B: "Router for the pipeline-recipes family." is the one-liner; the CONDITIONAL/N/A clause is firing contract, not identity — and the agent's argument (on a no-fire the body never loads, so the contract can only live here) is sound. Borderline: "else loudly answers … with the reason" edges toward behavior-spec, but it is a single contract clause, not a step sequence. |
| e | Triggers front-loaded | PASS | PASS | A: "Use before loading…" begins at char ~100. B: "Use when…" begins at char ~41. Both far inside the 1,536 truncation window. |
| f | Multilingual belt used or consciously skipped | PASS | PASS | Both used (spec stated mixed-language user base): A belt 37 chars, B belt 28 chars — both under the checklist's ≤50 cap. |
| — | (bonus) Third-person; no workflow steps | PASS | PASS | No first/second person; no "first A, then B" sequences. |

**Overall**: all applicable criteria met on both descriptions (one lettered criterion n/a each) under the rule text as written; zero hard misreads.

## MISREAD section

Hard misreads (cold agent misapplied the rule text): **0**.

Ambiguity findings (rule text left a case implicit; the cold agent had to infer — routed to Task 2, NOT fixed inline here):

1. **MISREAD-1 (ambiguity, not error) — new router with no firing evidence yet.** Principle 5 says the ≤500 exception band "REQUIRES a firing-evidence note (cite a corpus run or live A/B) — no evidence, no exception", but never says what the author of a *brand-new* router should do before any evidence can exist. The cold agent inferred: stay inside the normal ≤250 band and widen only after evidence arrives. That is a reasonable — arguably the intended — reading, but it is an inference, not a stated rule. The dispatching task's own grading criterion (b) instead expected a "firing-evidence note/placeholder" to appear. The two readings diverge exactly where the text is silent. **Routed Task-2 revision note**: add one sentence to Principle 5 (and mirror in the checklist bullet) stating the new-router path explicitly — e.g. "A new router with no evidence yet stays in the normal band (or ships a `firing-evidence: pending <planned run>` placeholder); it may claim the ≤500 band only after the cited run exists." Pick one mechanism; the current silence forces the reader to invent one.

No other confusion observed: the agent correctly used rendered-length auditing (YAML parse framing), the belt carve-out from the synonym rule, the WHAT-vs-WORKFLOW distinction, the about-to-violate pattern, and the negative-trigger checklist item (correctly judged n/a and said so).

## Scope compliance

This task wrote only this file. No edits to `description-design.md` or any other file; MISREAD-1 is routed to Task 2 via the orchestrator.
