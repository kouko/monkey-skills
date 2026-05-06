# Scene-window context — per-scene prompt structure

> **Implementation source-of-truth**: `scripts/lib/novel_prompts.py`
> (`build_scene_draft_prompt`, `build_scene_reflect_prompt`,
> `build_scene_improve_prompt`). This protocol documents the
> **6-section layout** (Decision 4 of the v0.2.0 plan), the prev / next
> truncation rules (Decision 5), the glossary scope (Decision 6), and how
> the 4D reflect prompt (Decision 7) ties back to the canonical prompts
> under `references/`.

## Why scene-window vs whole-doc TRANSLATE_THIS

`translation-doc` re-emits the entire document on every chunk's prompt,
with only the active chunk wrapped in `<TRANSLATE_THIS>...</TRANSLATE_THIS>`.
Cost is **O(N²)** in chunk count: a 30-chunk document re-sends 30× the
shared context. For technical docs that's tolerable — chunks are
typically 5-10 per document. For novels:

- A 30-scene chapter under whole-doc windowing = 900× the per-scene
  payload across the chapter run.
- Under scene-window (prev ~500 tok + current + next ~200 tok) it's
  **~17× smaller per scene** and the total chapter cost drops from
  O(N²) to **O(N)**.

The trade-off: the WRITER no longer sees the *whole document* on every
scene. We compensate by having `prev_scene_v2` carry the **target-side**
voice continuity (Decision 5) and `next_scene_source` carry **source-side**
narrative-flow context for the next ~200 tokens. Glossary terms keep
cross-scene consistency through M2 (HARD) at chapter level — see
`checklists/novel-quality-checklist.md` item 5.

## DRAFT prompt — 6-section layout (Decision 4)

`build_scene_draft_prompt()` renders these six sections in order, each as
a top-level `#` heading:

### 1. Translation parameters

The intake-spec rendered as a compact key/value block — `source_locale`,
`target_locale`, `mode`, `register`, `domain` first, then any extra
caller-supplied keys for forward-compat. Empty intake renders as `(none)`.

```
# Translation parameters
- source_locale: en-US
- target_locale: ja-JP
- mode: faithful
- register: literary
- domain: novel
```

### 2. Glossary terms

Caller-resolved hits only (Decision 6 — see "Glossary scope" below). Each
hit renders as `- source -> target` or `- source -> target (notes)` if
notes are present. Empty list renders as `(none -- no in-scope glossary
terms)`. Malformed hits (missing source or target term) are silently
dropped.

```
# Glossary terms -- USE THESE, do not invent alternatives (only those that hit in current scene + prev/next windows)
- Tom Sawyer -> トム・ソーヤー
- Mississippi -> ミシシッピ (river name, katakana)
```

### 3. Previous scene (last ~500 tokens)

The trailing ~500 tokens of `prev_scene_v2` (the **target-language**
translation of the previous scene). Truncated via `_truncate_tail` →
slices the last `500 * 3 = 1500` characters. First scene of the chapter
gets `(none -- first scene of chapter)`.

```
# Previous scene (last ~500 tokens) -- for continuity
…前のシーンの末尾、target-language（日本語訳）で〜1500文字…
```

### 4. CURRENT SCENE — wrapped in `<TRANSLATE_THIS>` markers

The full source text of the current scene, untruncated. The marker is
the WRITER's only signal of what to actually translate.

```
# CURRENT SCENE -- translate ALL of this
<TRANSLATE_THIS>
Tom turned the page. The morning light was thin.
…
</TRANSLATE_THIS>
```

### 5. Next scene opening (first ~200 tokens)

The leading ~200 tokens of `next_scene_source` (the **source** text of
the next scene, NOT a translation). Truncated via `_truncate_head` →
slices the first `200 * 3 = 600` characters. Last scene of the chapter
gets `(none -- last scene of chapter)`.

```
# Next scene opening (first ~200 tokens) -- for narrative flow context
…next scene の冒頭、source language（英語）で〜600文字…
```

### 6. Output requirements

A fixed bullet list reminding the WRITER of the scene-window contract:

```
# Output requirements
- Translate ONLY content inside <TRANSLATE_THIS>
- Preserve scene's paragraph breaks exactly
- Preserve all ⟦P:NN⟧ placeholder tokens unchanged
- Do NOT include translation of prev/next windows
- Output ONLY the translation
```

## prev_scene_v2 — target-side voice continuity (Decision 5)

Critical design choice: the previous scene is supplied as its **already-
translated v2**, not its source. Rationale:

- WRITER sees how a recurring character's voice / speech-tier / chosen
  translation was actually rendered, not just what the source said.
- Eliminates the cost of re-translating context every scene (O(N²) → O(N)).
- Self-corrects: if scene N-1's REVISER landed on a particular rendering
  for a character name, scene N's WRITER inherits that choice as a
  precedent.

Trade-off: a v2 error in scene N-1 propagates to scene N. M2 (HARD)
catches glossary-term errors; voice-tier drift is caught by S2 (SHOULD)
and the chapter-level checklist item 5.

The first scene of every chapter has no prior v2 → the prompt renders
`(none -- first scene of chapter)` and the WRITER falls back to the
intake-spec's `register` directive.

## next_scene_source — narrative-flow lookahead

Source-side, not translation. The WRITER does not translate this — it's
context-only for narrative flow (e.g. don't end the current scene's last
paragraph in a way that contradicts the next scene's opening sentence).
First ~200 tokens (~600 characters) is enough to establish the next
scene's tone / setting / POV without bloating the prompt.

The last scene of a chapter has no next → `(none -- last scene of chapter)`.

## Glossary scope per scene (Decision 6)

The caller resolves glossary hits via `lib.glossary.lookup()` over the
**concatenation of**:

```
current scene source + prev scene source + next scene source
```

Only terms whose source forms appear in this 3-window concatenation flow
into `glossary_hits`. The renderer in `_format_glossary_hits` does no
further filtering — it formats whatever the caller passes.

Why scope per-window rather than per-current-scene? A character name
mentioned only in the prev or next scene still needs to be in the WRITER's
prompt for the current scene because:

- The WRITER's `# Previous scene` section may reference the character by
  the rendering used in N-1; the M2 lookup needs to anchor on that name.
- Foreshadowing in the next scene's opening may telegraph a character
  about to enter the current scene's last paragraph; the WRITER should
  pre-stage the canonical translation rather than invent one.

No full-glossary dump (per `references/core-loop.md` §8) — irrelevant
terms are noise that pulls the WRITER's attention away from in-scope
vocabulary.

## REFLECT prompt — 4D axes (Decision 7)

`build_scene_reflect_prompt()` renders the same 4D shape as
`references/prompt-reflect-4d.md` (canonical), tied to a scene-window
source rather than a doc chunk:

1. **Accuracy** — semantic faithfulness. Additions, omissions, distortions?
2. **Fluency** — does target read naturally? Awkward phrasings?
3. **Style** — does register / rhythm / rhetoric match source and intended mode/register?
4. **Terminology** — does it match the glossary? Domain conventions?

Output is structured JSON; CRITIC never rewrites the translation, only
critiques. 5D effectiveness is `translation-creative`'s axis in
transcreation mode; novel-mode stays 4D in v0.2.0 (5D-for-fiction
effectiveness deferred to Tier 2).

## IMPROVE prompt — apply critique → v2

`build_scene_improve_prompt()` renders the same shape as
`references/prompt-improve.md` (canonical) with the source scene + draft
v1 + critique JSON. REVISER applies the critique and outputs v2 only —
no new reasoning beyond what the critique says, and `⟦P:NN⟧` tokens
preserved when present.

## What is NOT covered here

- **Scene boundary detection** — see `protocols/scene-chunking.md`.
- **Verification gates** — see `references/verification-gates.md` and the
  Layer 4 table in `SKILL.md`.
- **Whole-novel context** — character-arc-aware translation across an
  entire novel is deferred to Tier 2 (character pre-pass).

## See also

- `scripts/lib/novel_prompts.py` — implementation source-of-truth
- `scripts/lib/scene_chunker.py` — produces the `Scene` objects this protocol consumes
- `references/prompt-draft.md` — canonical DRAFT prompt template
- `references/prompt-reflect-4d.md` — canonical 4D REFLECT prompt template
- `references/prompt-improve.md` — canonical IMPROVE prompt template
- `references/core-loop.md` — DRAFT / REFLECT / IMPROVE role contracts
- `references/4d-reflection.md` — 4D axis definitions
