# Protocol — grade

Deterministic structural grading details, complementing `scripts/grade_draft.py`. The Python script handles file-level checks; this protocol documents the rationale for each check.

## Why deterministic-only at MVP

Per spec §3 decision Q9b, structural checks catch ~95% of "I forgot to fill X" mistakes without requiring Pearson-calibrated LLM rubric (which needs hand-graded baselines we don't have yet). Heavier LLM-rubric scoring is deferred to v0.4.0.1+ once 5-10 dogfood drafts give us calibration data.

## What grade_draft.py checks

1. **File presence** — both `<doc-type>.md` (privacy/tos/dpa/nda) + `compliance.md` exist
2. **No orphan placeholders** — `<doc-type>.md` has no `{{...}}` lingering (catches MERGE step omissions)
3. **Verdict coverage** — every `- [ ]` or `- [x]` line in `compliance.md` has a `**PASS**` / `**FAIL**` / `**TBD_<id>**` marker
4. **TBD canonicality** — every `TBD_<id>` used must appear in `references/pdpa-current-state.md` canonical OPEN list (rejects fabricated ids; LLM might invent `TBD_GDPR_72hr` which is wrong for Path A)
5. **Truncation guard** — `<doc-type>.md` byte-count > 500 bytes (catches LLM session timeout / context limit truncation)

## What grade_draft.py does NOT check (deferred)

- Semantic correctness of legal language (LLM rubric, post-dogfood)
- Statute citation URL liveness (templates are pinned at authoring; runtime fetch would be over-engineered)
- Optional-section appropriateness (e.g., did the LLM correctly omit 第三方 SDK when none declared?)
- Cross-mode consistency (e.g., did privacy and tos reference the same liability cap?)

## When grader emits FAIL

The pipeline halts. The COMPLY_CHECK step must re-run, addressing each FAIL reason. Common patterns:

| FAIL reason | Likely cause | Fix |
|---|---|---|
| `orphan template placeholder(s) in doc` | A `{{variable}}` was not resolved during MERGE | Re-run MERGE; check ASK_GAPS captured all required variables |
| `checklist line X has no verdict` | LLM forgot to substitute `{{verdict}}` for a checklist item | Re-run COMPLY_CHECK; emphasize "every item must end with PASS/FAIL/TBD_<id>" |
| `fabricated TBD id(s)` | LLM invented a new TBD identifier | Replace with a canonical id from `pdpa-current-state.md`; if a genuinely new deferred item exists, FIRST add it to the canonical list + tbd-migration-template.md before re-running |
| `possible truncation` | LLM output was cut off; doc too short | Re-run draft (entire pipeline); check session token budget |
| `missing compliance.md` | OUTPUT step skipped a file | Re-run OUTPUT |

## Exit codes

- 0 — all checks passed
- 1 — at least one structural failure (reasons on stderr)
- 2 — invalid invocation (wrong args, unknown mode)
