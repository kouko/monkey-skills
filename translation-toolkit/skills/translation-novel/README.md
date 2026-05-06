# translation-novel

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Translate novel chapters / long-form fiction.
> Scene-aware chunking + scene-window prompts (~17× cost reduction vs whole-doc windowing).

Part of the [translation-toolkit](../..) plugin. Operational spec
Claude loads is [`SKILL.md`](SKILL.md); this README is for humans.

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
| **M2** | HARD | Project glossary compliance — every L1-mandated source term renders as its mapped target form. **Critical for novel mode** because character + place names recur across scenes; per-scene M2 PASS does not guarantee chapter-level consistency (checklist item 5 catches this). |
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
  [`references/core-loop.md`](references/core-loop.md) (scene-window builder)
- [`references/4d-reflection.md`](references/4d-reflection.md) (Accuracy / Fluency / Style / Terminology)
- Typography: [`typography/jlreq-summary.md`](typography/jlreq-summary.md) (ja-JP) ·
  [`typography/clreq-summary.md`](typography/clreq-summary.md) (zh-CN / zh-TW)
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake) ·
  Sibling: [`../translation-doc`](../translation-doc)
