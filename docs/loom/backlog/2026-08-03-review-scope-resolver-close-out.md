---
name: 2026-08-03-review-scope-resolver-close-out
description: what the review-scope-resolver arc shipped, the two decisions its branch is waiting on, and the four-item queue that came out of it — recorded here because the session's own diagnosis was that a queue living only in conversation evaporates
status: OPEN
origin: the review-scope-resolver arc (loom-code 0.46.0, branch feat-review-scope-resolver, unpushed)
start: before the branch is pushed, or before the next arc begins — whichever comes first
---

## What shipped

`loom-code/scripts/review_scope.py` returns a branch's changed-file list and a
base-freshness verdict from the same call, so the check cannot be skipped while
still obtaining a scope. Four call sites across three skills stopped computing
scope independently; `requesting-code-review` hands its resolved scope down to
`requesting-docs-review` on both delegation paths, which resolves its own only
when none was supplied. Any failure to establish freshness refuses; a genuinely
stale base gets a ready-to-run `git rebase --onto` with both shas filled in.

**It narrows review SCOPE, not review JUDGMENT.** It stops a review running
against the wrong set of files. It says nothing about whether the review of
those files is correct. Those two were conflated repeatedly during the arc and
the CHANGELOG now separates them explicitly.

## The two decisions the branch is waiting on

The branch is complete and verified but **cannot honestly be pushed yet**:

1. **The docs arm's last verdict was NEEDS_REVISION.** Its three findings were
   fixed and each fix was mechanically verified, but no reviewer has passed the
   fixed version. `requesting-docs-review`'s convergence contract caps the loop
   at two rounds and permits a third **only on explicit user authorization**, so
   no third round was run. A review-pass gate marker cannot be minted from a
   NEEDS_REVISION verdict, and minting one on the orchestrator's own
   verification would be exactly the self-signed waiver the gate exists to
   prevent. Push therefore needs either an authorized round 3 or a knowing,
   recorded waiver.
2. **Push and PR are outward-facing.** They need the user's word regardless of
   the above.

Close-out verification that IS complete: the suite this branch runs against —
`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/` —
passes (806 at the time of writing; the figure moves with the suite, the command
does not); backlog index validate
and check, loom-memory integrity, living-spec index, Codex manifest sync, and
the skill-content version-bump gate all exit 0; every commit on the branch
carries retrievable memory trailers. (No commit count is stated: this entry is
itself committed, so any number written here is stale the moment it lands —
the same self-referential-count trap this arc hit four times before.)

## The queue this arc produced, in priority order

1. **The TDD backfill gap.** `tdd-iron-law`'s false-green diagnostic and its
   legacy-backfill section never reference each other, and the diagnostic's
   step 1 ("comment out the production code change") presumes a change that a
   backfill does not have. A backfill test always passes on first run, which is
   indistinguishable from a test that cannot fail. Two-sentence fix plus a
   version bump plus a cold-read check; this session produced a live case to
   test it against.
2. **PCE, forward-recording half only.** Phase Containment Effectiveness is
   already defined (`2026-07-27-phase-containment-effectiveness-...`) as the
   share of planning-origin defects caught before close-out. Recording it going
   forward costs almost nothing and answers "are the plan-stage gates catching
   anything, and which class do they miss". Its evaluation population as filed
   is investing-toolkit arcs only — widen it to any arc running the loom-code
   process, or loom-code arcs like this one never count.
3. **The repair-side sweep mechanism.** The rule "find every copy of a claim
   before editing any" now lives in
   `docs/loom/memory/enumerate-every-copy-before-editing-a-claim-and-name-the-leaks.md`,
   but nothing obliges a repairer to hit it — and this arc failed to follow it
   twice, once by the author who had written it hours earlier. A repairer-side
   pre-action or an unwrapping scan script would close the hard-wrap leak
   mechanically; the synonym leak stays open by nature and must be named rather
   than papered over.
4. **PCE's historical baseline — deferred, and it has a clock.** Reconstructing
   it means re-reading the ~35 MB of session transcripts the provenance audit
   was extracted from (2026-07-22 → 07-27, across three worktree project dirs).
   Those transcripts still exist as of 2026-08-03; the oldest surviving file in
   that directory is from 2026-07-04, so retention appears to be about thirty
   days. **If the baseline is wanted, it must be reconstructed before roughly
   2026-08-21.** The audit it depends on also has internal inconsistencies filed
   separately — three live, a fourth filed and then withdrawn as not a
   contradiction — and one of the live three is judgment-shaped rather than
   arithmetic.

## Residual notes carried, not fixed

- No mechanical check ties `review_scope.py`'s prose count of refusal shapes
  ("there are seven, exhaustive against `check_freshness`'s early returns") to
  the actual number of early returns. That number was wrong three times on this
  branch before it was right; nothing stops a fourth.
- `test_review_scope_docs_station.py` records its own residual gap in-line: no
  test in it distinguishes a conditional Step 1 from an unconditional one, and
  only a behavioural cold-read would.
- The module docstring's rationale for writing its own git helper leans on a
  `git-guard.py` analogy that is weaker than presented — that hook is genuinely
  stdlib-only, while this module already imports a public name from
  `loom_gate_markers`.
- `finishing-a-development-branch:100` still runs its own branch diff. That is
  a display read, not a routing decision, and was deferred deliberately (brief
  Open Question 1). Detached-HEAD handling was deferred the same way.
