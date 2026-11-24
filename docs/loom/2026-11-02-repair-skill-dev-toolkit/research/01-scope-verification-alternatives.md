---
title: "Reducing scope errors without another speculative checker framework"
type: loom-research
status: concluded
created: 2026-11-09
updated: 2026-11-09
change: 2026-11-02-repair-skill-dev-toolkit
tags:
  - loom/research
---

# Reducing scope errors without another speculative checker framework

## Question and scope

What should be investigated next when the consistency-check caller repeatedly
misstates the applicability of an original finding, despite correct-looking
labels and independent reviews? The decision is whether another implementation
is justified, and which smaller investigation would inform it.

The inspected project is at `c66424d387584c8ddb8c9dd109d15bfbd08b6802`.
The rejected W17 candidate is `1a7c51c29ad43df55690fb4717f16abdc439ec82`;
its two product files were restored. The original failure fixture references
`35a6be1446a3636450a6d94886195d37018da9b1`, not the current refactor text.
This research does not reopen the one-candidate experiment, its formal review
episode, or any paid test budget. Product code, original cases, expected labels,
failed outputs, installed tools and prior reports remain unchanged.

## Method and rationale

Use hypothesis-driven inspection plus a small qualitative trade study. First
recheck the frozen source and actual reasons; then compare transferable methods
against original research and one connected upstream implementation. Criteria
are complete claim fidelity, applicability to mixed factual/action instructions,
independent observability of the suspected error, runtime complexity and fit
with the existing no-new-parser/schema/standing-agent constraint. No invented
weighted scores are used.

English and Japanese exploratory searches were issued together using general
public technical terms. Primary papers are predominantly English. A Japanese
NINJAL PDF lead timed out and is not treated as inspected evidence. Stop once
the evidence supports a bounded next-investigation decision; no model experiment,
package installation, repository setup, paid CLI call or external contact runs.

Earlier [industry-oriented evaluation notes](../evidence/host-release-readiness.md)
already discuss execution completeness and transcript grading. They are retained;
this is not claimed to be the first external research. The narrower question
here is preservation of scope and logical conditions. The existing
[caller calibration](../evidence/caller-calibration.md) is reused, not relabeled
as a new solution.

## Findings

1. **Observed locally:** the failed boundary is semantic, upstream of rendering.
   W17 reordered source applicability before contradiction in the existing
   caller, but three actual reasons still generalized an excluded creative
   target over the original independent prose category. Correct labels did not
   establish faithful reasons. Both initial audits missed this issue until a
   targeted source challenge; their revised materiality assessments disagree.
   This supports investigating premise handling, not a causal claim about the
   model's internal mechanism. [Project evidence](../evidence/native-ten-rounds.md)
   and the [unchanged archive](../evidence/w17-scope-first-results.json) retain it.

2. **Source-supported:** claim decomposition is a possible method, not an
   automatic remedy. FActScore separates facts and checks them against evidence;
   its score measures factual precision, not a proof that a whole conditional
   policy claim is valid. Wanner et al. distinguish coverage, coherence and
   atomicity of decomposition. Those are separate from the final verdict.
   [FActScore](https://aclanthology.org/2023.emnlp-main.741.pdf),
   [Wanner et al.](https://aclanthology.org/2024.starsem-1.13.pdf).

3. **Counterevidence to indiscriminate splitting:** Hu et al. report effects
   varying with input granularity and verifier, including degraded performance.
   Their error analysis includes omitted context/logical relationships and
   altered meaning. Consequently, splitting every sentence could reproduce
   this project's qualifier loss rather than eliminate it.
   [Decomposition Dilemmas](https://aclanthology.org/2025.naacl-long.320.pdf),
   Sections 4–6. These are reported experimental results, not measurements here.

4. **Source-supported but transfer-limited:** Tyen et al. separate finding a
   reasoning mistake from correcting it given its location. Their BIG-Bench
   tasks and oracle-assisted corrections motivate isolating the failed stage.
   They do not prove a model can discover this project's source-scope error.
   [Tyen et al.](https://aclanthology.org/2024.findings-acl.826.pdf), Sections 2–4.

5. **Preserve contrary evidence:** ProCo reports gains from verifying selected
   conditions rather than generic self-correction, on QA, arithmetic and
   commonsense tasks using older models. Thus neither this research nor one
   rejected patch establishes that all prompt-based methods are futile.
   Its result does not establish effectiveness for policy scope or current
   Claude/Codex configurations. [ProCo](https://aclanthology.org/2024.emnlp-main.714.pdf),
   Sections 3–4. Its implementation was not inspected or executed here.

## Evidence

### Local source and measured history

- [Current caller](../../../../skill-dev-toolkit/skills/skill-consistency-check/SKILL.md),
  Step 6 items 2–4, already requires full original coverage and source reasons.
  Merely repeating this obligation is not a new design.
- [Merger](../../../../skill-dev-toolkit/skills/skill-consistency-check/scripts/merge_report.py),
  `_select` lines 114–137, checks hashes, IDs, statuses and nonempty reasons;
  `build_report` lines 178–193 consumes the resulting selection. This inspected
  path deliberately does not validate reason truth. Existing byte-identical
  report reproduction is historical evidence, not a fresh run in this study.
- [Frozen manifest](../../../../skill-dev-toolkit/tests/caller-review-cases/overstated-original-claim/case.json)
  and [W17 archive](../evidence/w17-scope-first-results.json) identify the original
  source and all three actual read/F1 reasons. Read-only `git show` of the two
  cited frozen files matched their manifest SHA256 values. Frozen entry
  `SKILL.md:358–360` qualifies the exclusion by creative/non-deterministic output;
  protocol `:119–123` agrees, while `:17` lists prose as an ordinary artifact type.
  That does not grant universal admission for prose; it prevents promoting the
  parenthetical example into an all-prose prohibition.
- The archive preserves audit A's qualified scope interpretation and audit B's
  reason-fidelity failure. No majority label is substituted for the source.
  [Intent](../../intent/2026-11-02-repair-skill-dev-toolkit.md), Acceptance 9/11,
  still governs correctness; [plan](../plan.md), Risk 44, records rejection.

### Upstream implementation inspected, not run

FActScore was inspected at commit
`f28272deffcf33efc1f1117d5479c10bb75221a9`, not inferred from its README:

- [`atomic_facts.py:96–139`](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/atomic_facts.py#L96-L139)
  builds decomposition prompts and calls the model. Its
  [entity coverage fallback at 282–285](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/atomic_facts.py#L282-L285)
  retains prior facts on failure; it is not a proof that modality, qualifications
  or logical relationships survived.
- [`factscorer.py:104–159`](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/factscorer.py#L104-L159)
  either accepts supplied atomic facts or generates them. The connected
  [`_get_score` path at 209–223](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/factscorer.py#L209-L223)
  retrieves context per fact; [180–190](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/factscorer.py#L180-L190)
  averages support decisions and optionally applies a length penalty.
  This does not justify averaging subclaim labels into this tool's original
  `confirmed` finding. Quantifiers and selected branches must retain their
  original meaning. No repository setup, NLP download or model call was run.

The source blob identifiers returned by the connector were
`d237ef6191d053ffdf22bee1753d7e8c527cf2a1` and
`6793fe5dad835508a044e4673ee235fe108ac440`, respectively. These source
observations establish a code path, not installed-release or runtime behavior.

## Decision impact

**Do not select another implementation candidate now.** Prefer preparing a
stage-isolating diagnostic comparison. This is an agent recommendation, not
user approval to change a contract or execute another paid trial.

| Alternative | Fit and complexity | Bounded decision |
|---|---|---|
| Retain current code and postpone repair | No added runtime; known release gap remains | Safe current boundary, not a completed repair. |
| Another wording/order-only patch | Small, but that shape already failed locally | No new discriminating evidence justifies it now. |
| Small diagnostic comparison, without product changes | Makes source-condition extraction and downstream reasoning separately observable | Recommended next investigation to design, not execute here. |
| Diagnostic comparison plus selective decomposition | Potentially useful only if decomposition preserves original conditions | Consider later only with independent coverage/coherence evidence; do not split everything. |
| Full translation to formal rules, new checker or more judges | Adds translation/maintenance burden; reliable translation still unproven | Not justified under the current minimal-complexity constraints. |

The proposed diagnostic is different from W17's instruction reordering:
hold the original finding, source snapshot and final reporting contract fixed;
compare ordinary processing with an explicitly supplied, independently checked
source-condition reference. That reference keeps the full original claim,
quantifier, action/fact modality, selected branch and exact source qualifications.
It contains source premises, not an expected final label. Do not edit frozen
cases or failed outputs to create it.

If correct premises enable faithful reasoning but ordinary processing does not,
that supports focusing on source-condition extraction. If reasoning still fails
with correct premises, extraction alone is insufficient. Either outcome remains
limited: a supplied correct reference is privileged diagnostic information, not
an autonomous production extractor, and extra context may itself affect results.
Its construction can also be wrong. Audit its coverage/coherence before
interpreting a comparison; keep disputed readings disputed.

This smaller design combines source-by-source comparison with selective
decomposition only where needed. It adds no permanent runtime stage in this
research. If a later proposal requires a new intermediate field, extra model
pass or parser, it must explicitly revisit the existing constraints through the
owning Loom process. Hiding new machinery inside a reason string is not a
complexity reduction. Do not call another ordered paragraph a separate stage.

Any future measurement must retain the overbreadth negative, genuine positive
controls and independent real-source held-out cases; judge reasons as well as
labels and track omissions. A correct supplied-reference arm is only an upper
bound for that setup. It must not be reported as a repaired host, an effect size
for unseen tasks, or permission to release. No experiment is run by this record.

## Limitations and open questions

The papers concern factual verification or other reasoning tasks, not this
mixed normative skill package. Their models and datasets do not match the
current requested hosts. No benchmark improvement, architecture limit or
industry-wide consensus is established. The recommended diagnostic itself is
unmeasured; the evidence supports what to investigate, not a working fix.

The earlier source calibration already identified the scope distinction; merely
writing another correct table would repeat it. A new experiment would have to
vary whether accurate premises reach the decision process, while preserving
blinding and acknowledging privileged information. Successful localization
would still leave automatic premise extraction and end-to-end host quality
unverified. User acceptance, publication, installation and merge are unchanged.

This record is concluded because the bounded next-investigation decision is
supported. The product repair remains unresolved. No product file, original
case, previous research, audit, expectation or measured output was changed.
