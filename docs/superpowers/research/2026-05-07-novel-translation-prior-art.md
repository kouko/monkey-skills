# Novel / Long-form LLM Translation — Prior Art Survey

**Date**: 2026-05-07
**Surveyed by**: research subagent (~10 min, 7 projects, 6 architectural dimensions)
**Trigger**: post-merge of `translation-toolkit` v0.2.0 Tier 1 (PR #262); user asked whether the implementation referenced any similar-purpose project
**Status**: One-shot — re-run before Tier 2 plan if landscape has shifted

## Quick verdict

Nobody else has solved scene-aware splitting the way `translation-novel` v0.2.0 does. Every surveyed project chunks at **sentence / JSON record** (Galgame line) or **whole-chapter file** or **fixed token budget**, never at literary-scene boundary with marker hierarchy.

Three Tier 2 candidates clearly worth borrowing:

1. **Two-pass cumulative-glossary build** (darkautism / qw02) — directly informs deferred Tier 2 character/world pre-pass.
2. **Rule-based residual-language / length-violation auto-detect** (GalTransl `problemAnalyze`) — cheap deterministic pre-S1 gate, no LLM cost.
3. **Critic role-split** (TransAgents prep → translate → localize → proofread) — informs Tier 2 5D literary reflect axis design.

Selective per-request term injection (our caller-filter design) is industry standard — confirmed across GalTransl + manga-image-translator + ours. Andrew Ng TA passes all-source-as-context but no target-side prev — **our prev-v2 target-side window is unique** in the surveyed set.

## Comparison matrix

| Project | D1 Chunking | D2 Cross-chunk | D3 Glossary | D4 Gates | D5 Multi-pass | D6 Cost |
|---|---|---|---|---|---|---|
| **translation-novel v0.2.0 (us)** | scene-aware (heading > marker > blank-gap > token-fill) | prev v2 ~500 tok target + next ~200 tok source | caller-filter L1-L4; matched-only injection | M1+M2 HARD, S1+S2 SHOULD, I1 INFO | DRAFT → REFLECT 4D → IMPROVE per scene | O(N), 17× vs whole-doc |
| **Andrew Ng TA** | RecursiveCharacterTextSplitter, 1000 tok | all prev + all next **source** wrapped in `<TRANSLATE_THIS>`; no target-side | extension idea only, not impl | reflection only | DRAFT → REFLECT → IMPROVE | O(N²) — passes whole doc per chunk |
| **GalTransl** | per-dialogue-line JSON record (sentence) | none across lines; context = GPT-Dict only | 3-tier dict (GPT-dict / pre-tl / post-tl); selective injection on name match; manual curation | rule-based `problemAnalyze`: residual JP, punct, length, dict compliance | optional proofread pass (`pre_zh` → `proofread_zh`) | per-line cache; selective dict inject |
| **darkautism ai-novel-translation** | per-chapter `.txt` file | cumulative glossary (no prev-translation pass-through) | **two-pass: Pass 1 extracts terms + summary; Pass 2 translates with cumulative glossary**; manual edit | none documented | 2-pass (analysis → translation) | — |
| **qw02 llm-novel-translator** | per-chapter | cumulative auto-glossary across chapters | auto-extract proper nouns (names/places/cultivation ranks); separate model for extraction vs translation | — | implicit 2-step (extract then translate) | configurable model split |
| **manga-image-translator** | per-bubble OCR text | `--context-size` = N **pages** (OpenAI translator only) | auto-extract relevant glossary entries from large dict (filtered) | — | `translator_chain` lets you stack translators sequentially | filtering avoids whole-dict bloat |
| **TransAgents** (academic) | per-chapter | guidelines + glossary + summaries built in **prep phase**; tone/style fixed up front | Junior Editor proposes, Senior Editor refines glossary in prep phase | structured stage gates (translate → cultural adapt → proofread → final review) by role | 4 substages with named agent roles | trilateral judge ends discussion early to cap context bloat |
| **TranslateBooksWithLLMs / KazKozDev book-translator** | token-based, default 400 tok | checkpoint/resume only; cross-chunk context not explicitly documented | none | none | `--refine` 2nd pass for literary polish | cache-aware |

## Per-project notes

### Andrew Ng Translation Agent (TA)

Confirmed via source: `multichunk_initial_translation` and `multichunk_reflect_on_translation` both pass full prev+next **source** chunks wrapped in `<TRANSLATE_THIS>`. No target-side context, no glossary code. Source: [translation-agent/utils.py](https://github.com/andrewyng/translation-agent/blob/main/src/translation_agent/utils.py). **Don't borrow** — the O(N²) cost is exactly what we fixed.

### GalTransl

Selective term injection: *"only when the current request contains this character name and sentence will this term's explanation be sent into this round of conversation"* — same principle as our caller-filter. Their `problemAnalyze` rule-based gate (residual-JP, punct, length, dict-compliance) is a cheap deterministic pre-LLM gate. **Borrow the rule-based gate concept** as a pre-S1 cheap filter. Source: [GalTransl README](https://github.com/GalTransl/GalTransl/blob/main/README.md).

### darkautism / ai-novel-translation

**Two-pass cumulative-glossary** is the cleanest expression of our deferred Tier 2 character/world pre-pass. Per-chapter Pass 1 = analysis (summary + new term extraction → glossary JSON), Pass 2 = translation using cumulative glossary. Manual edit allowed. Source: [README](https://github.com/darkautism/ai-novel-translation). **Borrow** — informs Tier 2 pre-pass design.

### qw02 / llm-novel-translator

Same auto-cumulative glossary pattern, plus the architectural choice of using a **different (smaller/cheaper) model for extraction** vs the translation model. Source: [README](https://github.com/qw02/llm-novel-translator). **Borrow the model-split idea** for cost.

### manga-image-translator

Confirms keyword-extraction filtering is industry pattern (`mit_glossory`, `sakura_dict`). `--context-size` is pages-of-context but only on OpenAI translator. Source: [README](https://github.com/zyddnys/manga-image-translator/blob/main/README.md). **Already aligned**.

### TransAgents (academic)

Multi-agent role-based (CEO / Senior Editor / Junior Editor / Translator / Localizer / Proofreader); preparation phase builds glossary + tone + chapter summaries up-front; "trilateral collaboration" judge halts looping. Human eval said "more expressive and captivating." Source: [Gonzo-ML summary](https://gonzoml.substack.com/p/perhaps-beyond-human-translation). **Borrow concept** for 5D literary reflect — separate "localization" axis from "accuracy" axis.

### TranslateBooksWithLLMs / KazKozDev book-translator

Both have explicit `--refine` / "stage-two refinement" 2-pass pattern. Sources: [hydropix/TranslateBooksWithLLMs](https://github.com/hydropix/TranslateBooksWithLLMs), [KazKozDev/book-translator](https://github.com/KazKozDev/book-translator). **Already aligned** with our DRAFT → REFLECT → IMPROVE.

## Findings

### Already-aligned (architectural consensus)

- **Multi-pass DRAFT + refine** — TA, GalTransl proofread, KazKozDev stage-two, hydropix `--refine`, TransAgents 4-stage. Universal pattern.
- **Selective per-request term injection** (not full-glossary dump) — GalTransl, manga-image-translator, ours. Strong consensus.
- **Cumulative glossary across units** — darkautism, qw02, GalTransl GPT-Dict. Ours via `glossary.json` + L1-L4 caller-filter aligns.

### Potentially worth borrowing (Tier 2 candidates)

- **Two-pass whole-book pre-pass** (darkautism Pass 1 / TransAgents prep phase / qw02 auto-glossary) — directly informs Tier 2 deferred *Pre-pass character/world-glossary extraction*. Pattern: cheap model reads each chapter, outputs `{names, terms, summary}`; merged JSON seeds project glossary. **Strong borrow.**
- **Cheap-model split** (qw02: separate extraction model vs translation model) — cost lever for Tier 2 pre-pass to keep total cost bounded. **Borrow.**
- **Rule-based deterministic gate** (GalTransl `problemAnalyze`: residual source-language chars, punctuation, length-ratio, dict-compliance) — add as a **pre-S1 cheap gate** in our verification stack; runs without LLM. **Borrow.**
- **Trilateral judge / role-split** (TransAgents) — informs Tier 2 5D literary reflect — separate "accuracy/fluency" critic from "literary/style" critic. **Borrow concept**, not full multi-agent infra.
- **Voice-bin sampling for cross-chapter character voice** — not seen in any surveyed project; our deferred Tier 3 S3 voice-consistency gate appears to be **architecturally novel**. Consider as future research-positioning.

### Things only we do (differentiation)

- **Scene-boundary class hierarchy** (heading > explicit marker > blank-gap > fallback). All others split at sentence (Galgame), chapter file (novel tools), or token budget (TA).
- **Target-side prev-v2 window** for voice continuity. TA passes all prev+next as **source only**; nobody else passes the prev chunk's *translation* back as context.
- **Round-trip byte-conservation** in scene splitting — not addressed elsewhere.
- **5-gate post-translation verification** (M1 / M2 / S1 / S2 / I1) with HARD / SHOULD / INFO tiers. GalTransl has rule-based detect; nobody else has gates as a tier-graded contract.

### Things they do that we explicitly chose NOT to do

- **Whole-doc source as context** (Andrew Ng TA `<TRANSLATE_THIS>` pattern) — explicitly rejected; this *is* the O(N²) problem we solved.
- **Per-line / sentence chunking** (GalTransl) — appropriate for Galgame structure (each line is a UI unit) but inappropriate for prose narrative; literary scene is the right unit for novels.
- **Multi-agent role hierarchy** (TransAgents 6 named agents) — too heavy for a skill; we collapsed to single agent with multi-pass prompt design.

## Open questions

- **TransAgents prep-phase glossary granularity** — paper digest doesn't say whether glossary is per-chapter or whole-book; would need the paper itself for Tier 2 pre-pass design specifics.
- **Sakura ecosystem** — surveyed only via downstream consumers (Eason0729, GalTransl integration); the upstream Sakura-13B-Galgame project README appears focused on model rather than pipeline — would require deeper dive if Sakura's *application-layer* design has more.
- **mtool / 萌翻** — searches surfaced GalTransl ecosystem instead; if these have distinct designs, not found in 10 minutes.
- **Cost numbers** for darkautism / qw02 / TransAgents — none publish $/100k-tokens benchmarks; our 17× claim has no comparable competitor data.

## Sources

- [GalTransl README](https://github.com/GalTransl/GalTransl/blob/main/README.md)
- [Andrew Ng translation-agent utils.py](https://github.com/andrewyng/translation-agent/blob/main/src/translation_agent/utils.py)
- [qw02 / llm-novel-translator](https://github.com/qw02/llm-novel-translator)
- [darkautism / ai-novel-translation](https://github.com/darkautism/ai-novel-translation)
- [zyddnys / manga-image-translator](https://github.com/zyddnys/manga-image-translator/blob/main/README.md)
- [TransAgents (Gonzo-ML digest)](https://gonzoml.substack.com/p/perhaps-beyond-human-translation)
- [hydropix / TranslateBooksWithLLMs](https://github.com/hydropix/TranslateBooksWithLLMs)
- [KazKozDev / book-translator](https://github.com/KazKozDev/book-translator)

## How this informs the Tier 2 plan

When Tier 2 plan is written, reference this survey for:

- **Pre-pass character/world-glossary** → adopt darkautism's Pass 1 / Pass 2 split + qw02's cheap-extraction-model
- **5D literary reflect** → adopt TransAgents' prep-phase concept (separate axes) but stay single-agent
- **New verification gate** → adopt GalTransl's deterministic `problemAnalyze` as pre-S1 cheap rule-based check
- **Voice-consistency gate (Tier 3)** → confirmed novel direction; no prior-art baseline to compare against
