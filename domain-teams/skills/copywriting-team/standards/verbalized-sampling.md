---
title: Verbalized Sampling (Zhang et al. 2025)
tier: 2
---

# Verbalized Sampling

Tier 2 standard: technique level. A prompt technique for mitigating
**mode collapse (typicality bias)** caused by LLM post-training
alignment (RLHF, etc.). Proposed by Zhang et al. 2025
(arXiv:2510.01171). By explicitly requesting "**multiple candidates
+ each candidate's probability distribution**" in the prompt, it
elicits modes beyond the default modality. Training-free /
model-agnostic / orthogonal to temperature. In copywriting-team,
it operates as **lexical-layer diversity** complementing Mandal-Art
(structural-layer diversity).

## Primary Sources

- Jiayi Zhang et al. (2025) "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity" arXiv:2510.01171 https://arxiv.org/abs/2510.01171 — canonical paper. Theory proposal, experiment design, 2–3× diversity improvement measured on 8 benchmarks.
- OpenReview discussion thread for arXiv:2510.01171 https://openreview.net/forum?id=verbalized-sampling — secondary dual-verify source: reviewer comments and explicit statement of limitation conditions (model-size effect gap).
- CHATS-lab/verbalized-sampling (GitHub) https://github.com/CHATS-lab/verbalized-sampling — official implementation repository. Prompt template and reproduction scripts as one-source reference.

## Framing

Large language models develop a bias toward "safe, typical outputs"
after post-training (RLHF, DPO, Constitutional AI, etc.). When
sampling the same prompt many times, outputs concentrate into a few
modes, losing diversity — this is **mode collapse**. Zhang et al. 2025
formalize this as **typicality bias** (concentration near the training-
data centroid) and propose Verbalized Sampling as a prompt technique
to counteract it.

From a copywriting perspective, mode collapse is critical: if the LLM
returns "10 similar safe lines" for ad copy generation, the divergence
stage lacks sufficient diversity, and the convergence stage's effective
options shrink to 1–2. Verbalized Sampling is a training-free
countermeasure for this symptom.

## Technical principle

### Baseline (prompt where mode collapse occurs)

```
Prompt: Write a catch copy for product X.
```

The LLM follows its post-training bias toward "one safe, typical line."
Even 100 samples converge into the top 3–5 modes.

### Verbalized Sampling (mode collapse mitigation)

```
Prompt: Generate 5 catch copies for product X along with their
probabilities. Format:
  1. [copy] — probability: X%
  2. [copy] — probability: Y%
  ...
```

This prompt demands two things from the LLM:
1. **List multiple candidates at once** (single-shot multi-output)
2. **Explicitly assign relative probabilities to each** (verbalized
   distribution)

The LLM, constructing its answer as a probability distribution,
**draws from a wider range of internal modes**. As a result, modes
beyond the top-1 candidate surface in the prompt output.

### Why it works

Zhang et al. 2025's theoretical explanation:
- **Typicality bias** manifests most strongly when "a single output is
  requested." The LLM's training objective makes it return "the most
  'typical' single line."
- **A prompt requesting multiple candidates + probability distribution**
  shifts the LLM's role from "typical-returning agent" to "distribution-
  describing reporter." In reporter mode, describing a multimodal
  distribution becomes natural behavior.
- **The probability field is critical**. Removing probabilities causes
  mode collapse even with multi-listing (paper §4 Ablation). Verbalizing
  probabilities is the trigger that switches to distribution thinking.

## Effects

Zhang et al. 2025 measurements (paper §5 Experiments):

- **Diversity improvement** — 2–3× distinct-n improvement across 8
  benchmarks (joke generation, story, dialogue, etc.)
- **Quality preservation** — diversity improvement does not degrade
  quality (human-evaluated A/B test)
- **Model-agnostic** — effective on GPT-4/4o, Claude 3.5 Sonnet,
  Gemini 1.5 Pro, Llama 3 70B/8B
- **Training-free** — no model retraining needed, prompt-only change
- **Orthogonal to temperature** — usable alongside temperature
  increase, effects are additive

## Complementary relationship with Mandal-Art

In copywriting-team's ideation pipeline, the two tools handle different
layers of diversity:

| Layer | Tool | What it diversifies |
|---|---|---|
| Structural (angle) layer | Mandal-Art 3×3 | 8 **approach angles** covered. Frame selection such as "write from daily-life scenario vs. write from numbers" |
| Lexical (expression) layer | Verbalized Sampling | **vocabulary / expression variation** within the same angle. E.g. "high moisturizing power" vs. "makes tomorrow morning's mirror check something to look forward to" |

Use them **in combination**, not alone:

```
【Step 1】Mandal-Art: 8 angles × 1 copy = 8 candidates (structural diversity)
【Step 2】For each angle, Verbalized Sampling: 5 candidates (lexical diversity)
【Step 3】Total 8 × 5 = 40 candidates → KJ法 convergence (ideation-kj-convergence.md)
```

Applying VS across Mandal-Art's 8 directions yields 40–80 candidates,
meeting 谷山's「散らかす」volume target of 64–100.

## Production rules (subagent prompt template)

Embed the following patterns in copywriting-team's ideation subagent
prompt:

### Pattern A: diversify within a single angle

```
【Task】Write catch copies for product: {product}
【Angle】{angle}（例：感官描写）

【Output format】Generate exactly 5 candidates along with probabilities.
Use format:
  1. [copy text, 7-15 chars] — probability: X%
  2. [copy text, 7-15 chars] — probability: Y%
  3. [copy text, 7-15 chars] — probability: Z%
  4. [copy text, 7-15 chars] — probability: W%
  5. [copy text, 7-15 chars] — probability: V%

Probabilities must sum to ~100%. Include both high-probability
(typical) and low-probability (unusual) candidates to reflect the
full distribution.
```

#### Forced probability allocation (optional)

For briefs that need explicit tail coverage (not just "include both
high and low"), specify an allocation shape instead of "sum to ~100%":

| Slot | Probability | Role |
|---|---|---|
| Option 1 | >60% | The typical, expected direction |
| Option 2 | ~25% | Secondary, still conventional |
| Options 3–N | <5% each | Long-tail, counter-intuitive |

This forces subagents to reach the tail rather than clustering at
high-probability candidates. Use when Pattern A's soft hint ("include
both") is not producing enough tail coverage — typically detected by
evaluator (Pattern C) flagging probability skew.

### Pattern A+: long-tail forced sampling (進階版)

Upgrade of Pattern A for briefs that deliberately require tail-mode
extraction — guerrilla marketing, counter-intuitive positioning,
viral-seed hunting. Adds two hard constraints absent from Pattern A:

1. **Probability cap** — every candidate's probability must be below
   a user-specified cap (typical: 0.10 for mild tail, 0.05 for
   aggressive tail).
2. **Explicit long-tail directive** — "Deliberately sample from the
   long tails of your internal probability distribution, not the
   typical mode."

Pattern A+ template:

```
【Task】Write catch copies for product: {product}
【Angle】{angle}

【Output format】Generate exactly {N} candidates.
Wrap each in <response> tags containing:
  <text>: the copy body ({char range})
  <probability>: your estimated typical generation probability

⚠️ Critical constraint: every <probability> must be less than
{probability_cap} (typical: 0.10). Deliberately sample from the
long tails of your internal probability distribution — avoid the
typical mode entirely.
```

When to use Pattern A+:
- Guerrilla / viral / counter-intuitive brief
- Existing mainstream copy pool already exhausted
- Campaign explicitly wants "un-ChatGPT" outputs

When NOT to use:
- Default copy generation — stay on Pattern A. Pattern A+ lowers
  average copy-quality floor in exchange for tail coverage; only
  worth it when the brief explicitly prizes the tail.
- Small models (7B and below) — cap enforcement is unreliable and
  numeric thresholds get ignored (see Limitations §model-size gap).

Derivation: Zhang et al. 2025 §5 experimental setup explicitly uses
probability thresholds in the tail-sampling condition — Pattern A+
is a direct application of that experimental protocol to copy
ideation.

### Pattern B: combined with Mandal-Art 8 angles

```
【Task】Generate catch copies for product: {product}
【Mandal-Art angles】{8 angles from ideation-mandalart.md}

【Output format】For each of the 8 angles, generate 5 candidates
with probabilities. Total 40 candidates.

Angle 1: {angle name}
  1. [copy] — probability: X%
  ... (5 candidates)

Angle 2: {angle name}
  1. [copy] — probability: X%
  ... (5 candidates)

... (8 angles total)
```

### Pattern C: integration with evaluator

The worker-output probabilities serve as an inspection axis for the
evaluator: "**are there meaningful candidates even among low-probability
ones?**" If all candidates cluster near high probability, this is a
sign that mode collapse was not effectively mitigated, and a
re-generate directive should be issued.

## Limitations and caveats

- **Model-size effect gap** — Zhang et al. 2025 §6 Limitations: effects
  are clear with large models (GPT-4, Claude 3.5 Sonnet, Gemini 1.5
  Pro); effects are unstable with small models (7B and below). Do not
  over-expect results when using 7B-class local models in
  copywriting-team.
- **Probabilities are not "true probabilities"** — the probabilities
  the LLM verbalizes are not a faithful projection of its internal
  probability distribution; their primary role is prompt triggering
  toward distribution thinking. Do not treat the numbers as
  statistically rigorous.
- **Unverified domain generalization** — the paper's evaluation is
  primarily English. Effectiveness for JP copy / advertising-specific
  corpora requires separate dogfood verification (this team's future
  tuning topic, grounding-v4.12.0.md §9 Open questions reference).
- **Distinction from temperature** — raising temperature alone also
  increases diversity but tends to degrade quality. VS raises diversity
  while preserving quality — this is its differentiation. When using
  both, temperature 0.7–0.9 + VS is the typical combination.

## Anti-Patterns

- **Using VS as a replacement** — intending to replace Mandal-Art
  entirely with VS alone. Mandal-Art handles structural-layer
  diversity; VS handles lexical-layer diversity — they cover different
  layers. Using only one leaves the other layer's diversity unmet.
- **Dropping the probability field** — calling it "verbalized
  distribution" in name only, multi-listing without requiring
  probabilities. Paper §4 Ablation shows this eliminates the effect.
  Probabilities are the core triggering mechanism.
- **Mistaking "list 5" as sufficient** — multi-listing without
  probabilities merely selects 5 lines from top modes and does not
  resolve mode collapse.
- **Completing「散らかす」with VS alone** — even if VS produces 40
  candidates solo, they may all be expression variants within a single
  angle (e.g. sensory description only), lacking structural-layer
  coverage. Mandal-Art × VS combination is required.
- **Treating LLM probabilities as statistical quantities** — using
  verbalized probabilities as "true internal distribution" for Bayesian
  updates, etc. The paper claims a triggering effect; statistical
  meaning of the numbers is not guaranteed.
- **Expecting equivalent effects from small models** — expecting 2–3×
  improvement from 7B-class models as in the paper. Stable effects
  appear only with large models. For small models, temperature tuning
  is more efficient.
- **Positioning temperature as antagonistic** — creating a "VS or
  temperature" binary choice. The two are orthogonal with additive
  effects; combined use is recommended.
- **Invoking "極限版" (contrarian-persona + absurd quota + temp=1.2)
  inside copywriting-team** — extreme-creativity tiers (contrarian
  system persona + "at least half must be counter-intuitive /
  borderline absurd" + temperature=1.2 / top_p=0.99) target
  creative-writing extremes, not production ad copy. For campaign
  copy, stay at Pattern A (basic) or Pattern A+ (judged probability
  cap). Extreme tiers drop copy-usability floor below production
  threshold; use VS directly outside copywriting-team if genuinely
  needed.
