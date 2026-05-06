---
name: translation-novel
description: Translate novel chapters / long-form fiction with scene-aware chunking + scene-window context. Replaces v0.1.0 whole-doc TRANSLATE_THIS windowing for ~17x cost reduction. M1+M2 strict, S1+S2 SHOULD, I1 INFO.
version: 0.2.0
---

# translation-novel

Layer 2-5 owner for **novel chapters / long-form fiction** in `translation-toolkit`. Reads an `intake-spec` from `translation-intake` (Layer 1), splits the chapter into **scenes** via `scripts/lib/scene_chunker.py`, runs the shared DRAFT / REFLECT / IMPROVE core loop with a **scene-window prompt** (prev_scene_v2 + current scene + next_scene_source) instead of the whole-doc `<TRANSLATE_THIS>` windowing used by `translation-doc`, and concatenates the per-scene v2s back into the chapter target.

The scene-window prompt collapses cost from O(N²) to O(N) over a chapter (~17× reduction for a 30-scene chapter) while voice continuity is anchored to the **target translation** of the previous scene rather than its source. (Decision 1 of the v0.2.0 plan: this is a new skill, not a flag on `translation-doc` — chunking, prompts, and gate weights diverge enough to warrant separation.)

## Inputs

- **chapter** — single Markdown file (`.md`) per chapter. Recommended preprocessor: `tsundoku:book-extract`, which produces NCX-driven chapter `.md` files from an EPUB.
- **intake-spec** — from `translation-intake`. If invoked directly without one, run intake first (`--intake` flag) before continuing. Novel-relevant intake hints include `register` (literary / colloquial / mixed), `mode` (faithful / transcreation), and whether to run a protect-pass at all (default off for prose-only novels — see Layer 2).
- **project_glossary_path** *(strongly recommended)* — repo-local glossary listing **character names**, **place names**, and **recurring terms** in the canonical target form. Defaults to `<caller_repo>/docs/i18n/glossary-{target_locale}.md`; missing → fall through to L2 bundled glossary in `glossary/`. M2 enforces compliance per term; without a project glossary character names drift across scenes.

Service-interface contract (the four shared fields plus `web_search`) is defined in the design spec §Service Interface; no per-skill duplication here.

## When to use

- Routed in by `using-translation-toolkit` when the user supplies a novel chapter `.md` file or pastes long-form fiction prose.
- Invoked directly by name when the user already knows novel-mode is the right specialist (e.g. distilling a Kobo EPUB into chapter `.md` files via `tsundoku:book-extract` and translating chapter-by-chapter).

## When NOT to use

- **Technical documentation** — code blocks / diagrams / TOC-anchor concerns dominate; route to `translation-doc`.
- **Ad copy / catchphrases / product copy** — voice / brand constraints + transcreation variants dominate; route to `translation-creative`.
- **i18n format files** — placeholder integrity dominates short UI strings; route to `translation-i18n`.
- **Reviewing an existing translation pair** — diff-protect mode, no new translation; route to `translation-audit`.

## Web search policy

ON by default per `using-translation-toolkit` §"Web search trade-off note" (spec Decision #15). For novel batches (translating 30-scene chapters in bulk) override to OFF:

```
--web-search=off
```

When OFF, glossary resolution stops at L2 (bundled) — L3 (web) is skipped, L4 (LLM-fallback) still runs. Spot-check a sample chapter with web search re-enabled before shipping a full untriaged batch; recurring fictional terms (invented place names, magic-system vocabulary) often have no web hits anyway, so OFF is usually the correct default for fiction.

## Pipeline

This skill executes **Layers 2-5** of the toolkit's 5-layer pipeline. (Layer 1 — intake — is the upstream `translation-intake` skill.)

### Layer 2: Preparation

1. **Parse chapter.** Read the chapter `.md` file as plain text. Novels are prose-dominant; the markdown AST work `translation-doc` does (code blocks, math, mermaid, frontmatter) does not apply. The chapter is treated as a single text payload.

2. **Optional protect-pass.** Default OFF for prose-only novels — there are typically no `⟦P:NN⟧`-class spans (no fenced code, no URLs, no HTML, no math) in fiction prose. If the intake-spec sets `protect_pass: on` (rare — e.g. a non-fiction memoir with embedded code listings), the same protect-pass-spec base classes from `references/protect-pass-spec.md` apply. M1 enforces token parity only when protect-pass ran.

3. **Scene chunk.** Call `scripts/lib/scene_chunker.chunk_chapter_into_scenes(chapter_text, max_scene_tokens=2000)`. The chunker walks the chapter once and emits a `list[Scene]` using **four boundary classes** in priority order: `heading > explicit_marker > blank_gap > fallback_token_fill`. The round-trip contract is: heading lines are kept with their scene; explicit-marker lines and blank-gap whitespace are consumed by the chunker (NOT part of any scene's `source_text`); concatenating all `source_text` plus the consumed boundary strings exactly reproduces the input. See `protocols/scene-chunking.md` for the full algorithm + boundary examples + token heuristic.

4. **Glossary resolve (per-scene, scene-window scope).** Decision 6: for each scene, scan the **current scene + previous scene source + next scene source** for known terms via `lib.glossary.lookup()`. Inject **only matched terms** into the WRITER / CRITIC / REVISER prompts — no full-glossary dump. 4-tier fallthrough is unchanged from `translation-doc` (per `references/orthogonal-axes.md` and `docs/glossary-format-spec.md`):
   1. **L1 project** — `<repo>/docs/i18n/glossary-{target_locale}.md` (highest priority — character / place names live here).
   2. **L2 bundled** — `glossary/glossary-{source}--{target}.md`.
   3. **L3 web search** — only if web search is ON.
   4. **L4 LLM fallback** — flagged in audit-trail with tier `L4`.

### Layer 3: Core loop (per scene)

Three roles, one LLM call each per scene, per `references/core-loop.md`. The prompts are **scene-window** instead of whole-doc — see `protocols/scene-window-context.md` for the 6-section layout.

- **DRAFT** (WRITER) — `references/prompt-draft.md` rendered through `scripts/lib/novel_prompts.build_scene_draft_prompt()`. Layout (Decision 4): translation parameters → glossary terms → previous scene (last ~500 tokens of `prev_scene_v2`) → CURRENT SCENE wrapped in `<TRANSLATE_THIS>` → next scene opening (first ~200 tokens of `next_scene_source`) → output requirements.
- **REFLECT 4D** (CRITIC) — `references/prompt-reflect-4d.md` rendered through `build_scene_reflect_prompt()`. 4 axes (Accuracy / Fluency / Style / Terminology) per Decision 7. 5D effectiveness is `translation-creative`'s axis in transcreation mode; novel-mode stays 4D in v0.2.0 (5D-for-fiction effectiveness is deferred to Tier 2).
- **IMPROVE** (REVISER) — `references/prompt-improve.md` rendered through `build_scene_improve_prompt()`. Consumes critique JSON, outputs v2.

**Cross-scene voice continuity.** Decision 5: `prev_scene_v2` is the **target-language** translation of the previous scene, not its source. Tying scene N to N-1's *target* keeps voice / register / chosen-translation choices consistent (e.g. the same character's name + same speech-tier across scenes) without re-translating context for every scene. The first scene receives `prev_scene_v2 = None`; subsequent scenes get the trailing ~500 tokens of the just-emitted v2.

WRITER and REVISER outputs MUST preserve every `⟦P:NN⟧` token exactly (when protect-pass ran). CRITIC produces structured JSON critique only — never a rewrite.

### Layer 4: Verification

Per `references/verification-gates.md` §"Per-skill gate application" + Decision 8 of the v0.2.0 plan:

| Gate | Tier | Action |
|---|---|---|
| **M1** | HARD | Placeholder integrity. No-op in practice for prose-only novels (protect-pass off → no tokens to count); when protect-pass is on, deterministic count + ID set parity. |
| **M2** | HARD | Project glossary compliance — every L1-mandated source term renders as its mapped target form. **Critical for novel mode** because character + place names recur across scenes; per-scene M2 PASS does not guarantee chapter-level consistency (see checklist item 5). |
| **S1** | SHOULD (faithful) / MUST (transcreation) | Back-translation. Per scene, BACK-TRANSLATOR dispatches a blind v2 → source retranslation; embedding-cosine similarity vs original source. Reliable for scene-length prose (typically 500-2000 tokens). Skips with audit-trail flag `S1: SKIPPED (no isolation capability)` when no subagent / task isolation is available. |
| **S2** | SHOULD | Register preservation. JUDGE classifies source vs target on a discourse / formality axis. Reliable for prose scenes; fiction register is high signal. |
| **I1** | INFO | Untranslatability flagging — cultural references, wordplay, idioms, untranslatable honorifics. Non-interactive: records borrow / explain / approximate decisions in the audit-trail; never blocks, never prompts the user. |

S1 / S2 are **SHOULD**, not HARD: a single-scene failure with a clear cause (e.g. dialect register the JUDGE misclassifies) records to the audit-trail and surfaces to the caller, but does not block emit. M1 / M2 still HARD-block.

### Layer 5: Output

1. **Restore placeholder tokens** (only if protect-pass ran). Replace every `⟦P:NN⟧` in each translated scene with the original substring from the protect-pass token map.
2. **Concatenate scene v2s.** Stitch translated scenes back into a single chapter document **in original index order**. The scene chunker's round-trip contract guarantees that source `Scene[i].source_text` concatenated with the consumed boundary strings reproduces the source chapter; the reassembler must emit the same boundary strings between target scenes (heading lines stayed inside their scene, so they round-trip naturally; explicit-marker lines + blank-gap whitespace need to be re-emitted).
3. **Roundtrip check.** Per `checklists/novel-quality-checklist.md`: scene order preserved, scene boundary text faithfully consumed, heading levels match, paragraph breaks within scenes preserved, glossary compliance at chapter level (M2 cross-scene check), no truncation-window leakage.
4. **Emit audit-trail JSON.** Schema per `references/audit-trail-spec.md`. Every scene's `(source, draft, reflect, improve)` quadruple, every gate verdict, every glossary resolution with tier + audit_path, every untranslatability decision.

## Cross-scene consistency

Distinguishing trait of `translation-novel` vs `translation-doc`:

- `translation-doc` uses **whole-doc `<TRANSLATE_THIS>` windowing** — the entire document is re-emitted on every chunk's prompt, with only the active chunk wrapped. Cost is O(N²) in chunk count.
- `translation-novel` uses **scene-window prompts** — only `prev_scene_v2` (last ~500 tokens) + current scene + `next_scene_source` (first ~200 tokens) appear in each prompt. Cost is O(N) per scene, ~17× reduction over a 30-scene chapter.

Voice continuity comes from `prev_scene_v2` (target side, not source) so the WRITER sees how the *previous translation* handled a recurring character's voice — not the source text it would have to re-translate. Glossary terms keep cross-scene consistency through M2 (HARD) at chapter level, double-checked by checklist item 5.

## Roles

Same vocabulary as the rest of the toolkit (per `using-translation-toolkit` §Roles vocabulary):

- **WRITER** — produces the per-scene draft, preserves `⟦P:NN⟧` tokens.
- **CRITIC** — 4D structured JSON critique per scene; no rewrites.
- **REVISER** — consumes critique, outputs v2 per scene; preserves placeholders.
- **BACK-TRANSLATOR** — blind v2 → source retranslation, used by S1.
- **JUDGE** — register classification, used by S2.

Roles are behavioral. Any LLM model can fill any role; this skill specifies behavior, not models.

## What this skill does NOT do

- **Does not run intake.** If invoked without an intake-spec, hand off to `translation-intake` first (or use `--intake` to run it inline).
- **Does not parse markdown AST.** Novel chapters are treated as prose text; protect-pass is off by default. If the source has embedded code / math / diagrams, route to `translation-doc` instead.
- **Does not rewrite chapter structure.** Scene order is preserved; the chunker's round-trip contract is the spec, not a suggestion.
- **Does not generate transcreation variants.** Route to `translation-creative` with `--variants=N`. Novel-mode runs a single faithful translation per scene.
- **Does not audit existing translations.** Route to `translation-audit`.
- **Does not bypass M1 / M2.** No `--bypass-gates` flag exists (anti-pattern per spec Decision #15). Fix the underlying issue (e.g. add the missing character name to the project glossary) and re-run.
- **Does not do whole-novel context assembly.** Voice continuity is scene-window only; for character-arc-aware translation across an entire novel, see Tier 2 (character pre-pass) which is deferred from v0.2.0.
- **Does not prompt the user during I1.** Untranslatability decisions are recorded, not asked.

## See also

- `protocols/scene-chunking.md` — scene boundary detection algorithm + 4 boundary classes + round-trip contract
- `protocols/scene-window-context.md` — 6-section scene-window prompt layout + prev/next truncation rules + glossary scope
- `checklists/novel-quality-checklist.md` — 6-item roundtrip check before emit
- `references/protect-pass-spec.md` — canonical protect-pass algorithm and `⟦P:NN⟧` token format (used only when intake enables protect-pass)
- `references/core-loop.md` — DRAFT / REFLECT / IMPROVE role contracts (scene-window builder is the novel-mode rendering)
- `references/4d-reflection.md` — critique axes for novel-mode (Accuracy / Fluency / Style / Terminology)
- `references/verification-gates.md` — gate semantics + audit-trail entry shapes
- `references/audit-trail-spec.md` — full audit-trail JSON schema
- `references/orthogonal-axes.md` — 5 intake axes + 4-tier glossary resolver definition
- `glossary/glossary-{source}--{target}.md` — bundled L2 glossary (5 pair files)
- `typography/jlreq-summary.md` — JLReq typography rules for `target_locale=ja-JP`
- `typography/clreq-summary.md` — CLReq typography rules for `target_locale=zh-CN` / `zh-TW`
- `../using-translation-toolkit/SKILL.md` — router (when to land here)
- `../translation-intake/SKILL.md` — Layer 1 owner
- `../translation-doc/SKILL.md` — sibling skill for technical documentation
- `../../scripts/lib/scene_chunker.py` — scene chunker implementation (Phase A)
- `../../scripts/lib/novel_prompts.py` — scene-window prompt builders (Phase B)
- `../../../docs/superpowers/plans/2026-05-06-translation-toolkit-v0.2.0-novel-mode.md` — v0.2.0 plan with Decisions 1-8
