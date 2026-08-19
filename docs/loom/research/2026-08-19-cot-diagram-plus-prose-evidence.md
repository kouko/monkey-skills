# Evidence: a per-unit CoT diagram shown alongside its prose

Commissioned 2026-08-19 by kouko, to decide whether to build the parked
`docs/loom/backlog/2026-08-18-per-unit-cot-diagram-in-the-adjudication-view.md`.
Three parallel sweeps: external evidence on the human reader, external
evidence on the model reader, and an audit of what this repo had already
measured. Every claim below carries its source; inferences across
literatures are labelled as inferences.

## Bottom line

The literature predicts this feature **harms** the reader it was designed
for, and the premise that kept it out of the agent-consumed artifact is
**not the premise that actually holds**.

Two mechanisms do the damage, and both are specific to our case rather
than general objections:

- The reader is an **expert**, reviewing at a sign-off gate.
- The diagram is **machine-generated, unreviewed, and regenerated per
  render**.

## Human reader — the literature predicts harm

| Finding | Predicts | Source |
|---|---|---|
| **Redundancy effect** (cognitive load theory — Sweller/Chandler lineage; Mayer's CTML carries a parallel *redundancy principle*) — the same content in two simultaneous forms adds extraneous cognitive load | harm | [Springer, Sweller/Ayres/Kalyuga 2011 ch.12](https://link.springer.com/chapter/10.1007/978-1-4419-8126-4_12) (EN) |
| **Expertise reversal effect** — support that helps novices costs experts; experts perform better with diagram-only OR text-only than with both | harm, specifically for an expert | [Springer 2011](https://link.springer.com/article/10.1007/s11423-011-9199-0), [ResearchGate](https://www.researchgate.net/publication/48829036_The_Expertise_Reversal_Effect) (EN) |
| **Split-attention effect** — separated text and diagram force costly integration; placing the diagram directly beneath fixes this | help, but irrelevant | [Chandler 1992](https://bpspsychub.onlinelibrary.wiley.com/doi/abs/10.1111/j.2044-8279.1992.tb01017.x) (EN) |
| Causal-chain diagrams improve comprehension of causal sequences | help — content-type match | [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0361476X05000652) (EN) |
| LLM-generated diagrams hallucinate more as source complexity rises, and models fail to self-detect the errors | harm | [arXiv 2601.20476](https://arxiv.org/pdf/2601.20476) (EN) |
| Plausible-looking AI output raises user trust even when wrong; automation bias suppresses scrutiny | harm | [arXiv 2505.21512](https://arxiv.org/pdf/2505.21512) (EN) |
| 冗長性効果・専門性逆転効果・分割的注意効果 — same three mechanisms, same direction | no reversal | [zenn.dev](https://zenn.dev/kangetsu_121/articles/6b31565dda6053) (JA) |

Three readings of that table matter more than the rows themselves.

**The layout we chose fixes the wrong problem.** Putting the diagram
directly beneath its paragraph is the textbook remedy for split-attention
— and split-attention was never the risk here, precisely because the
layout is already integrated. Redundancy survives perfect integration
untouched, because two representations still say the same thing twice.

**The content-type match is real but the population is wrong.** Diagrams
do help with causal sequences, which is exactly the paragraph class this
feature targets. Every study behind that finding tests learners acquiring
new material. Nothing found tests an expert verifying material at a gate.

**The two machine-generation findings compound into one failure mode.** A
subtly wrong diagram beside correct prose is more likely to be skimmed and
trusted than caught — and the reader most exposed to automation bias is
the one doing final sign-off. Stated honestly: this is an inference across
two literatures, not a study of "wrong diagram versus no diagram".

## Model reader — the premise is contradicted or untested, not confirmed

The shipped premise was: *structure buys human readability and leaves
model comprehension unchanged.* Neither half survives inspection.

| Finding | Effect | Source |
|---|---|---|
| Structured formats change task accuracy versus prose — direction depends on the task | not neutral | [arXiv 2510.21034](https://arxiv.org/pdf/2510.21034) (EN) |
| Format **restriction** degrades performance on reasoning tasks specifically | harm, and reasoning is our target class | [arXiv 2408.02442](https://arxiv.org/html/2408.02442v1) (EN) |
| Graph structure derived from text helps multi-hop reasoning — but it ADDS relations not otherwise visible | help, different mechanism | [arXiv 2501.07845](https://arxiv.org/abs/2501.07845) (EN) |
| Long or redundant context dilutes attention; degradation can arrive as a cliff | removes the "extra tokens are free" assumption | [redis.io](https://redis.io/blog/context-rot/) (EN), [Qiita](https://qiita.com/ktdatascience/items/aa01661d3fde252d4d3b) (JA) |
| Models have no dedicated mechanism for resolving contradictions **within** one context; no clean recency-wins or first-wins rule | uncharacterized risk | [EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1742.pdf), [arXiv 2310.00935](https://arxiv.org/pdf/2310.00935) (EN) |
| Redundant restatement — the same content as prose plus diagram, in one context | **untested** | — |
| Token cost of a small mermaid fence versus the paragraph it restates | roughly 1:1, not decisive | practitioner estimate |

The graph-reasoning row is the one most likely to be miscited in this
repo's favour, so it is worth stating plainly: those graphs carry
relations the prose leaves implicit. Ours would restate relations the
prose already spells out. Same notation, different mechanism, and the
measured benefit belongs to the other one.

## What this repo had already measured — less than its shorthand suggests

| Evidence | Compared | n | Reader | Result |
|---|---|---|---|---|
| Dogfood Probe 1 | table vs numbered-list template slot | 2 baseline, 3 candidate | writer | 0/2 → 3/3 tables |
| Dogfood Probe 3 | diagram edge labels, node layering | 2 per leg | writer | edges no delta; two-layer nodes 0/0 → 7/7 |
| Dogfood Addendum | table vs list, same facts, 10 questions | 12 | model | 10/10 everywhere |

Sources: `docs/loom/dogfood/2026-08-17-artifact-table-routing-dogfood.md:14-74`.

Three gaps, in ascending order of how badly they bite:

1. **The comprehension result is at ceiling.** Every reader on every form
   scored full marks. That is an instrument with no resolution at this
   difficulty, not a measured null. It licenses "not detected", never "no
   effect". The memory entry distilled from it has been corrected
   accordingly.
2. **Every diagram measurement here is writer-side.** Whether a writer
   draws one, and in what shape. This repo has never measured a reader —
   human or model — understanding a diagram better or worse than prose.
3. **The commissioning spec declared human comprehension out of scope**
   (`docs/loom/specs/2026-08-17-artifact-table-routing.md:29`). The
   comprehension numbers are an unplanned addendum, not an acceptance
   criterion.

Internal evidence about diagram density, about a diagram disagreeing with
its prose, or about machine-generated diagrams at all: **none, at any n**.

## What the evidence changes

**Keeping the diagram out of the agent-consumed artifact is now better
justified, for a different reason.** The original reason was that model
comprehension is unaffected, so the benefit accrues only to the human.
That reason is untested. The reason that survives is stronger: a second
statement of the same content carries an uncharacterized contradiction
risk, and this repo has no evidence of any offsetting gain.

**The always-on, side-by-side design is the one the evidence rejects.**
Expertise reversal does not say "experts do not need diagrams" — it says
experts do better with **one** representation than with two. That points
at a toggle, not a pair, and it is a design the backlog entry never
considered.

**A different purpose might survive where comprehension does not.** If
the diagram is for **navigation** — deciding which paragraph deserves a
close read — rather than for understanding, redundancy never fires,
because the reader does not read both. No evidence was found for or
against this use; it is the honest place to put the remaining hope, and it
must be measured rather than assumed.

## If it is measured, avoid this run's own mistake

The task must be hard enough to score below ceiling, or it repeats the
addendum's failure and reports a null it never had the power to detect.

- **Human arm, n=1 (kouko), three conditions**: prose only, diagram only,
  both. Measure time-to-locate a planted reasoning flaw and whether it is
  caught — review effectiveness, which is what this view is for, not
  comprehension.
- **The load-bearing condition**: in one arm, the diagram must disagree
  subtly with its prose. This is the largest unquantified risk in the
  design, and a single trial shows whether the diagram or the prose wins.
- **Model arm**, same three conditions, with multi-hop and
  find-the-contradiction questions rather than recall.

## Provenance

Three parallel `general-purpose` sweeps, 2026-08-19, English and Japanese
queries per the repo's search convention. No EN/JA disagreement was found
on the human side; the JA corpus has no expert-specific redundancy data,
which is an absence of coverage rather than a contradicting finding.
Vision-model findings were excluded by construction — the diagram is read
as source text, never as a rendered image, and that is a separate
question.
