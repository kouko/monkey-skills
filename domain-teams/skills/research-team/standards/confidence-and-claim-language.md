---
title: Confidence and Claim Language
tier: 2
---

# Confidence and Claim Language

Defines the vocabulary research-team uses to communicate **how confident
a claim is** (confidence) and **how likely an outcome is** (likelihood),
plus the distinction between fact, analysis, and speculation. Tier 2:
LLMs know the IPCC framework names but routinely muddle the 5-level
confidence ladder, the 7-level likelihood ladder, and the 3×3
evidence × agreement grid. The body spells out the exact levels, their
numerical ranges, and the orthogonality rule.

## Primary Sources

- Michael D. Mastrandrea, Christopher B. Field, Thomas F. Stocker, Ottmar Edenhofer, Kristie L. Ebi, David J. Frame, Hermann Held, Elmar Kriegler, Katharine J. Mach, Patrick R. Matschoss, Gian-Kasper Plattner, Gary W. Yohe, Francis W. Zwiers (2010) *Guidance Note for Lead Authors of the IPCC Fifth Assessment Report on Consistent Treatment of Uncertainties*. IPCC. https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf. Canonical source for the IPCC AR5 5-level confidence ladder, 7-level likelihood ladder, and the 3×3 evidence × agreement grid.
- Sherman Kent (1964) "Words of Estimative Probability". *Studies in Intelligence* 8(4). https://www.cia.gov/resources/csi/studies-in-intelligence/archives/vol-8-no-4/words-of-estimative-probability/. The origin of the intelligence-community discipline of mapping natural-language hedging words to numerical probability ranges, which IPCC AR5 operationalized.
- Philip E. Tetlock & Dan Gardner (2015) *Superforecasting: The Art and Science of Prediction*. Crown. Ch.5 "Supersmart" and Ch.6 "Superquants?" are the empirical evidence base for calibrated probabilistic forecasting; Ch.4 grounds why point estimates with no confidence bands are worse than calibrated ranges.

## Critical Attribution Corrections

### 6-month freshness threshold is internal convention, not IPCC

The "flag sources older than 6 months for fast-moving topics" rule
retained in `citation-standards.md` is a **research-team internal
operational convention**, not an IPCC AR5 guidance. IPCC, PRISMA, and
Cochrane do not prescribe any numerical freshness cutoff; they prescribe
**judgment about relevance for the research question**. The 6-month
figure is a heuristic calibrated for the kinds of technology, market,
and policy topics research-team typically investigates. When citing
the freshness rule, disclose it as internal convention, not as
IPCC-grounded.

## IPCC AR5 Confidence — the 5-Level Ladder

Confidence expresses **the author's evaluation of the validity of a
finding**, based on the type, amount, quality, and consistency of
evidence and the degree of agreement across independent lines of
evidence. IPCC AR5 uses **exactly 5 levels** (not 3, not 4, not 6):

| Level | Name | When to use |
|---|---|---|
| 1 | **Very low confidence** | Limited evidence and/or low agreement among sources |
| 2 | **Low confidence** | Limited or medium evidence and/or low-to-medium agreement |
| 3 | **Medium confidence** | Medium evidence and medium agreement |
| 4 | **High confidence** | Robust evidence and/or high agreement |
| 5 | **Very high confidence** | Robust evidence and high agreement |

Confidence answers: "how much should a reader trust the claim?" It
is **not** a probability — a claim can be "very high confidence"
about something that is unlikely to occur ("very high confidence that
the probability of X is below 10%").

## IPCC AR5 Likelihood — the 7-Level Ladder with Percentages

Likelihood expresses **the probability that an event will occur or a
hypothesis is true**. IPCC AR5 maps natural-language likelihood terms
to exact percentage ranges so different authors use the same words to
mean the same thing:

| Term | Probability range |
|---|---|
| **Virtually certain** | 99–100% |
| **Very likely** | 90–100% |
| **Likely** | 66–100% |
| **About as likely as not** | 33–66% |
| **Unlikely** | 0–33% |
| **Very unlikely** | 0–10% |
| **Exceptionally unlikely** | 0–1% |

(Additional IPCC terms **extremely likely** 95–100% and **more likely
than not** >50–100% are used selectively; the 7 above are the core
ladder.)

### Confidence and likelihood are orthogonal

A claim has **both** a confidence level (how robust is the evidence?)
and, when applicable, a likelihood statement (what is the probability?).
You can have:

- **High confidence, very likely** — "We are highly confident that
  warming by 2100 is very likely to exceed 1.5°C" — robust evidence and
  high probability
- **High confidence, unlikely** — "We are highly confident that a
  complete ice-sheet collapse this century is unlikely" — robust
  evidence and low probability
- **Low confidence** (no likelihood statement) — evidence is too sparse
  to attach a probability; report qualitatively only

**Do not collapse confidence and likelihood into a single score.**
Confidence is about the evidence base; likelihood is about the
probability of the outcome. They are orthogonal.

## Evidence × Agreement — the 3×3 Grid

IPCC AR5 decomposes confidence into two sub-dimensions:

- **Evidence** — the amount, type, quality, and consistency of the
  data / studies available: **limited / medium / robust**
- **Agreement** — the degree to which independent lines of evidence
  and independent authors converge: **low / medium / high**

The cross product gives a 3×3 grid that authors fill in to choose the
confidence level:

|  | **Agreement: Low** | **Agreement: Medium** | **Agreement: High** |
|---|---|---|---|
| **Evidence: Robust** | Low-to-medium confidence | Medium-to-high confidence | **Very high confidence** |
| **Evidence: Medium** | Low confidence | Medium confidence | High confidence |
| **Evidence: Limited** | **Very low confidence** | Low confidence | Low-to-medium confidence |

The diagonal top-right cell (robust evidence × high agreement) is the
only cell that supports a "very high confidence" verdict; the diagonal
bottom-left cell (limited evidence × low agreement) is the only cell
that forces "very low confidence". Everything else is in between, and
the 3×3 grid makes the judgment reproducible.

## Kent 1964 — the Origin of Estimative-Probability Discipline

Sherman Kent was an analyst at the CIA's Board of National Estimates
who, in 1964, published "Words of Estimative Probability" after
discovering that different readers of the same intelligence estimate
interpreted phrases like "serious possibility" to mean anywhere from
20% to 80%. Kent proposed mapping estimative words to numerical
probability ranges, a discipline that IPCC AR5 later adopted and
formalized. The core insight: **natural-language hedging is not
neutral — it leaks ambiguity that calibrated numerical ranges fix.**

Research-team applies this insight by requiring that every "likely"
or "unlikely" claim in a deliverable either maps to the IPCC 7-level
ladder above or is rewritten to be qualitative-only (when likelihood
cannot be assigned).

## Tetlock & Gardner 2015 — Calibration as an Empirical Discipline

Tetlock's Good Judgment Project (2011-2015 IARPA tournament) produced
the empirical evidence that calibrated probabilistic forecasting is a
**learnable skill**, not an innate gift. Three of Tetlock's findings
are load-bearing for research-team:

1. **Granular probability estimates beat vague hedging.** Forecasters
   who said "there is a 62% chance" outperformed forecasters who said
   "this is likely" even when they were drawing on the same information.
2. **Aggregating independent forecasts outperforms any single
   forecaster.** This grounds the "cross-verify across 2+ independent
   sources" rule in `citation-standards.md`.
3. **Reviewing your past forecasts for calibration is the single
   strongest improvement lever.** Forecasters who audited their own
   track records improved; forecasters who did not stagnated.

Tetlock's discipline maps directly to research-team's confidence +
likelihood tagging: tagging forces calibration, and retaining the tags
in the output record enables future audit.

## Mapping Research-Team 高/中/低 to IPCC 5-Tier

Research-team's existing 3-level high/medium/low confidence tagging
maps to the IPCC 5-level ladder as follows:

| Research-team tag | IPCC level |
|---|---|
| **高 (High)** | High or Very high confidence |
| **中 (Medium)** | Medium confidence |
| **低 (Low)** | Low or Very low confidence |

The 3-level mapping is deliberately coarser than the 5-level IPCC
ladder because research-team deliverables are not climate assessments
and a 5-way distinction is more overhead than the use case warrants.
Workers who need the full 5-level distinction (e.g., when the
deliverable will be further aggregated by another researcher) MAY
report at the 5-level granularity, disclosing the choice.

## Fact / Analysis / Speculation Taxonomy

Every sentence in a research deliverable is one of three categories,
and the category MUST be explicit:

| Category | Definition | Required evidence | Example |
|---|---|---|---|
| **事實 Fact** | A verifiable observation attributed to a primary / secondary source, or a raw data point. | Cited, source accessible to reader, date attached. | "Google open-sourced Kubernetes on 2014-06-07 (Google Cloud Platform Blog 2014-06-07)." |
| **分析 Analysis** | A reasoned inference from facts. Logic chain must be explicit; premises must themselves be facts. | All input premises must be cited facts; the inference itself is the author's contribution. | "Because Kubernetes was open-sourced before the CNCF's launch (fact) and the CNCF adopted Kubernetes as its seed project (fact), Kubernetes' licensing posture predates CNCF governance (analysis)." |
| **推測 Speculation** | A forward-looking or uncertain claim. Must be hedged with explicit probability language (IPCC ladder) and confidence level. | Confidence and likelihood tags REQUIRED; must name the key uncertainty that would resolve the speculation. | "Kubernetes operator pattern adoption is **likely** (66-100%) to continue growing through 2027 (**medium confidence**) based on the current CNCF landscape trajectory; the key uncertainty is enterprise tooling consolidation." |

The taxonomy is non-negotiable: untagged sentences leak the distinction
between observation, inference, and guess, which is the single most
common failure mode for LLM-generated research output. A deliverable
where every sentence is tagged is auditable; a deliverable where the
tags are missing is not.

## Anti-Patterns

- Using the word "likely" without mapping it to the IPCC ladder
  (66-100%). A reader cannot tell whether you mean 55% or 90%.
- Collapsing confidence and likelihood into a single "confidence score".
  They are orthogonal — keep them separate.
- Omitting the tag on speculative sentences. Untagged speculation reads
  as fact to downstream readers and propagates.
- Claiming "very high confidence" without the 3×3 grid supporting it
  (robust evidence × high agreement).
- Citing the 6-month freshness rule as if it were an IPCC standard.
  It is a research-team internal convention; disclose it as such.
