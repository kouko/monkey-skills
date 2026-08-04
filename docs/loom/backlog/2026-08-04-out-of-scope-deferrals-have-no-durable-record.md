---
name: 2026-08-04-out-of-scope-deferrals-have-no-durable-record
description: an out_of_scope finding is surfaced once in chat and persisted nowhere -- nothing re-injects it into a later round, so a deferred defect is silently dropped the moment nobody acts on the verdict in the same session
status: OPEN
origin: loom-code 0.50.0 -- D5 retracted the "deferred on the record" overclaim; this entry is the retraction's follow-up, proposing the mechanism the honest wording says does not yet exist
start: when a docs-review out_of_scope finding is lost across a session boundary in practice, or when the next branch touches requesting-docs-review's Aggregation rule / Verdict structure sections
---

## The gap

`out_of_scope:` entries (Directive 2's block for what a delta-scoped round
declines to raise) carry no `severity:`, no `dimension:` and no `class:`.
`loom_gate_markers.py`'s `_FINDING_RE` (`^\s*-\s*severity\s*:`) is the only
thing that turns verdict text into an origin-ledger row, and it matches only
`- severity:` blocks at any indent -- an `out_of_scope:` entry never matches
it, by design (the fail-closed "missing class: counts as instruction" rule
must not sweep these back into the gate). So the entry is emitted in the
panel verdict text, which Step 4 writes to an unspecified temp file and Step
5 surfaces once in chat, and then nothing: no later round re-reads it, no
ledger row records it, no path a future session could grep. 0.50.0 retracted
the "surface them ... so a deferred defect is deferred on the record" wording
to the honest fact -- surfaced to the user with the verdict, persisted
nowhere; deferral survives only if the user or orchestrator acts on it in the
same session -- but a retraction is not a fix. This entry is that fix's
placeholder.

## Candidate mechanism: a severity-less ledger block type

The append pipeline already exists and already runs on every `review-pass`
invocation (D2, 0.50.0): `_record_origin_ledger_round` writes a row to
`<git-common-dir>/loom/origin-ledger.json` regardless of verdict, ordered
before the schema and verdict checks. The candidate: teach that writer a
second block type alongside the existing `- severity:` findings -- a
severity-less `out_of_scope` entry riding the same append, keyed the same way
(`branches[<branch>][].round`), so a later round (or a later session) can
read back what a prior round declined to raise without re-parsing chat
history. This is a candidate, not a decision: it inherits the round-COUNT
mint-index confusion the sibling entry below documents, and the ledger's own
staleness (rounds that never invoke the CLI append nothing) would apply to
this block type exactly as it applies to findings.

## Sibling candidate, noted not designed here

`validate_verdict_text` (`loom_gate_markers.py`) could gain a `reviewed_sha`
presence/format check as a schema-gate addition, parallel to its existing
`standards_version` / `verdict` / `dimension_scores` checks. That would catch
a missing or malformed `reviewed_sha` at mint time rather than downstream,
but it does not by itself solve persistence -- it is a validation tightening,
not a storage mechanism, and is noted here only because it shares this
entry's neighborhood (the verdict-text schema) and might be worth bundling
into whichever change picks a persistence mechanism.

## Relationship to the sibling entry

`2026-08-04-a-delta-scoped-round-cannot-resume-across-a-session.md` already
documents that `reviewed_sha:` and the round count have no durable carrier
across a session boundary, and lists three persistence options for that gap.
Whichever mechanism gets picked there is the natural place to also carry
`out_of_scope:` entries -- both are "verdict text nobody persists" problems
with the same candidate fix shape (extend the ledger writer, or have the
orchestrator write a known path). Do not open a third entry if that one gets
picked up first; fold this one in.

## Why it is not promised in the contract text

D5 (0.50.0) deliberately retracted the overclaim rather than build the
mechanism in the same branch -- the branch's stated direction was
retract-not-add. This entry is the durable trace that the retraction was not
the end of the story.
