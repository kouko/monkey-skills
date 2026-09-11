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

## Reference run — 2026-09-11

Contract version: `SKILL.md` as of commit `d7d89f6d3`; `Record` section
digest `c7b0dcff`, the value pinned in `scripts/test_skill_contract.py`. Reader: one
fresh-context `sonnet` agent, no tools used.

**Verdict: PASS on all three criteria.**

| Criterion | Expected | Observed |
|---|---|---|
| Timing | Records on the open branch, before it closes, citing the contract | "recorded now, before this branch closes, on this same open branch — the contract says a fact already known while the branch is open… belongs in that branch" |
| Exception | Candidate 11, and only candidate 11, to a batched follow-up | Exactly candidate 11, explicitly batched |
| Scarcity | 0-2 RECORD of 11, and the reader checks its own count | 1 RECORD, and it checked the count against the contract's stated normal outcome unprompted |

### One disagreement with ground truth

Candidate 1 — an acceptance line written without measuring the baseline
first — is `RECORD` in ground truth and the reader marked it `REJECT`,
routing it to evidence as a finding about this change.

Both readings are defensible: the incident is bound to one change, the
rule it teaches is not. The disagreement is recorded rather than resolved
because the contract's bias here runs toward rejection, which is the
direction this clause was written to push. A reader that had marked eight
of eleven `RECORD` would be a failure; a reader that rejects one
borderline case is the clause working.

### What this run does not show

The reader was given the clause in isolation, so this measures the
wording, not whether an agent mid-change will remember to consult it at
all. That second question belongs to the moment the question gets asked,
not to this text.
