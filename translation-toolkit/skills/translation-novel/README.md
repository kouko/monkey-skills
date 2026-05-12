# translation-novel

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Translate novel chapters / long-form fiction.
> Scene-aware chunking + scene-window prompts (~17× cost reduction vs whole-doc windowing).
> v0.3.0 adds whole-book pre-pass, 5D literary critic, and M3 deterministic linter.

Part of the [translation-toolkit](../..) plugin. Operational spec
Claude loads is [`SKILL.md`](SKILL.md); this README is for humans.

## What's new in v0.3.0

Four Tier 2 features layer on top of the v0.2.0 scene-window foundation:

- **Whole-book pre-pass** — before per-chapter translation, the skill walks
  every chapter once with two extractors:
  - `character_extractor` — surfaces every named character + paired-structure
    aliases + voice notes + first/last chapter index → `characters.json`.
  - `world_glossary_extractor` — surfaces places / organizations / world
    terms / cultural references → `world-glossary.json`. Cultural references
    carry a closed-enum `category` (literary_quotation / idiom / religious /
    food / place_culture / historical / other) and a `handling_hint`
    (borrow / explain / approximate).
  Both artifacts feed the per-scene glossary lookup as a new **L1.5** tier
  (between project glossary L1 and bundled glossary L2), giving every scene
  consistent character renderings and world-term anchoring without
  whole-novel context bloat.
- **5D literary critic** — the per-scene REFLECT step (default for novel
  mode) gains a Literariness axis on top of the v0.2.0 4D (Accuracy /
  Fluency / Style / Terminology). Sub-concerns: rhythm (sentence cadence),
  euphony (sound pattern), archaism (period vocabulary / honorific), and
  register-shift fidelity (narrator vs dialogue, formal vs casual within
  the same character). Distinct from `translation-creative`'s 5D, which
  uses Effectiveness as the fifth axis.
- **M3 deterministic linter** — a no-LLM structural sanity check that
  runs *before* S1 back-translation: M3a (residual source-script chars,
  HARD), M3b (length-ratio band, SHOULD), M3c (CJK fullwidth punctuation,
  SHOULD). Adopted by `translation-doc` in v0.3.0 alongside novel mode
  (Decision H — both novel + doc surface M3 in their Layer 4 audit-trail).
- **Cheap-model split** — the intake-spec `model` field accepts a dict
  form `{default: ..., extractor: ..., back_translator: ...}`. The
  whole-book pre-pass routes to the `extractor` model when set, so the
  fixed-cost pre-pass amortizes against the per-scene translation cost.
  See "Setting up a book for translation" below for the recommended split.

## Setting up a book for translation

Recommended workflow when translating a multi-chapter book:

1. **Extract chapters to Markdown.** Use
   [`tsundoku:book-extract`](../../../tsundoku/skills/book-extract) to
   convert an EPUB into chapter-split `.md` files. Place them in a
   directory `book-ja/` with names that sort lexicographically in reading
   order (`chapter-01.md`, `chapter-02.md`, ...).
2. **Run the whole-book pre-pass once.** Before translating any chapter,
   point the skill at `book-ja/` to produce `characters.json` and
   `world-glossary.json`. The pre-pass is the only place where each
   chapter is read in full — translation thereafter operates per scene.
3. **Translate chapter-by-chapter.** Each chapter run loads the two
   pre-pass artifacts and consults them at L1.5 in the glossary lookup
   chain, before falling through to L2 / L3 / L4. Cross-scene voice
   continuity is still anchored on `prev_scene_v2`; pre-pass adds
   *cross-chapter* canonical-rendering anchoring.
4. **Re-run the pre-pass on book changes.** Each artifact is stamped
   with a `book_manifest_hash` covering filenames + per-file SHA-256.
   When the manifest hash drifts (chapter added / edited / reordered),
   the next pre-pass run emits a `UserWarning` and overwrites the
   artifact. The skill never silently uses a stale artifact.

### Cost note

The pre-pass uses the cheap **extractor** model by default once the
`model: dict` form is supplied — pre-pass total cost scales with raw
chapter text only, not per-scene prompt overhead, and amortizes across
the entire book (you pay once, every chapter benefits). For a typical
20-30 chapter novel the pre-pass cost is well under 10% of one
chapter's translation cost; for very small books (≤2 chapters) the
ratio is higher and the cheap-model split is the load-bearing design
choice. The smoke fixture (`scripts/tests/fixtures/sample-book-ja/`)
ships a 2-chapter case so the cost ceiling can be exercised in CI; see
`test_prepass_cost_ceiling_assertion` in
`scripts/tests/test_e2e_v030_tier2_smoke.py` for the calibrated
worst-case bound.

Example dict-form `model` field (intake spec):

```yaml
model:
  default: claude-opus-4-7
  extractor: claude-haiku-4-5         # whole-book pre-pass
  back_translator: claude-haiku-4-5   # S1 round-trip
```

## Why a dedicated novel skill

Novels are prose-dominant. The markdown-AST work `translation-doc` does
(code blocks, math, mermaid, frontmatter) does not apply, and the
whole-doc `<TRANSLATE_THIS>` windowing it relies on costs O(N²) in chunk
count. A 30-scene chapter under whole-doc windowing re-sends 900× the
shared context — tolerable for a 5-10 chunk technical document, ruinous
for fiction batches.

Novel-mode also needs **cross-scene voice continuity** that doc-mode
doesn't: the same character's name, the same speech-tier, the same
register from scene to scene. Doc-mode's whole-doc context happens to
preserve this; once you drop to a scene window for cost reasons, voice
continuity must be carried explicitly.

`translation-novel` solves both at once: scene-aware chunking via
heading / explicit-marker / blank-gap / token-fill boundaries, then
scene-window prompts that carry the **target-language** translation of
the previous scene (`prev_scene_v2`) plus the source opening of the
next scene (`next_scene_source`). Cost collapses to O(N), voice stays
anchored to its target-side history.

(Decision 1 of the v0.2.0 plan: this is a new skill, not a flag on
`translation-doc` — chunking, prompts, and gate weights diverge enough
to warrant separation.)

## Pipeline

```
intake-spec (from translation-intake)
        │
Layer 2 — Preparation
        ├── parse chapter as plain prose (no markdown AST work)
        ├── optional protect-pass (default OFF — no code/math/diagrams
        │   in fiction; M1 enforces only when ON)
        ├── scene chunk: heading > explicit_marker > blank_gap >
        │   fallback_token_fill, max_scene_tokens=2000
        └── per-scene glossary resolve (4-tier: L1 project → L2 bundled
            → L3 web → L4 LLM); scope = current + prev_source + next_source
        │
Layer 3 — Per-scene core loop (DRAFT → REFLECT 4D → IMPROVE)
        │   └── scene-window prompt (Decision 4):
        │       params → glossary → prev_scene_v2 (~500 tok) →
        │       <TRANSLATE_THIS>current</TRANSLATE_THIS> →
        │       next_scene_source (~200 tok) → output requirements
        │
Layer 4 — Verification (M1 + M2 HARD; S1 + S2 SHOULD; I1 INFO)
        │
Layer 5 — Output
        ├── restore ⟦P:NN⟧ → original spans (only if protect-pass ran)
        ├── concatenate scene v2s in original index order, re-emit
        │   consumed boundary strings (explicit-marker / blank-gap)
        ├── roundtrip check (scene order, headings, paragraph breaks,
        │   chapter-level glossary, no truncation-window leakage)
        └── emit audit-trail.json
```

## Scene-window vs whole-doc — the cost story

`translation-doc` uses **whole-doc `<TRANSLATE_THIS>` windowing**: every
chunk's prompt re-emits the entire document, with only the active chunk
wrapped. Cost is **O(N²)** in chunk count.

`translation-novel` uses **scene-window prompts**: only `prev_scene_v2`
(last ~500 tokens) + the current scene + `next_scene_source` (first ~200
tokens) appear. Cost is **O(N)** per scene — for a 30-scene chapter that
is roughly **17× smaller** than whole-doc windowing.

Voice continuity comes from `prev_scene_v2` (the **target-side**
translation of the prior scene, per Decision 5) — not from re-translating
the source on every prompt. The WRITER sees how the previous translation
already handled a recurring character's voice; it does not pay to
rediscover that choice scene by scene. Glossary terms keep chapter-level
consistency through M2 (HARD), double-checked by checklist item 5.

Below the 2000-token chunk threshold, the chapter is a single scene and
the windowing degenerates to a normal prompt with empty prev / next.

## Verification gate matrix

Calibrated for scene-length prose (typically 500-2000 tokens):

| Gate | Tier | What it checks |
|---|---|---|
| **M1** | HARD | Placeholder integrity — `⟦P:NN⟧` count + ID set parity. No-op when protect-pass is off (the default for prose-only novels). |
| **M2** | HARD | Project glossary compliance — every L1-mandated source term renders as its mapped target form. **Critical for novel mode** because character + place names recur across scenes; per-scene M2 PASS does not guarantee chapter-level consistency (checklist item 5 catches this). v0.3.0+ resolves at **L1.5** first against `characters.json` / `world-glossary.json` from the pre-pass, before falling through to project glossary L1 and bundled glossary L2. |
| **M3** | HARD (m3a) / SHOULD (m3b, m3c) | Deterministic post-translation linter — three subrules: m3a residual source-script chars (HARD; e.g. JP→EN target should not contain hiragana / katakana / CJK ideographs above the 1% locale-pair threshold), m3b length-ratio band (target/source token ratio inside locale-pair-tuned band), m3c CJK fullwidth punctuation (per JLReq / CLReq). Runs *before* S1 — short-circuits S1 when the target is structurally broken so we don't pay for a meaningless back-translation. v0.3.0+; adopted by `translation-doc` in the same release. |
| **S1** | SHOULD (faithful) / MUST (transcreation) | Back-translation — BACK-TRANSLATOR produces a blind v2 → source retranslation per scene; embedding-cosine similarity vs the original source. Reliable for scene-length prose. Skips with audit-trail flag if runtime provides no isolation. |
| **S2** | SHOULD | Register preservation — JUDGE classifies source vs target on a discourse / formality axis. Fiction register is high-signal at scene length. |
| **I1** | INFO | Untranslatability flagging — cultural references, wordplay, idioms, untranslatable honorifics. Records borrow / explain / approximate decisions; never blocks, never prompts the user. |

S1 / S2 are SHOULD, not HARD: a single-scene failure with a clear cause
(e.g. a dialect register the JUDGE misclassifies) records to the
audit-trail and surfaces to the caller, but does not block emit.
M1 / M2 still HARD-block.

## Roundtrip checklist

Before emit, [`checklists/novel-quality-checklist.md`](checklists/novel-quality-checklist.md)
verifies:

1. Scene order preserved
2. Scene boundary text faithfully consumed (explicit-marker + blank-gap re-emitted)
3. Heading levels match
4. Paragraph breaks within scenes preserved
5. Chapter-level M2 cross-scene glossary consistency
6. No truncation-window leakage (prev / next slices not bleeding into v2)

Failure on any item halts emit and surfaces to the caller.

## Web search policy

ON by default. Override to OFF for novel batches (e.g. translating a
30-scene chapter in bulk):

```
--web-search=off
```

When OFF, glossary resolution stops at L2 (bundled) — L3 (web) is
skipped, L4 (LLM-fallback) still runs. Recurring fictional terms
(invented place names, magic-system vocabulary) often have no web hits
anyway, so OFF is usually the correct default for fiction.

## What this skill does NOT do

- **Does not run intake.** Hand off to [`translation-intake`](../translation-intake)
  (or use `--intake`)
- **Does not parse markdown AST.** Novel chapters are treated as prose
  text; protect-pass is off by default. If the source has embedded code
  / math / diagrams, route to [`translation-doc`](../translation-doc) instead.
- **Does not rewrite chapter structure.** Scene order is preserved; the
  chunker's round-trip contract is the spec, not a suggestion.
- **Does not generate transcreation variants.** Route to
  [`translation-creative`](../translation-creative) with `--variants=N`.
  Novel-mode runs a single faithful translation per scene.
- **Does not audit existing translation pairs.** Route to
  [`translation-audit`](../translation-audit).
- **Does not bypass M1 / M2.** No `--bypass-gates` flag (anti-pattern per
  spec Decision #15).
- **Does not do whole-novel context assembly.** Voice continuity is
  scene-window only; character-arc-aware translation across an entire
  novel is deferred Tier 2 work (character pre-pass).
- **Does not prompt the user during I1.** Untranslatability decisions
  are recorded, not asked.

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/scene-chunking.md`](protocols/scene-chunking.md) ·
  [`protocols/scene-window-context.md`](protocols/scene-window-context.md)
- [`checklists/novel-quality-checklist.md`](checklists/novel-quality-checklist.md)
- [`references/verification-gates.md`](references/verification-gates.md) ·
  [`references/core-loop.md`](references/core-loop.md) (DRAFT / REFLECT / IMPROVE role contracts)
- [`references/4d-reflection.md`](references/4d-reflection.md) (Accuracy / Fluency / Style / Terminology) ·
  [`references/prompt-reflect-5d-literary.md`](references/prompt-reflect-5d-literary.md) (5D literary critic — v0.3.0 default)
- [`references/prompt-extract-characters.md`](references/prompt-extract-characters.md) ·
  [`references/prompt-extract-world-glossary.md`](references/prompt-extract-world-glossary.md) (whole-book pre-pass extractors — v0.3.0)
- Typography: [`typography/jlreq-summary.md`](typography/jlreq-summary.md) (ja-JP) ·
  [`typography/clreq-summary.md`](typography/clreq-summary.md) (zh-CN / zh-TW)
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake) ·
  Sibling: [`../translation-doc`](../translation-doc)
