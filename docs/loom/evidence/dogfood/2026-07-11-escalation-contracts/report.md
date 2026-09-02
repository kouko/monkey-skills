# Dogfood report — escalation interface / decision-log / acceptance-surface / appetite contracts

**Date**: 2026-07-11
**Plan**: docs/loom/plans/2026-07-11-escalation-interface-contracts.md, Task 6
**Shipped-commit anchor**: branch `feat-escalation-interface-contracts` @ `116a300b137fff9c94fc559a372426c3cacf331f` (this report certifies the branch HEAD at report time)

## Method

Pattern: `docs/loom/memory/process-mechanism-dogfood-via-coldreader-real-commits.md`
— dogfood a shipped process RULE (not a whole skill's triggering/output)
by handing a fresh-context, blind agent ONLY the rule text and a
realistic case, then checking it decides + executes the correct branch.

Adapted for this gate: **synthetic cases** in place of sandbox git
commits (these four contracts are decision-routing rules over
plan/branch content, not mechanical file-scope rules — a synthetic
plan/branch/PRINCIPLES.md fixture exercises the same "decide + execute
the correct branch, cite the sentence that justified it" bar without
needing a live git history). **One probe per contract** (four
contracts landed in Tasks 1-5; one cold-reader per contract, not one
per file). All four probes were orchestrator-dispatched, fresh-context
`sonnet` agents given only the shipped contract text plus one synthetic
case — no probe saw this plan, the architecture doc, or another
probe's fixture.

## Per-probe results

| # | Contract | Input given to reader | Expected | Observed | Verdict |
|---|----------|------------------------|----------|----------|---------|
| 1 | Kickoff briefing (Task 2) | `loom-code/skills/writing-plans/references/kickoff-briefing.md` + synthetic 3-task plan (datastore choice / cache-key rename / telemetry-vendor choice), no PRINCIPLES.md. Fixture: `probe1-plan.md` (scratchpad, non-committed) | Classify each decision via the two-axis test; brief the one-way-door hit(s); silently log the two-way-door hit to the plan's Decision Log; apply the no-PRINCIPLES default (brief all one-way hits) | Classified datastore=top-right→brief; cache-key=bottom-left→silent+Decision-Log entry (correctly noted the append happens during SDD execution, not at kickoff); telemetry=top-right→brief. Produced a correctly formatted batched briefing (plain-language stakes → 2 options with product consequences → recommendation, ask inline). Applied the no-PRINCIPLES default correctly. | **PASS** (see fixture-ambiguity note below) |
| 2 | SDD exception + Decision Log (Task 3) | `subagent-driven-development/SKILL.md` + its pointers + two synthetic mid-implementation events (Event A: session storage local vs cloud, schema bake-in; Event B: retry backoff 3→5, one-line revert, invisible) | Event A escalates via the two-axis test at the §f exception point with a full brief-before-asking briefing; Event B does NOT escalate, and instead produces a correctly-shaped Decision Log entry | Event A: escalated at the §f exception point, correctly identified the complex-fork bar, produced a full 6-block brief-before-asking briefing with recommendation + conditional reversal. Event B: NOT escalated; produced the record `N. chose to raise the HTTP retry backoff from 3 attempts to 5 with jitter because CI's network is slow… — cost-of-change: the day you want fewer or faster retries, this choice costs a one-line config change`, targeted at the plan's `## Decision Log` with the correct per-task commit cadence. Correctly distinguished bottom-left (fully silent) from top-left (mentioned in the completion report). | **PASS** |
| 3 | Acceptance surface (Task 4) | `finishing-a-development-branch/SKILL.md` + `ui-verification/SKILL.md` + a synthetic finished search-feature branch with UI | Product-language completion report leading with user-facing behavior; ui-verification's state walkthrough as the acceptance narrative; mechanical evidence (SHA/test count/review verdict) demoted to a footer | Produced a product-language completion report leading with what search now does for the user; ui-verification's 6-state walkthrough presented as the acceptance narrative; the deferred offline-search state honestly flagged as intentional; commit SHA / 87-test count / review verdict all sunk to a footer sub-line | **PASS** |
| 4 | Appetite dial (Task 5) | `kickoff-briefing.md` + synthetic PRINCIPLES.md with an appetite entry. Fixture: `probe4-principles.md` (scratchpad, non-committed) | Locate the entry via the scoped-region contract; apply the dial without re-asking on a two-way-door hit already covered by the entry; one-way hits still collected/briefed; no-PRINCIPLES sub-case defaults to collection only | Located the entry via the scoped contract (Engineering Principles region, incl. the region-runs-to-EOF edge); D1 (one-way) → briefed; D2 (two-way, mid-arc) → refused to re-ask, citing the appetite entry verbatim per judgment-rubrics §3(c); no-PRINCIPLES sub-case handled exactly (default expands one-way collection only, never two-way briefing — D2 still logged, not asked) | **PASS** |

**Overall**: 4/4 PASS, zero fold-backs required.

## Fixture-ambiguity note (probe 1 — honest limitation)

The probe-1 fixture's telemetry-vendor-choice item was authored to
land in the two-axis test's **bottom-right** cell (visible × two-way
door — the cell this gate wanted independently discriminated, since
probe 1's other two items already covered top-right and bottom-left).
The cold-reader instead classified it **top-right** (brief), reasoning
that vendor data-egress terms hit "future product option space (cost
structure, data availability)" under Axis A. On inspection this is the
more faithful SSOT reading of the fixture's stated facts, not a reader
error — but it means **both** populated cells in this probe route to
"brief," so the bottom-right cell was not independently discriminated
by probe 1. This is a fixture-authoring gap, not a contract-behavior
gap: the reader applied the two-axis test correctly to the text it was
given. Not treated as a fold-back (no contract wording is implicated);
flagged here per Rule 12 (fail loud on what was and wasn't actually
exercised) and left as an open item for a future dogfood round that
wants to isolate the bottom-right cell specifically (e.g. re-author the
fixture with an explicitly low-visibility framing).

## Fold-backs

None required. All four probes PASS on first dispatch; no contract
text was revised as a result of this gate.

## Fixture paths (ephemeral, not committed)

- `/private/tmp/claude-501/-Users-kouko-GitHub-monkey-skills/033aefba-2dd2-47eb-b13b-c3e304730565/scratchpad/dogfood-fixtures/probe1-plan.md`
- `/private/tmp/claude-501/-Users-kouko-GitHub-monkey-skills/033aefba-2dd2-47eb-b13b-c3e304730565/scratchpad/dogfood-fixtures/probe4-principles.md`

Probes 2 and 3 used inline synthetic scenario descriptions (no
standalone fixture file) alongside the shipped SKILL.md text, per the
scope given to each probe's dispatch.
