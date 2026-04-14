---
title: Neta WebSearch Pipeline — Phase A-D Lightweight Retrieval for Cultural Context
tier: 2
---

# Neta WebSearch Pipeline

Tier 2 standard: references `neta-injection-techniques.md` (Tier 3)
for the 4 techniques themselves. This standard defines the runtime
**retrieval + application pipeline** that grounds neta injection in
up-to-date cultural context. The pipeline uses **WebSearch only** —
no RAG, no vector DB, no graph DB — consistent with the monkey-skills
"file-based, no external infra" principle.

Four phases: **A. Audience Context Retrieval**, **B. Structural
Deconstruction** (Chain-of-Thought), **C. Parameter Stitching**
(Strict Replacement Rule), **D. Vibe & Safety check**. The pipeline
is executed by `copy-neta-injection.md` protocol.

## Primary Sources

### Reasoning + tool-use canon

- **Wei, J. et al.** (2022) "Chain-of-Thought Prompting Elicits
  Reasoning in Large Language Models." arXiv:2201.11903.
  **Canonical** for step-by-step reasoning. Anchors Phase B
  structural deconstruction.
- **Yao, S. et al.** (2022) "ReAct: Synergizing Reasoning and Acting
  in Language Models." arXiv:2210.03629. **Canonical** for CoT +
  tool-use (WebSearch) hybrid as hallucination-reduction mechanism.
  Anchors the reasoning + retrieval combination.
- **Agentic RAG survey** arXiv:2501.09136 — dual-verify source for
  JIT retrieval positioning vs traditional RAG.

### Meme lifecycle canon

- **Dawkins, R.** (1976) *The Selfish Gene*, Ch. 11. Oxford UP.
  **Canonical.** Coins "meme" as unit of cultural transmission.
- **Shifman, L.** (2014) *Memes in Digital Culture*. MIT Press.
  ISBN 9780262525435. **Canonical** definitional primary source for
  internet memes as communication practice.
- **Cambridge *Humor 2.0* Ch. 16** "Half-Life of a Meme: The Rise
  and Fall of Memes" — documents meme lifespan trends.
- **Outline / Veix** meme half-life data: ≈4 months (2014), ≈6.25
  months (2012 peak), trending shorter year-over-year.

### Search operator documentation

- **Google Search Central** `site:` operator — formally documented
  search syntax for domain restriction.
- **LLM grounding literature** (arXiv:2604.03493, arXiv:2502.13497) —
  dual-verify sources on using specific subreddit / platform content
  as cultural ground truth.

## Critical Attribution Corrections

- **Drift note**: The Phase A-D pipeline itself is this team's
  synthesis. Individual phases are grounded as follows:
  - Phase A (Audience Context Retrieval): partial grounding on
    Google `site:` operator + LLM grounding papers; the specific
    domain allow-list is **team-curated**.
  - Phase B (Structural Deconstruction): **fully grounded** on Wei
    2022 + Yao 2022.
  - Phase C (Strict Replacement Rule): **team synthesis — no
    primary source identified**. This is explicitly flagged,
    parallel to the v4.15.0 action-weight taxonomy disclaimer.
  - Phase D (Vibe & Safety): partial grounding on Shifman 2014 +
    Cambridge *Humor 2.0* Ch. 16; gate rubric is fully grounded in
    `neta-safety-gate.md`.

## Framing — why WebSearch-only

### No RAG, no GraphRAG principle

monkey-skills is a **file-based skill system** with no external
infrastructure. This reflects three design constraints:

1. **Deployment simplicity**: the skill must run anywhere Claude
   runs, with no per-environment vector DB setup
2. **Freshness**: meme half-life is ≈4-6 months (Shifman 2014;
   Cambridge *Humor 2.0*); pre-indexed embeddings go stale faster
   than typical RAG refresh cadence
3. **Attribution + auditability**: WebSearch returns provenance
   (URLs, dates) inline; pre-indexed retrieval loses this

### RAG vs WebSearch JIT positioning

Agentic RAG surveys (arXiv:2501.09136) document the tradeoff:

| Dimension | RAG | WebSearch JIT |
|-----------|-----|---------------|
| Setup | Requires indexing + vector DB | Zero setup |
| Freshness | Limited by refresh cadence | Real-time |
| Attribution | Embedding-distance match; provenance via ID lookup | Direct URL + date in results |
| Infra cost | Persistent storage + compute | Pay-per-query |
| Scope control | Index-boundary determines scope | `site:` operator determines scope |
| Best fit | Stable domain knowledge | Fast-moving cultural content |

For neta injection, **fast-moving cultural content** dominates.
WebSearch JIT is the structural fit; RAG would be an over-
engineered choice.

**Synthesis disclaimer**: the RAG-vs-WebSearch-JIT positioning in
this standard is a defensible analytical synthesis, not a single
academic theorem. Cite agentic-RAG surveys + Shifman 2014 meme
lifecycle as grounding; do not cite this positioning as canonical.

## Phase A: Audience Context Retrieval

### Purpose

Retrieve up-to-date context on what the target audience is
**currently** referencing, sharing, and quoting. The output is a
catalog of candidate neta (classic references, trending memes,
in-group tokens, structural templates) that the audience would
recognize.

### Method

1. **Audience profiling** from intake Understanding Summary
   (`copywriting-brainstorming.md` Q3 target audience):
   - Age band, platform presence, subcultural affiliations
   - Content consumption patterns (which subreddits, which JP 2ch
     boards, which TikTok communities, which X JP clusters)

2. **Site-lock WebSearch queries** using documented `site:` operator
   (Google Search Central):
   - For JP audiences on X/Twitter: `site:twitter.com OR
     site:x.com [topic] lang:ja`
   - For JP 2ch archive: `site:2ch.sc OR site:5ch.net [topic]`
   - For English Reddit: `site:reddit.com/r/[relevant_subreddit]
     [topic]`
   - For JP niconico: `site:nicovideo.jp [topic]`
   - For TikTok comments: search via transcript-indexing services
     (since TikTok content is hard to crawl directly)

3. **Recency filter**: prefer results from within the meme
   half-life window (≈4-6 months per Shifman 2014). Anything older
   than 12 months should be re-checked for continued currency
   before use.

4. **Domain allow-list** (team-curated, NOT canonical):

   | Audience tier | JP sources | EN sources |
   |---------------|-----------|------------|
   | SNS-native youth | X JP, TikTok, niconico | Reddit, Twitter/X, TikTok |
   | Anime/manga fandom | 2ch, X JP, pixiv | Reddit r/anime, Crunchyroll forums |
   | Business / adult professional | はてなブックマーク, NewsPicks | LinkedIn, FT, WSJ |
   | Gaming | ふたば, niconico 実況 | Reddit r/games, Steam forums |

5. **Candidate catalog output**: list 5-15 candidate references
   with metadata (source URL, date, recognition assessment, in-group
   context).

### Failure modes

- **Zero results**: audience profile too narrow or too niche for
  WebSearch — escalate BLOCKED to user with intake refinement
  request
- **Outdated-only results**: audience moved platforms or the topic
  has no current discourse — signal to user that evergreen
  techniques (Reversal, Substitution, Cross-domain Mapping) are
  safer than current memes (Subcultural Capital
  in-group code)

## Phase B: Structural Deconstruction (Chain-of-Thought)

### Purpose

For each candidate reference, deconstruct its rhetorical structure
into a reusable template. Output is a formulaic pattern that can
be instantiated with product-specific parameters.

### Method

Apply Chain-of-Thought prompting (Wei et al. 2022, arXiv:2201.11903)
with explicit reasoning steps:

1. **Identify the reference's canonical form** ("what is the exact
   original phrasing, visual, or structural pattern?")
2. **Identify what makes it recognizable** ("which element is the
   recognition hook — a phrase, a frame, a visual token?")
3. **Identify the rhetorical operation** (per
   `neta-injection-techniques.md`):
   - Is it a reversal candidate? (Technique 1: Reversal — subvertising)
   - Is it a template/snowclone candidate? (Technique 2: Substitution — snowclone / 大喜利)
   - Is it an in-group code? (Technique 3: Subcultural Capital — tribal signal / 界隈消費)
   - Is it an analog mapping? (Technique 4: Cross-domain Mapping — conceptual simplification / 次元降下)
4. **Extract the reusable template** ("what stays fixed, what can
   be slotted?")
5. **Predict the reader cognition** ("what will the reader recognize,
   and what incongruity will they resolve into product meaning?")

### ReAct pattern (Yao et al. 2022, arXiv:2210.03629)

Interleave reasoning (CoT) with acting (WebSearch) when candidate
context requires verification:

```
Thought: This reference seems to be a 2024 TikTok meme — I need to
verify current usage before using it.
Act: search site:tiktok.com [reference] 2026
Observation: [WebSearch results]
Thought: Results show currency is ≤6 months; safe to use.
```

### Output

For each selected candidate: `{canonical form, recognition hook,
technique mapping, reusable template, predicted reader cognition}`.

## Phase C: Parameter Stitching (Strict Replacement Rule)

### Purpose

Instantiate the reusable template from Phase B with product-
specific parameters, producing draft copy.

### The Strict Replacement Rule

**Team synthesis — no primary-source grounding.** Flagged
transparently. The rule:

> Replace ONLY the parameter slots identified in Phase B. Do NOT
> modify the reference's recognition hook. Do NOT alter tense,
> voice, or punctuation that is load-bearing for the reference's
> identifiability.

**Why strict replacement matters**:
- Recognition depends on exact hook preservation (Raskin 1985
  script theory: the script is activated only if its identifying
  features match)
- Drift from the template breaks the incongruity-resolution cycle
  (Suls 1972) — reader cannot resolve the distortion back to the
  original, triggering confusion instead of recognition
- Partial matches fail worse than full misses (McGraw & Warren 2010
  benign-violation condition: violation must be recognizable, or
  it's not a violation — it's just odd)

### Method

1. Start from Phase B's reusable template (e.g.,
   `"X は Y の新 Z" with slots X, Y, Z`)
2. Enumerate what each slot must encode for the product message
3. Fill slots with minimum-drift parameters (prefer syllable /
   mora count matching; prefer similar grammatical category)
4. Preserve ALL non-slot elements verbatim
5. Validate by re-reading against the Phase B canonical form — the
   reference must still be recognizable after replacement

### Iteration rule

If a single parameter choice feels wrong, iterate only on that
parameter. Do NOT relax the Strict Replacement Rule by modifying
multiple slots or bending template structure. If no parameter
choice works, the candidate is a **bad fit** — discard and try
another from Phase A's catalog.

### Output

Draft copy with neta injection applied, annotated with (a) original
reference source, (b) technique used, (c) slot-fill mapping.

## Phase D: Vibe & Safety Check

### Purpose

Verify that the draft passes safety criteria before delivery.

### Method

Run `neta-safety-gate.md` SHOULD gate (see rubric file for full
criteria). Summary of dimensions:

| Dimension | Check |
|-----------|-------|
| Cringe index | Traffic-light; Red → revise |
| Copyright / trademark risk | **Hard veto**: fair use (17 USC § 107) / 著作権法 32条 applicability |
| 景表法 ステマ risk | **Hard veto**: brand-influence + identifiability test (消費者庁 2023-10-01 告示) |
| 圈層 match | Traffic-light; Red → revise |
| Timeliness | Traffic-light; Red (expired meme) → revise |

**Hard legal vetoes** (copyright + ステマ) block delivery regardless
of other gate outcomes. This is non-fungible risk.

### Pre-gate self-check

Before launching evaluator, worker performs SELF Check:
1. Is the reference's recognition hook preserved intact?
2. Could a reasonable first-time reader parse this without the
   reference (fallback readability)?
3. Does the reference carry product meaning (not merely
   cleverness)?
4. Has the reference been checked for currency within meme
   half-life window?
5. Could this be mistaken for 真正 UGC (ステマ risk)?

If any answer is uncertain, revise before gate.

### Post-gate handling

- **PASS**: deliver with attribution metadata (technique used,
  source reference, confidence assessment)
- **PASS_WITH_NOTES** (yellow flags, no hard vetoes): deliver with
  explicit disclosure of the flagged dimension and mitigation taken
- **NEEDS_REVISION** (red flag or hard veto): return to Phase A or
  B; if all candidates fail, escalate BLOCKED to user

## Integration with other copywriting-team standards

### With `neta-injection-techniques.md` (Tier 3)

This Tier 2 pipeline standard operationalizes the Tier 3 technique
standard. References in Phase B's deconstruction step map directly
to the 4 techniques (Reversal / Substitution / Subcultural Capital /
Cross-domain Mapping).

### With `write-short-form-copy.md` / `write-long-form-copy.md` / `write-mid-form-copy.md`

Neta injection is an **optional post-production layer**. The base
framework (PASONA / BEAF / CREMA / キャッチコピー) produces initial
draft; neta injection optionally transforms the draft via Phase A-D.

### With `copywriting-brainstorming.md`

Intake Q must surface "neta 使用許可" as a Level 2 field (opt-in).
If brand voice or channel policy forbids neta injection, skip this
pipeline entirely.

### With `neta-safety-gate.md`

Phase D invokes the gate rubric. Gate is SHOULD tier per team
convention; hard legal vetoes elevate specific dimensions to
NEEDS_REVISION without fungibility.

## Anti-Patterns

- **Skipping Phase A (Audience Context Retrieval)**. Assuming
  "general knowledge" of memes from the model's pre-training is a
  recipe for using expired references. Meme half-life is 4-6 months;
  pre-training data is typically older.
- **Violating the Strict Replacement Rule**. Modifying more than
  template slots breaks recognition. If multiple slots need custom
  structure, you have a different reference or no reference; don't
  hybridize.
- **Skipping Phase D safety check**. Neta injection carries
  non-trivial legal + reputational risk; the safety gate is
  non-optional.
- **Using RAG or pre-indexed retrieval for neta**. Violates
  file-based skill principle AND meme freshness requirement. Use
  WebSearch.
- **Citing the pipeline as canonical**. Phase A-D is this team's
  synthesis. Individual phase components are grounded (see Primary
  Sources); the pipeline assembly itself is operational, not
  canonical.
- **Omitting `site:` restriction**. Broad WebSearch without domain
  constraint returns too much noise and fails recency.
- **Treating Phase B's template as product-agnostic**. A template
  that "works for any product" is suspect — it probably means the
  reference is too generic to add value.
- **Chaining too many techniques in one piece**. One technique per
  piece, per 眞木's「ダジャレではなく、オシャレです」principle
  (cross-ref `jp-copy-craft-lineage.md` §眞木).
- **Trusting a single WebSearch result as recency ground truth**.
  Confirm via 2+ independent sources before using a reference as
  "current." One post doesn't prove a meme is alive.
