# W18 native replays — results and limits

Immutable experimental evidence for the W18 candidate (per-candidate isolation
in the existing `skill-consistency-check` reporting caller). Recorded
2026-11-24. This file and its JSON companion are historical evidence, not a
product schema.

Authorization: user "ＯＫ" (2026-11-24) — three native local replays with
`gpt-6.1-sol` / reasoning effort `high`, same frozen input; any single replay
reproducing the same-class overbroad judgment rejects the W18 candidate;
W15–W17 failures and counts retained; no install, publish or merge.

## What ran

Three tool-mediated caller-review replays through `codex exec`
(`--sandbox workspace-write`, `--ignore-user-config`, network and web search
disabled, `approval_policy=never`), each a fresh session, on the same frozen
inputs. Unlike the 2026-11-09 inline diagnostic (which read source embedded in
the prompt and did not reproduce the failure), these executions read the files
through tools and ran the two deterministic scripts — the tool-mediated caller
context in which W17 failed.

| Run | Exit | Elapsed | Tool calls | Est. cost (USD) | Preregistered grade |
|---|---:|---:|---:|---:|---|
| trial (run 1) | 0 | 568 s | 84 | 0.7666 | passed |
| run-2 | 0 | 488 s | 104 | 0.8213 | passed |
| run-3 | 0 | 558 s | 62 | 0.8267 | passed |
| **total** | | | | **2.4146** | |

Requested model `gpt-6.1-sol`, provider openai, effort high. The executor JSONL
does not expose the actual backend identity; no identity is inferred.

Runtime: `git archive` of `skill-dev-toolkit/skills/skill-consistency-check` at
HEAD `9b76c250fa15c77f76fe0339b3f6016f4cba344e` (contains the W18 Step 6
items 2–3 text). Inputs: reconstructed from the W17 archive
`input_preimages`; **every one of 93 files was SHA256-verified against the
archive before dispatch** (targets from tracked git blobs at
`35a6be14…` for the original/skill-refactor and case-k targets and
`cd2c2c02…` for case-m; raw detector JSON from the committed case fixture and
the committed `research/scope-diagnostic-20261109/case-inputs.json`).

## Preregistered grading (written before results were inspected)

The grading spec was written to
`/private/tmp/toolkit-w18-replay-20261124-tools/grading-spec.md` before any
replay decision existed. Its criteria:

1. `original/read-1.json F1` status must be `excluded`; `confirmed` is the
   W17 overbroad false positive and vetoes the candidate instantly.
2. `F1`'s reason fails if it asserts an all-prose exclusion, claims the whole
   target falls outside entry scope without distinguishing the qualified
   category from the bare prose artifact type, or asserts a universal all-prose
   abort rule. It passes if it keeps any parenthetical/example within the
   category and scope its source assigns and grounds the exclusion in the
   original's asserted coverage.
3. `case-k HOLDOUT-K1` must be `excluded`; `case-m HOLDOUT-M1` must be
   `confirmed`.
4. Other original candidates have no preregistered gold label; they are
   recorded for the archive and are not graded by the veto rule.

## Result

| Candidate | run 1 | run 2 | run 3 | W17 (3 runs) |
|---|---|---|---|---|
| read-1.json F1 | excluded | excluded | excluded | excluded |
| read-1.json F2 | excluded | confirmed | excluded | excluded |
| simulate-1.json F1 | confirmed | confirmed | confirmed | excluded |
| simulate-1.json F2 | confirmed | confirmed | confirmed | confirmed |
| simulate-1.json F3 | excluded | confirmed | excluded | excluded |
| simulate-1.json F4 | excluded | excluded | excluded | excluded |
| simulate-1.json F5 | excluded | excluded | excluded | excluded |
| simulate-1.json F6 | confirmed | confirmed | confirmed | confirmed |
| simulate-1.json F7 | excluded | excluded | excluded | excluded |

Verdicts: all three runs report `needs-revision` for the original case,
`pass` for case-k, `needs-revision` for case-m — matching the W17 shape.
Raw candidate bytes were preserved in every case in every run (clause 3
antecedent checked by SHA256).

### Veto clause (preregistered)

**Not triggered in any run.** All three runs excluded `read-1.json F1`, and
all three reasons kept the parenthetical "writing style, prose, design feel"
inside the creative/non-deterministic category, rejecting the original's
disjunctive all-prose coverage rather than generalizing it. The W17 failure
class did not reproduce.

### Controls

All three runs: `HOLDOUT-K1` excluded, `HOLDOUT-M1` confirmed. Byte
preservation held on all six raw copies per run.

## Divergences that are NOT covered by the veto rule

These are recorded, not graded, per preregistration clause 4. They are
material to the change's Acceptance 9/11 and are handed to independent
blind source audits; this record does not pre-judge them.

1. **`simulate-1.json F1` confirmed in all three W18 runs, excluded in all
   three W17 runs.** The W17 semantic audits rated that exclusion PASS in
   every run. The candidate's `why` asserts an abort-versus-full-ensemble
   action conflict for creative/non-deterministic targets; the entry's
   Not-triggers text and the ensemble file's :165–166 instruction are the two
   quoted sides. Whether the entry's admission bar resolves the conflict (W17
   reading) or the ensemble instruction remains an unqualified direct
   instruction (W18 reading) is disputed; two audits were dispatched to
   adjudicate it blind.
2. **`read-1.json F2` and `simulate-1.json F3` flip between runs** (excluded in
   run 1 and run 3, confirmed in run 2). The structural-only PROCEED versus
   Q2/Q3 conflict is the common subject. This is cross-run instability on a
   candidate W17 audits rated QUALIFIED — neither direction is settled here.
3. `simulate-1.json F2` and `F6` are confirmed in all runs and all W17 runs;
   no divergence.

## Limits retained

- This is not accuracy testing, not a healed-Claude claim, not cross-model
  validation, and not release approval. The requested model identity is not
  observed; `--model unknown` was passed to the merger as in W17.
- The replay judges labels and reason fidelity on one frozen fixture plus two
  controls. It does not establish general caller correctness.
- The W17 candidate's rejection and its three executions remain unchanged
  evidence; W18 continues the same failed task without resetting counters.
- Audit verdicts are inputs to a decision, not a verdict on merging.
