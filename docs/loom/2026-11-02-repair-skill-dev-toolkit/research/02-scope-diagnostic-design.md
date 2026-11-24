---
title: "A bounded diagnostic for source-condition failures"
type: loom-research
status: concluded
created: 2026-11-09
updated: 2026-11-09
change: 2026-11-02-repair-skill-dev-toolkit
tags:
  - loom/research
---

# A bounded diagnostic for source-condition failures

## Question and conditions

Can a small diagnostic distinguish failure to preserve source conditions from
failure to judge an original contradiction, without adding a production checker?
This continues the decision in [the alternatives study](01-scope-verification-alternatives.md)
but answers the narrower experimental-design question. No experiment runs here.
The product remains at the previously inspected c66424d revision. Existing
cases, failures, budgets, review counters and release restrictions remain intact.

## Method and rationale

Use hypothesis-driven design inspection: identify competing explanations and
the smallest comparison that could discriminate them. Reuse the frozen manifest
and earlier research, and inspect original research methods for intervention
controls. English and Japanese general technical searches were issued together;
only original papers support external claims. No project text was sent in queries.
This is a proposed diagnostic protocol, not measured effectiveness or a new
implementation plan. There is no product, runner, schema or runtime-role change.

## Findings and evidence

The [frozen manifest](../../../../skill-dev-toolkit/tests/caller-review-cases/overstated-original-claim/case.json)
explicitly separates executor inputs from grader expectations. It has one
contract-derived expected disposition and disputed candidates without unique
gold labels. Consequently the supplied reference must not disclose that
disposition, reproduce a previous verdict, or pretend the entire case is gold.
Prior failure reasons and audits remain available to graders, not executors.

The earlier two-arm proposal confounds correct interpretation with highlighting
and additional context. A third, literal-excerpt control is worth its small
diagnostic cost before proposing an autonomous extraction component. It does
not eliminate every confound: interpretation necessarily adds information.

[Tyen et al., ACL 2024](https://aclanthology.org/2024.findings-acl.826.pdf),
Sections 4.1–4.2, compare correction using known mistake locations with random
locations. Their discussion also notes that aggregate benefit depends on the
starting answer distribution. This supports using a relevant control and
checking regressions, not transferring their effect sizes to this project.

[Jia et al., REALM 2026](https://aclanthology.org/2026.realm-1.6.pdf),
Sections 3.1–3.3, replace trajectory context with privileged structured state
while using an environment-only reset as a control. Their oracle state is
model-generated and sampled for validation by two human annotators. This is
useful methodological evidence that an oracle needs validation and that other
changed conditions need controls. WebArena action recovery is not skill-rule
consistency, and their intervention changes more than our proposed input.
No implementation or reproduction was inspected or run here. The Anthology
HTML abstract and PDF differ in numerical wording; no effect size is adopted.

## Proposed comparison — not executed

| Arm | Additional executor input | Question it helps answer |
|---|---|---|
| A: baseline | None; otherwise identical source and original finding | Does the ordinary path still fail in this setup? |
| B: source emphasis | Exact relevant source excerpts, with paths and sufficient surrounding qualifications | Does making already available text salient help without supplying an interpretation? |
| C: checked premises | Same excerpts plus a separately checked account of conditions, alternatives and scope | Does explicitly supplying the interpretation help beyond excerpts alone? |

Keep all original source files available in every arm; B and C do not replace
the complete input. Match wrapper, insertion position, host/model configuration,
tool permissions and output contract. Record prompt lengths rather than claiming
perfect length matching: padding can introduce another effect. Use fresh
sessions and interleave arm order. Never compare a new arm solely against old
archived runs under a different setup. Record actual configuration visibility;
an unknown backend stays unknown. This protocol does not specify a new model.

Prepare a separate research-only premise reference, leaving original fixtures
untouched. Every proposition needs an exact source location and surrounding
conditions. Preserve alternatives, quantifiers, modality and selected branches;
do not turn an example into a category-wide restriction. Include no expected
status or assertion that the finding is valid/invalid. Reject disputed premise
interpretations from the decisive subset; retain them as disputed observations.
Check the reference independently of executor output before running. That
check has not happened here and is a prerequisite, not assumed available truth.

Grade the final result and explanation separately. Require the reason to account
for the complete original claim and material source conditions; a correct label
with an overbroad reason fails. Track unsupported additions, omitted conditions,
and genuine-positive regressions individually. Grade shuffled outputs without
arm names where feasible, acknowledging that wording can reveal the arm.
Do not require private chain-of-thought or treat a plausible explanation as a
measurement of the model's internal computation.

Retain the known overbreadth case and genuine positive controls. Reserve new,
independent source cases before exposure if making any generalization claim;
otherwise report a development-case diagnostic only. Repeated runs estimate
within-case variability, not independent case coverage. Before execution,
predeclare the exact cases, repeats, call cap, cost cap and stopping rules;
this research does not silently allocate or reopen a budget.

## Decision impact and stopping rules

| Observation | Bounded interpretation | Next decision |
|---|---|---|
| A does not reproduce the failure | This setup is not diagnostic of the archived failure | Stop; inspect setup differences before claiming repair. |
| B improves as much as C | Salience or retrieval support may suffice | Investigate the smaller source-presentation change first. |
| C improves beyond B without positive-control regressions | Supplied interpretation helps in tested conditions | Consider an extraction feasibility test, not a production stage yet. |
| C still fails despite a checked reference | Supplying these premises is insufficient | Reconsider downstream judgment; do not infer an absolute architecture limit. |
| Outcomes vary, references are disputed or controls regress | Localization remains inconclusive | Preserve results and stop this bounded trial; no automatic expansion. |

Agent-decided recommendation: design this three-arm diagnostic rather than a
new production component. Doing nothing remains valid if no bounded trial is
authorized. A smaller A/C comparison is a feasibility screen only; it cannot
separate source emphasis from interpretation. Combine a diagnostic with selective
decomposition only after fidelity has been independently checked. More judges
or a formal parser are not justified by this design research.

## Limitations and correction to the earlier study

The earlier study called supplied-reference performance an "upper bound".
That is too strong: input changes can hurt, other representations can help,
and no monotonicity or optimality is established. Read it only as performance
under privileged input, not a mathematical ceiling or proof of causal mediation.
This explicit correction preserves the original research record and decision.

The new design has not been executed; references, held-out cases and execution
caps have not been prepared or approved by this record. No known failure is
repaired and release remains unsupported. Stop literature expansion now: the
remaining consequential uncertainty requires a controlled observation, not more
papers. No product files, cases, installed tools or prior results were modified.
