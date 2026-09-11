# record-timing — frozen reference run

This is the dilution guard for the `Record` operation's **When** and
**How much** clauses. It is not automated and it does not run in CI.

Two different failures can happen to those clauses, and they need two
different guards:

| Failure | Guard | Runs |
|---|---|---|
| A clause is deleted | `scripts/test_skill_contract.py` | every push |
| A clause is kept but softened until it no longer steers anyone | this eval | when the clauses change |

A string assertion cannot detect the second: a rewrite that keeps the
required elements and drains their force stays green. Only a reader can
tell, so the guard is a reader.

## Method

Give a fresh agent the `Record` section of `SKILL.md` verbatim and
nothing else — no repository access, no search, no prior context — plus
the situation and the eleven candidates in `record-timing-cases.json`.
Ask for three answers in order: when and on which branch it would record;
a verdict per candidate; and whether its own RECORD count matches what
the contract calls the normal outcome.

Re-run this whenever the **When** or **How much** clause changes, and
update the run below with the new result and an explicit reason.

Nothing about prose makes that re-run happen on its own, so it is wired
to a digest. `scripts/test_skill_contract.py` pins the sha256 of the
whitespace-flattened `Record` section; any edit to it turns that test
red with a message naming this file. Updating the digest without
re-running the eval is the single move that defeats the guard, and it
costs less than the dispatch it skips — which is exactly why it is worth
saying out loud here.

## Reference run — 2026-09-11 (second, current)

Contract version: the `Record` section after Round 3 added the
digest-exhausted case to the exception sentence; section digest
`33a40772`, the value pinned in `scripts/test_skill_contract.py`.
Twelve candidates. Reader: one fresh-context `sonnet` agent, no tools used.

This run exists because the digest pin demanded it. Round 3 edited the
exception sentence, the pin went red naming this file, and the honest
response was to re-run rather than to update the number — which is the one
move that defeats the guard, and the first time it was tested on the person
who built it.

**Verdict: PASS on all three criteria.**

| Criterion | Expected | Observed |
|---|---|---|
| Timing | Records on the open branch, before it closes, citing the contract | "before the branch closes, on this same open branch/PR — the contract says a fact already known while the branch is open… belongs in that branch, never a separate post-merge branch opened only to write it down" |
| Exception | Candidate 11, and only candidate 11, to a batched follow-up | Exactly candidate 11, explicitly batched |
| Scarcity | 0-2 RECORD of 12, and the reader checks its own count | 2 RECORD, and it not only checked the count but judged 2 "slightly above" the stated outcome and named which row it would drop — it corrected toward fewer, unprompted |

### Where the two runs disagree, and where each disagrees with ground truth

Neither run matched ground truth exactly, and they did not agree with each
other. That is the finding, not a flaw in it.

| Candidate | Ground truth | Run 1 (11 candidates) | Run 2 (12 candidates) |
|---|---|---|---|
| 1 — an acceptance line written without measuring the trunk | RECORD | REJECT → evidence | REJECT → evidence |
| 2 — a fidelity test silently skipping in its own CI job | REJECT | REJECT → evidence | **RECORD** |
| 4 — worktree cleanup by pattern match destroying others' work | RECORD | RECORD | RECORD |
| 12 — an assertion scoped wider than the clause it defends | RECORD | not present | REJECT → evidence |

Only candidate 4 is stable across both runs and ground truth. The rest move,
and they move in both directions, which says the clause draws a line the
readers can apply consistently in aggregate — both runs landed inside the
scarcity band and both routed the post-merge exception correctly — while
individual borderline calls stay genuinely borderline.

The direction of the error matters more than its size. A reader marking
eight of twelve recordable would be the failure this clause exists to
prevent. Both runs erred toward rejection, and run 2 volunteered a further
rejection when it checked its own count. That is the clause working.

Candidate 12 is the one worth watching: it is the defect this change's own
review episode produced four times, and the reader classified it as a bug
fixed inside the change rather than a durable lesson. Defensible — it *was*
fixed here — and it is recorded anyway, because recurrence across four
independent instances is what makes a defect a lesson rather than an
incident. If a later run also rejects it, the clause is under-weighting
recurrence and should say so explicitly.

### What this run does not show

The reader was given the clause in isolation, so this measures the wording,
not whether an agent mid-change will remember to consult it at all. That
second question belongs to the moment the question gets asked, not to this
text.
