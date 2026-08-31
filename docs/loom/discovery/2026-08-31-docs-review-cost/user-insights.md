# User insights — 2026-08-31-docs-review-cost

> Problem-space artifact. It states what must improve and why, without deciding
> that a new plugin is the answer.

## Problem framing

- **What** — During Loom development, document review consumes disproportionate
  effort, but the available records cannot separate initial writing defects,
  fix-introduced defects, reviewer variance, and review-policy effects.
- **Why now** — Review loops have already triggered repeated redesigns of the
  reviewer contract, yet the latest process still lacks durable measures that
  show whether cost and quality improved.
- **Whose problem** — Loom maintainers authoring contract-class prose and relying
  on that prose to guide weak or fresh agents.

## Opportunity space

### Need N1 — Attributable review cost

- **Job story**: When a document review becomes expensive, I want to know which
  stage created each consequential defect, so I can improve the stage causing
  the cost instead of tuning the entire pipeline.
- **Evidence**: `evidence.md` C1–C5, C9.
- **Context / journey stage**: drafting, remediation, and branch close-out.
- **Today's workaround**: reconstruct causes manually from audit prose, Git
  history, and surviving PR narratives.

### Need N2 — Stable quality signal

- **Job story**: When a reviewer returns a verdict, I want to know how repeatable
  and consequential that signal is, so I can trust it without mistaking one
  sample for exhaustive truth.
- **Evidence**: `evidence.md` C3–C6, C10–C12.
- **Context / journey stage**: quality-gate judgment and post-fix confirmation.
- **Today's workaround**: use multiple reviewers or additional rounds, raising
  cost while still producing non-overlapping findings.

### Need N3 — Earlier defect prevention

- **Job story**: When contract prose is being created or repaired, I want
  repeatable defect classes caught before final judgment, so reviewer attention
  remains available for ambiguity and factual reasoning.
- **Evidence**: `evidence.md` C1–C2, C5, C13–C14.
- **Context / journey stage**: authoring and pre-review verification.
- **Today's workaround**: introduce one-off scripts, format rules, and reviewer
  clauses after a defect class has already caused repeated rounds.

### Need N4 — Coherent ownership without duplicate orchestration

- **Job story**: When documentation work crosses technical, business, and
  strategy contexts, I want each quality responsibility to have one clear owner,
  so capability can expand without maintaining competing routers and gates.
- **Evidence**: `evidence.md` C7–C8, C15.
- **Context / journey stage**: capability routing and long-term maintenance.
- **Today's workaround**: combine existing skills manually and infer which
  review contract governs the resulting artifact.

## Value commitment

- **Committed needs**: N1, N2, N3. First make review cost attributable,
  establish a stable quality signal, and move repeatable defect prevention
  earlier. N4 is not committed as a new plugin boundary; ownership is
  reconsidered only after the measured campaign.
- **Desired outcome per need**:
  - N1 — qualitative: each consequential finding can be attributed to initial
    authoring, remediation, reviewer variance, or review policy; quantitative:
    a baseline corpus and per-run records exist before process changes land.
  - N2 — qualitative: reviewer verdicts are interpreted with known stability
    limits; quantitative: finding rate, false-alarm rate, repeat-run agreement,
    and cost per load-bearing finding are compared on the same corpus.
  - N3 — qualitative: deterministic and fixed-rule defects reach final review
    less often; quantitative: each proposed pre-review check must reduce a
    measured defect class on the corpus without hiding a load-bearing finding.
- **Appetite**: one bounded research/experiment arc, with a stop after baseline
  if the evidence identifies an upstream-only cause, and a second stop after
  existing-stage improvements if no stable unowned responsibility remains.
- **Ratified by user on** 2026-08-31.

## Risks & open questions

- **R1** — Historical evidence is concentrated in several unusually difficult
  branches; it does not establish the current average cost.
- **R2** — A new organizational boundary could duplicate `docs-team`,
  `requesting-docs-review`, and strategy owners without improving N1–N3.
- **Q1** — What stable corpus and human-owned labels should define a correct
  finding, an escape, and a false alarm?
- **Q2** — Which minimum measures make quality/cost comparable across reviewer
  contract versions?
- **Q3** — After measurement, does the smallest adequate ownership change fit an
  existing plugin, a shared Loom contract, or a separate plugin?
