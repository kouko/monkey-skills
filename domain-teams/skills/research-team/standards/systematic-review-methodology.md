---
title: Systematic Review Methodology
tier: 2
---

# Systematic Review Methodology

Defines the methodology research-team uses when the research question
demands a **systematic** rather than ad-hoc literature synthesis —
planning the question, searching exhaustively, screening at two
levels, extracting data, appraising quality, synthesizing findings,
and reporting the full trail so the work is reproducible. Tier 2:
LLMs know Cochrane and PRISMA by name but routinely muddle the
7-section PRISMA 2020 structure, the Cochrane 8-step workflow, and
Booth's 5-element argument model. The body spells out each of these.

## Primary Sources

- Julian P.T. Higgins, James Thomas, Jacqueline Chandler, Miranda Cumpston, Tianjing Li, Matthew J. Page, Vivian A. Welch (eds.) (2024) *Cochrane Handbook for Systematic Reviews of Interventions*, Version 6.5. The Cochrane Collaboration. https://training.cochrane.org/handbook/current. The canonical source for the 8-step systematic-review workflow and PICO question framing.
- Matthew J. Page, Joanne E. McKenzie, Patrick M. Bossuyt, Isabelle Boutron, Tammy C. Hoffmann, Cynthia D. Mulrow, Larissa Shamseer, Jennifer M. Tetzlaff, Elie A. Akl, Sue E. Brennan, Roger Chou, Julie Glanville, Jeremy M. Grimshaw, Asbjørn Hróbjartsson, Manoj M. Lalu, Tianjing Li, Elizabeth W. Loder, Evan Mayo-Wilson, Steve McDonald, Luke A. McGuinness, Lesley A. Stewart, James Thomas, Andrea C. Tricco, Vivian A. Welch, Penny Whiting, David Moher (2021) "The PRISMA 2020 statement: an updated guideline for reporting systematic reviews". *BMJ* 372:n71. https://www.prisma-statement.org/prisma-2020-statement. The 27-item checklist across 7 sections that defines minimum reporting standards for systematic reviews.
- Wayne C. Booth, Gregory G. Colomb, Joseph M. Williams, Joseph Bizup, William T. FitzGerald (2024) *The Craft of Research*, 5th ed. University of Chicago Press. Part III "Making an Argument" (Ch.7-12) defines the 5-element argument model (Claim / Reason / Evidence / Warrant / Acknowledgment-and-Response) that research-team uses as the scaffolding for research deliverables. The 1st-edition core argument model is stable across editions; the 5th-edition chapters on generative AI, visual presentation, and oral delivery are new.
- Association of College and Research Libraries (2016) *Framework for Information Literacy for Higher Education*. https://www.ala.org/acrl/standards/ilframework. The "Research as Inquiry" and "Searching as Strategic Exploration" frames ground the disposition of treating literature search as an iterative, question-driven process rather than a one-shot keyword dump.

## Critical Attribution Corrections

### Booth *Craft of Research* is 5th edition (2024), not 4th

The Craft of Research 5th edition was released on **2024-06-25** and
supersedes the 4th edition. Cite 5th edition for v4.9.0 and forward.
The core 5-element argument model (Claim / Reason / Evidence / Warrant
/ Acknowledgment-and-Response) is **stable since the 1st edition
(1995)** and LLM parametric knowledge of it is strong. However, the
5th-edition additions — a chapter on generative AI in the research
workflow and updated sections on visual and oral presentation — were
published **after most LLM training cutoffs**, so workers needing
5th-ed-specific content MUST Read the body of this standards file
rather than rely on parametric recall.

## When to Run a Full Cochrane Review vs a Lightweight Synthesis

Systematic review methodology is expensive. The decision rule:

| Question type | Methodology |
|---|---|
| "What does the evidence say about intervention X vs Y?" for a decision that will be cited externally (policy, investment, technology selection for a multi-year commitment) | Full Cochrane 8-step + PRISMA 2020 reporting |
| "What are the most cited recent papers on topic X?" for internal orientation | Lightweight 3-step: search → screen → summarize; no PRISMA reporting |
| "Is there any evidence that X works?" for a yes/no existence check | Lightweight; stop at the first adequately-powered primary source |
| "What is the mechanism behind X?" for conceptual understanding | Lightweight; prioritize review articles and primary mechanistic studies |

The distinguishing question: **will the output be audited by a reader
who did not see how you got there?** If yes → full systematic review
with PRISMA reporting. If no → lightweight is honest and faster.

## The Cochrane 8-Step Workflow

Cochrane Handbook v6.5 organizes a systematic review into eight
sequential steps. Each step is a gate: do not proceed until the
previous step's output is written down.

1. **Define the question** using the PICO (or PICOC) framework (see
   below).
2. **Plan the review** — write a protocol that pre-registers inclusion
   criteria, search strategy, and analysis plan BEFORE touching any
   studies. Pre-registration is the single biggest defense against
   confirmation bias.
3. **Search for studies** — build and document the search strategy:
   which databases, which search terms, which date ranges, which
   filters. Save the exact queries.
4. **Select studies** — two-stage screening: (1) title + abstract
   screening against inclusion criteria, (2) full-text screening.
   Record the count that passes each stage.
5. **Collect data** — extract pre-specified data fields from each
   included study using a standardized form.
6. **Assess risk of bias** — apply a risk-of-bias tool (Cochrane's
   RoB 2 for randomized trials; ROBINS-I for non-randomized studies)
   to each included study.
7. **Analyze and synthesize** — meta-analysis where quantitative
   pooling is valid; narrative synthesis otherwise. Do not pool what
   should not be pooled (heterogeneous populations, outcomes, or
   interventions).
8. **Interpret and report** — apply GRADE or equivalent to rate the
   certainty of the overall body of evidence, then report following
   PRISMA 2020 (see below).

Steps 1-3 happen before any study is read. Steps 4-6 are the
screening and appraisal phase. Steps 7-8 produce the deliverable.

## PICO and PICOC Question Framing

Cochrane's standard framing for clinical questions:

- **P**opulation — who is being studied?
- **I**ntervention — what is being done to them?
- **C**omparator — what are they being compared to?
- **O**utcome — what is being measured?

Research-team broadens this to **PICOC** for non-clinical questions:

- **P**opulation — what population / domain / cohort / dataset?
- **I**ntervention — what action / change / technology?
- **C**omparator — the counterfactual or baseline
- **O**utcome — the metric that would resolve the question
- **C**ontext — the setting that bounds generalizability

A well-formed question is **one sentence** that contains all four
(or five) elements. "Is Rust better than Go?" is not a question. "For
a 10-engineer backend team shipping latency-sensitive services (P),
does adopting Rust (I) vs continuing with Go (C) reduce p99 latency
and incident rate (O) over a 2-year horizon (C)?" is a question.

## PRISMA 2020 — the 27-Item, 7-Section Checklist

PRISMA 2020 (Page et al. 2021) is the minimum reporting standard for
a systematic review. A review that does not follow PRISMA 2020 cannot
be audited, because the reader cannot reconstruct the search, the
screening, or the synthesis. The checklist has **27 items across 7
sections**:

| Section | Items | What it covers |
|---|---|---|
| **Title** | 1 | Identify the report as a systematic review |
| **Abstract** | 2 | Structured summary (background, objectives, data sources, eligibility criteria, methods, results, conclusions, registration) |
| **Introduction** | 3-4 | Rationale (why this review matters) + Objectives (PICOC) |
| **Methods** | 5-16 | Eligibility criteria, information sources, search strategy, selection process, data collection process, data items, study risk of bias assessment, effect measures, synthesis methods, reporting bias assessment, certainty assessment |
| **Results** | 17-22 | Study selection (with PRISMA flow diagram), study characteristics, risk of bias in studies, results of individual studies, results of syntheses, reporting biases, certainty of evidence |
| **Discussion** | 23 | Interpretation — limitations, implications for practice, implications for research |
| **Other information** | 24-27 | Registration and protocol, support, competing interests, availability of data / code / other materials |

Items 5-16 (the Methods section) are the highest-density checklist
section because they define what makes the review reproducible. The
PRISMA 2020 flow diagram (item 16a) is a standard visual that
accompanies the Results section — see the ASCII flow below.

## PRISMA 2020 Flow Diagram — the 6-Step Funnel

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. IDENTIFICATION                                                │
│    Records identified from:                                      │
│      Database / register searching:     n = N_1                  │
│      Citation searching / other:        n = N_2                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ 2. SCREENING — TITLE / ABSTRACT                                  │
│    Records after duplicates removed:    n = N_3                  │
│    Records screened:                    n = N_3                  │
│    Records excluded:                    n = N_4                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ 3. RETRIEVAL                                                     │
│    Reports sought for retrieval:        n = N_5                  │
│    Reports not retrieved:               n = N_6                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ 4. ELIGIBILITY — FULL TEXT                                       │
│    Reports assessed for eligibility:    n = N_7                  │
│    Reports excluded, with reasons:      n = N_8                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ 5. INCLUDED — IN QUALITATIVE SYNTHESIS                           │
│    Studies included in review:          n = N_9                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ 6. INCLUDED — IN QUANTITATIVE SYNTHESIS                          │
│    (meta-analysis, where applicable):   n = N_10                 │
└──────────────────────────────────────────────────────────────────┘
```

Every N must be explicit. A flow diagram with unlabeled funnels fails
PRISMA 2020 item 16a. A review that drops from 1000 identified records
to 12 included studies must account for the missing 988 — how many
were duplicates, how many were excluded at title/abstract, how many
at full-text, and **why**.

## Booth's 5-Element Argument Model (Booth et al. 2024 Part III)

Booth's *Craft of Research* 5th ed decomposes any research argument
into five required elements. Research-team uses this as the
scaffolding for the Discussion section of systematic reviews and the
body of lightweight syntheses.

| Element | Question it answers | Example |
|---|---|---|
| **Claim** | What do you want the reader to believe? | "Rust reduces p99 latency compared to Go for CPU-bound services." |
| **Reason** | Why should they believe it? | "Because Rust's zero-cost abstractions remove GC pauses that dominate Go tail latency." |
| **Evidence** | What facts support the reason? | "Benchmark X (2024) measured 12ms→3ms p99 reduction on workload Y. Production telemetry from Company Z showed similar." |
| **Warrant** | Why does the evidence support the claim? (The often-unstated bridge) | "Because GC pauses account for >70% of p99 latency in Go services per Google's own profiling guidance, removing GC removes the dominant contributor." |
| **Acknowledgment-and-Response** | What would critics say? And how do you answer? | "Critics point to Rust's learning curve raising hiring costs (acknowledgment). Response: for latency-sensitive services the latency improvement and incident-rate reduction amortize the hiring cost within 18 months (response)." |

An argument that skips the **Warrant** leaks the unstated assumption
that connects evidence to claim — and that unstated assumption is
usually the weakest link. An argument that skips
**Acknowledgment-and-Response** pretends critics do not exist, which
is the single biggest credibility-killer for a research deliverable.
Research-team deliverables MUST contain all 5 elements for every
load-bearing claim.

## Anti-Patterns

- Declaring a review "systematic" without a pre-registered protocol.
  Systematic means pre-registered; everything else is a literature
  review.
- Reporting only the "included" count without the exclusion counts at
  each funnel stage. The excluded records are the audit trail.
- Pooling heterogeneous studies in a meta-analysis because "more is
  better". Heterogeneity invalidates pooling.
- Citing Booth 4th edition when 5th edition is the current release.
- Skipping the Warrant element in an argument because "it's obvious."
  If the warrant is truly obvious, stating it costs nothing; if it is
  not obvious, skipping it hides the weak link.
