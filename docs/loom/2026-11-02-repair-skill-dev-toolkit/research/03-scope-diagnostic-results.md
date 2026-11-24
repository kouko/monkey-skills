---
title: "Measured source-condition diagnostic"
type: loom-research
status: concluded
created: 2026-11-09
updated: 2026-11-09
change: 2026-11-02-repair-skill-dev-toolkit
tags:
  - loom/research
---

# Measured source-condition diagnostic

## Question and scope

Execute the [diagnostic design](02-scope-diagnostic-design.md) to ask whether
literal excerpts or checked source premises help preserve the original claim.
This is a reporting-stage, inline-source experiment, not an installed-skill,
detector-routing, merger or complete host replay. Product HEAD is
`c66424d387584c8ddb8c9dd109d15bfbd08b6802`. User authorized execution with
"開始實測吧". No product edit, install, publication or merge is authorized here.

## Method and rationale

Use a controlled comparison with identical full source, original findings,
reporting contract, requested provider/model/effort and output shape. A supplies
no added reference; B repeats literal excerpts; C adds checked condition
interpretations to those same excerpts. See the immutable
[corrected preregistration](scope-diagnostic-20261109/corrected/preregistration.json).
Known development inputs retain all nine original findings plus K/M controls.
No new held-out cases or complete gold-label set is claimed.

The root researcher checked the supplied interpretation against source before
outputs existed. This was not an independent human/model audit. Final reasons
are judged by the root with arm labels visible; no blind-review claim is made.
The decisive original read/F1 requires an excluded label and a reason retaining
the independent prose disjunct rather than calling every target entry-excluded.
K must retain the explicit new-skill baseline exception; M must recognize the
case/run metadata location conflict in its own historical source version.
Other original findings retain disagreement and are not aggregate accuracy data.

## Preparation failures retained

The initial A1 CLI failed before a thread was created with an in-process
app-server permission error; its JSONL is empty. A pre-response
[startup amendment](scope-diagnostic-20261109/startup-amendment.json) allowed
normal host initialization without changing prompts or model settings.

The root then found a preparation error: the initial source pack used the
current repaired creator runtime, rather than each control's frozen target.
The running A1s process was terminated before any response or usage event was
observed. It had thread.started and turn.started events; remote billing cannot
be inferred as zero. No B/C process from that invalid batch was started.
Its original prompts, runner and logs remain unchanged under the parent
[artifact directory](scope-diagnostic-20261109/).

This is an investigator error, not a model failure or repair. The correction
was fixed before any model result existed. The corrected pack keeps each case's
separate source tree: original/K at `35a6be1446a3636450a6d94886195d37018da9b1`,
M at `cd2c2c02851f114559097f689892384332c69975`. All 87 files and six raw input
JSONs match the prior W17 input hashes. Every candidate side quote is found in
its own full file after whitespace normalization; raw bytes are not rewritten.

The corrected trial shrinks to one call per arm, order A/B/C, maximum three
valid-batch initiations and five total process initiations including failures.
Each valid call has a 300-second timeout. There are no output-selected retries.
Incomplete execution, invalid coverage, unexpected tools or missing usage stops
the batch. This amendment reduces repeatability evidence and is not hidden.

## Evidence and execution

Codex CLI reports version `0.167.0`. The retained
[runner](../../evidence/research/2026-11-02-repair-skill-dev-toolkit/scope-diagnostic-20261109/corrected/run.py) explicitly requests OpenAI
`gpt-6.1-sol`, `high`, ignores user config and removes provider override environment
variables. Executor approval is `never`, sandbox read-only, web search disabled,
project instruction loading disabled, tools forbidden. Source workflows are data.
Complete numbered source text is supplied inline; no executor file reads are
needed. All outputs are captured by the runner outside the executor workspace.

[Official pricing](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
was read on 2026-11-09: standard per-million input USD 2, cached input USD 0.10,
output USD 10. The runner stops before another call if observed API-equivalent
usage reaches USD 2. This is a usage estimate, not a hard invoice cap; cache
writes, subscription accounting, actual service tier and aborted-call usage
are not fully observable. Do not add the unknown interrupted-call charge as zero.
Previous Claude estimates and all historical review counters remain unchanged.

## Findings

All three corrected-batch calls completed, with 11 decisions each and no
executor tool calls. Both controls received the expected dispositions in every
arm: K excluded, M confirmed. Complete raw outputs remain
[A](scope-diagnostic-20261109/corrected/A1.final.txt),
[B](scope-diagnostic-20261109/corrected/B1.final.txt), and
[C](scope-diagnostic-20261109/corrected/C1.final.txt).

| Arm | Original read/F1 label | Reason assessment | K/M controls |
|---|---|---|---|
| A: baseline | excluded | PASS for the tested scope defect | excluded / confirmed |
| B: literal excerpts | excluded | PASS for the tested scope defect | excluded / confirmed |
| C: checked premises | excluded | QUALIFIED: incomplete ordinary-prose branch explanation | excluded / confirmed |

A explicitly says "Ordinary prose also does not establish the creative-output
blocker." B says "Deterministic prose alone also does not establish the abort
condition." These reasons retain the original prose disjunct separately from
entry-excluded creative targets. Consequently A did not reproduce the historical
blanket-scope failure. This is a development-case observation, not a repaired
host or proof of stable caller quality.

C retains the original union and states that prose is a parenthetical example
under the creative/non-deterministic entry predicate. It does not make the old
explicit all-target exclusion, but its final "No incompatible actions survive
that scope" does not separately finish the ordinary-prose branch. Grade this
QUALIFIED for explanation completeness, not a demonstrated wrong label or
proof of a worse method. Do not supply a better argument on the executor's behalf.

B confirmed original read/F2, simulate/F2 and simulate/F3, while A and C excluded
them. These concern the pre-existing local/global PROCEED and unreachable-warning
interpretations. They are retained as disagreement, not scored improvements or
newly settled truths. No all-finding accuracy is calculated. The root read all
33 outputs but adjudicated only the preregistered focal claim and two controls;
the [grading record](scope-diagnostic-20261109/corrected/grading.json) preserves
actual reasons, separate label checks and assessment qualifications.

Observed usage for the completed calls totals 547,351 input tokens, including
29,568 cached input tokens, and 11,521 output tokens. At the inspected standard
rates, the API-equivalent estimate is USD 1.1537328. This covers only completed
calls; aborted-call usage remains unknown. Durations were 133.37, 100.06 and
84.69 seconds. The initial sandbox-start failure and interrupted invalid call
are additional retained process attempts, not successful tests or free calls.

Post-run checks revalidated all 87 historical source hashes and all three prompt
hashes; the original W17 archive SHA256 remains
`dac5102f2727dfe685aa548c251bad5023b4662d69d1b196c99972bc07305392`.
`git diff HEAD -- skill-dev-toolkit` is empty. Prior case files, failed outputs,
user work and product code were not rewritten. Backend identity was not exposed
in exec JSONL; provider/model/effort claims describe explicit request settings.

## Decision impact and limitations

If baseline A does not reproduce the historical reason failure, this setup
cannot localize that failure even if all arms look correct. A single run per arm
cannot establish repeatability, statistical improvement or an architecture limit.
Inline source presentation, explicit model request and a smaller reporting-only
task differ from historical native host runs. Backend identity must remain
unknown if not exposed by CLI events. Supplied premises are privileged input,
not an autonomous extractor or a proven upper bound. No green mechanical suite
can substitute for source-grounded reason assessment.

That non-reproduction condition occurred. The bounded decision is **inconclusive
localization, no demonstrated treatment benefit**. There is no basis here to add
an extractor, parser, extra judge or standing runtime stage. No more calls follow
this batch. To investigate further, the smaller relevant question would be
whether the actual reading/tool-mediated caller reproduces the failure with
matched current sources and known host configuration. This record does not
execute or allocate another test window. Publication and release remain blocked
by the existing unresolved semantic evidence, not by a newly invented standard.
