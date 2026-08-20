---
name: 2026-08-02-origin-quote-tier-counts-have-no-durable-ledger
description: the origin-quote match-tier counts are written to a marker the next review-pass overwrites, so the observable the pre-registered stop rule depends on does not accumulate
status: closed
origin: Task 2 of the finding-origin-attribution arc (docs/loom/plans/2026-08-02-finding-origin-attribution.md), code-quality review rounds 1-2
start: before the origin field's ≥40-finding tally is read — or the moment the second arc using the field begins, whichever comes first
---

## Shipped (Tasks 7-8 of the same arc, commit 517a4777)

The gap this entry describes is fixed. `loom_gate_markers.py` now writes an
append-only, branch-keyed `origin-ledger.json` (schema documented in the
module's top docstring) on EVERY `review-pass` invocation — including
NEEDS_REVISION and schema-failure rounds, which mint no `review-pass.json` at
all. `payload["origin_quote_tiers"]` (described below as "what exists today")
is REMOVED from `review-pass.json`; the ledger supersedes it entirely.

The two further gaps this entry named are both closed by the same shape:

- **Population mismatch** — each ledger finding now carries its own `"arm"`
  (`"code"` / `"docs"`), so a consumer computing the stop rule filters to
  code-arm findings directly instead of trusting an undifferentiated counter.
- **Zero state** — every round leaves an explicit `"findings"` list (possibly
  empty-of-verified-quotes but never simply absent), so a round with zero
  verified quotes is no longer byte-identical to a marker written before the
  field existed.

One accumulation-correctness gap surfaced by whole-branch review after this
shipped: the ledger initially lived under `git rev-parse --git-dir`, which
forks a private, deletable copy per `git worktree` checkout instead of the
one shared ledger every checkout must append to. Fixed via
`resolve_common_marker_dir` (`git rev-parse --git-common-dir`) — no
separate backlog entry needed.

## What existed before (Task 2 shape — superseded, kept for context)

`loom_gate_markers.py` verifies a finding's `origin:` quote in two stages —
byte-exact first, then a normalised retry — and records which stage matched as
`payload["origin_quote_tiers"] = {"exact": n, "normalised": m}` in the
review-pass marker.

That is a **per-run snapshot**, and the docstrings now say so. `_write_marker`
writes one fixed filename via `os.replace` into untracked, per-checkout
`.git/loom/`, so the next `review-pass` on the same checkout destroys the
previous run's counts. Nothing in the repo reads the field.

## Why it matters

The tier split is not decoration. The user's kickoff decision chose two-stage
matching specifically so that the stop rule could be adjudicated later:

> once forty findings accumulate there is otherwise no observable that
> separates "no quotable origins existed" from "the matcher rejected true
> ones" — the tier count is that observable, and it must be collected from the
> first finding or not at all.

The stop rule is **pre-registered and uneditable after data lands**, and spans
roughly three arcs. A counter that survives one process on one checkout cannot
answer it. Backfill is impossible: the brief records that the quote is not
recoverable after the fact.

Two further gaps in the current shape, both measured:

- **Population mismatch.** The stop rule counts **code-arm** findings. The
  counter increments for any finding carrying a verified quote, including
  docs-arm ones. Verifying a docs-arm quote is correct; counting it into a
  code-arm-scoped tally is not.
- **Zero state.** A run with zero verified quotes and a marker written before
  the field existed are byte-identical — the key is omitted in both, and
  `schema` is still `1`. A consumer cannot distinguish them.

## The shape this repo already has

`review-rounds.json` is branch-keyed and never resets, and the 2026-07-30 plan
deliberately distinguishes it from the content-bound review-pass marker
(`docs/loom/plans/2026-07-30-review-round-ledger-and-bad-fix-recheck.md:168`).
That is the precedent to follow rather than re-derive.

## Why it was not built in Task 2

The kickoff decision's own downgrade clause permits shipping the matching rule
with no tier recording at all, so an accumulating ledger was never inside that
task's boundary. Task 2 shipped the machine-readable snapshot — cheap, honest
about what it is — and left the ledger here.
