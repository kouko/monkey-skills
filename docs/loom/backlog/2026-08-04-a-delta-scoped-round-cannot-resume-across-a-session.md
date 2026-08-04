---
name: 2026-08-04-a-delta-scoped-round-cannot-resume-across-a-session
description: the sha a delta-scoped review round needs is carried only by the dispatching orchestrator's context, so a round resuming in a new session falls back to unbounded
status: OPEN
origin: loom-code 0.49.0 — shipped with the in-session half working and the boundary stated in Directive 2 rather than papered over
start: when a docs-review round 2 actually resumes in a fresh session, or when the next branch touches `requesting-docs-review` Directive 2
---

## The item

Directive 2 scopes a round to `<previous round's reviewed_sha>..HEAD`. Within
one session the orchestrator carries that sha and the rule works. Across a
session boundary nothing does, so the round takes the `unbounded` fallback —
correct and safe, and also the exact outcome `reviewed_sha:` was added to
avoid.

`reviewed_sha:` being REQUIRED in the panel verdict does not close this on its
own: **no step persists that verdict anywhere a later session could find it.**
Step 4 writes it to "a temp file" at an unspecified path, and only on the
docs-only mint path; on a mixed branch it returns the verdict to the
orchestrator and writes nothing. Step 5 surfaces it in chat.

## What the existing ledger does and does not do — verified, because a review round got this wrong

A round-3 reviewer proposed closing this by naming
`<git-common-dir>/loom/origin-ledger.json`, on the grounds that it records
`head_sha` per round "written even on the NEEDS_REVISION round". Half right,
and the wrong half is the load-bearing one:

- The ledger is real, durable, append-only and cross-worktree, and it does
  carry `branches[<branch>][].head_sha` with `round`, `verdict` and
  `written_at`.
- `_record_origin_ledger_round` has exactly **one** caller
  (`loom_gate_markers.py`, inside the `review-pass` command), and the write is
  ordered before the schema and verdict checks — so a `review-pass` invocation
  on a failing verdict *would* be recorded.
- But nobody invokes `review-pass` on a `NEEDS_REVISION` verdict; there is no
  reason to, and it refuses to mint anyway. Measured on this repo's own
  ledger: branch `fix-docs-review-mechanisms` has **two** ledger rows against a
  review history of more rounds than that (the exact count is not retrievable —
  its audit defers the record to PR #644, which carries no review comments).

So the ledger records mint attempts, not review rounds. It therefore misses
every `NEEDS_REVISION` round — but not every round a round 2 might follow:
`PASS_WITH_NOTES` is a passing verdict that mints, and Step 6 keys round 2
on "the user fixed and wants re-review", not on a failing verdict. This
repo's own ledger shows both rows for `fix-docs-review-mechanisms` are
`PASS_WITH_NOTES`. So the ledger is usable and merely stale, and a stale
sha yields a WIDER range than the true one — the safe direction. The
cheapest fix below is therefore live, not ruled out.

A second trap for whoever mines the ledger: `_append_origin_ledger` writes
`"round": len(rounds) + 1`, so that field is a MINT index, not the review
round number. The two rows above read `round: 1` and `round: 2` while being
that branch's third-and-later rounds. Nothing in the field name says so.

## What a fix has to decide

Not a sentence — a persistence decision, one of:

- have the orchestrator write every round's verdict to a known path (and
  define that path, including on the mixed-branch return path);
- extend the ledger writer so a round is recorded when it is *produced*, not
  when a marker is minted;
- or accept the boundary permanently and delete the cross-session ambition
  from Directive 2, leaving `reviewed_sha:` as a human-facing convenience.

Whichever is chosen, the fail-closed direction stays: an unresolvable range
means `unbounded`, never a guess. An unbounded round is expensive but its
costs are visible; a wrong range suppresses findings nobody ever saw.

## Why it shipped open

0.49.0 was shipped to get the in-session half into real use. The failure mode
is fail-closed, and at the time of shipping none of this machinery had reached
a live reviewer anyway — the installed plugin was two versions behind, so the
whole delta-scope mechanism was still inert in practice.
