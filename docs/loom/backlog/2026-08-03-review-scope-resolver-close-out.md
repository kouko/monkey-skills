---
name: 2026-08-03-review-scope-resolver-close-out
description: what the review-scope-resolver arc shipped, and the queue that came out of it — recorded here because the session's own diagnosis was that a queue living only in conversation evaporates; the arc itself merged as PR #641, so only the queue is still live
status: OPEN
origin: the review-scope-resolver arc (loom-code 0.46.0), merged as PR #641, squash 2b8785d3
start: before the next arc begins — the queue below is what remains; the push gate this entry originally carried is spent
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

## The two decisions the branch was waiting on — both resolved

**Struck 2026-08-03.** This section described a live push gate on branch
`feat-review-scope-resolver`. That branch shipped: PR #641, squash `2b8785d3`,
now an ancestor of `origin/main`. Kept as a struck record rather than deleted
because the queue below is still live and because the shape is worth seeing —
the gate was real, it was resolved by an authorized third round plus the user's
word, and the section outlived the event it described by long enough for two
separate later edits to this file to pass over it untouched.

1. ~~**The docs arm's last verdict was NEEDS_REVISION.**~~ Resolved: an
   authorized round ran and the branch merged. The contract it names is
   unchanged and still governs — `requesting-docs-review` caps the loop at two
   rounds and permits a third only on explicit user authorization, a review-pass
   gate marker cannot be minted from a NEEDS_REVISION verdict, and minting one
   on the orchestrator's own verification would be exactly the self-signed
   waiver the gate exists to prevent.
2. ~~**Push and PR are outward-facing.**~~ Resolved: the user gave the word.

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
   twice, once by the author who had written it hours earlier.
   **Half done 2026-08-03.** The unwrapping scan script shipped as
   `scripts/claim_copy_sweep.py` — it normalizes whitespace on both sides so
   hard-wrapped copies cannot hide, and it partitions operative from frozen.
   What remains open is the OBLIGATION half: nothing requires a repairer to run
   it, left that way deliberately rather than added as another gate. The synonym
   leak stays open by nature (`--also` covers only phrasings you already know
   about) and must be named rather than papered over.
4. ~~**PCE's historical baseline — deferred, and it has a clock.**~~
   **WONTDO 2026-08-03, decided by the user.** Grounds and the accepted
   consequence are recorded in the PCE entry's own decision block
   (`docs/loom/backlog/2026-07-27-phase-containment-effectiveness-success-measure-for-plan-stage-fact-grou.md`);
   in short, the comparison's "after" side is empty and unscheduled under the
   filed population, the result would not be a rate at this n, and the useful
   half was answered more cheaply by
   `docs/loom/audits/2026-08-03-remediation-candidate-status-and-live-population.md`.
   The transcripts were not preserved, so the baseline is unreconstructible
   once they age out — accepted, not overlooked. **The forward-recording half
   of PCE is NOT closed by this** and still stands under its own entry.
   Two figures this item stated are also corrected there: the transcript volume
   ("~35 MB" — measured 2026-08-03 as 954 files / 303 MB in that window) and
   the retention basis. The provenance audit's internal inconsistencies remain
   filed separately and remain live; their trigger changed from "before
   computing the baseline" to "before anyone cites the audit for a count".

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
