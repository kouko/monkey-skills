---
name: using-translation-toolkit
description: Router skill for translation-toolkit. Routes to one of 5 active translation skills based on user intent and input shape. Use when the user asks for any translation between en-US / ja-JP / zh-TW / zh-CN. 翻訳・翻譯・トランスレーション・本地化・i18n・transcreation。
version: 0.3.0
---

# using-translation-toolkit

Entry router for the `translation-toolkit` plugin. Inspect the user's request — intent + the shape of the input they handed in — and route to one of the 5 active specialist skills (`translation-i18n`, `translation-doc`, `translation-creative`, `translation-novel`, `translation-audit`), preceded by `translation-intake` if the brief is ambiguous. **This router does not translate, audit, or rewrite anything itself — it only decides which downstream skill should run.**

## When to use

- User asks for a translation between en-US / ja-JP / zh-TW / zh-CN and has not named a specific specialist skill.
- User provides translatable content (i18n file / markdown doc / ad copy / existing translation pair) but no explicit pipeline.
- Triggers (any locale): "translate / 翻訳して / 翻譯一下 / 翻译", "i18n / localize / 本地化 / ローカライズ", "audit translation / 翻訳レビュー / 翻譯審核", "transcreation / トランスクリエーション".

## When NOT to use

- User explicitly names a downstream skill ("run `translation-i18n` on this PO file") — call it directly.
- Task is outside translation scope: copywriting → `copywriting-toolkit`, original-language drafting → `domain-teams:copywriting-team`, technical-doc authoring (not translating) → `domain-teams:docs-team`.
- Locale pair is outside the v0.1.0 supported set (en-US ↔ ja-JP ↔ zh-TW ↔ zh-CN). For other languages, tell the user the toolkit cannot guarantee glossary coverage and ask if they want to proceed with degraded quality.

## Routing rules

Pick exactly one downstream specialist. If multiple signals fire, the **input-shape rule wins** over the **intent rule** (an explicit PO file always routes to i18n even if the user says "creative").

When a `.md` payload is **explicitly a novel chapter** (long-form fiction, scene markers, dialogue heavy), prefer `translation-novel` over `translation-doc`. Heuristic: if input has scene-break markers (`* * *`, `***`, `―――`, `◇◇◇`) or chapter markup typical of novels, route to novel. Otherwise stay with `translation-doc`.

**v0.3.0 routing tip — novel pre-pass.** When the user is translating a multi-chapter novel (a directory of chapter `.md` files from `tsundoku:book-extract` or similar), `translation-novel` runs a **whole-book pre-pass** (Layer 1.5) before per-chapter translation. The pre-pass produces `<repo>/.translations/characters.json` + `<repo>/.translations/world-glossary.json` and amortizes across all chapters. Suggest passing `book_manifest` (a chapter directory or ordered path list) on the first invocation; subsequent per-chapter runs reuse the artifacts. For a one-shot single-chapter run the pre-pass still works but the cost-amortization argument shrinks.

| Signal | Route to | Why |
|---|---|---|
| User provides existing translation + asks to review / audit / 改善提案 / 找問題 | `translation-audit` | Audit-only mode; no rewrite. Runs full M1+M2+S1+S2+I1 verification. |
| User provides PO / JSON / XLIFF / Android `strings.xml` / iOS `.strings` file | `translation-i18n` | Strict placeholder + key preservation; project glossary compliance. |
| User provides Markdown / `.md` / technical doc / API reference / runbook | `translation-doc` | AST-aware protection of code blocks, URLs, HTML tags, frontmatter. |
| User provides novel chapter / long-form fiction `.md` (chapter exports from `tsundoku:book-extract` or similar) | `translation-novel` | Scene-aware chunking + scene-window prompts (~17× cost reduction vs `translation-doc` on long files); 4D reflect; voice continuity via prev_scene_v2 (last 500 tokens, target side). |
| User provides ad copy / marketing brief / headline / tagline / catchphrase / キャッチコピー | `translation-creative` | Transcreation mode + 5D reflection (adds Effectiveness axis). |
| Ambiguous (or short raw text with no format / domain hint) | `translation-intake` first | Intake clarifies the 5 axes (mode / register / strategy / locale / domain) + skopos, then re-routes per its output. |

### What each downstream skill expects as input

- `translation-intake` — raw text or an under-specified brief. Outputs an `intake-spec.json` consumed by the next skill.
- `translation-i18n` — path to a PO / JSON / XLIFF / Android / iOS file (or inline strings keyed by ID). Reads intake-spec if present.
- `translation-doc` — path to a `.md` / technical doc, optionally with frontmatter and code fences. Reads intake-spec if present.
- `translation-creative` — short text + brand brief (voice / tone / forbidden phrases / target persona). Optionally `--variants=N` for alternative outputs. Reads intake-spec if present.
- `translation-novel` — path to a single chapter `.md` file (one chapter per invocation). Optional `project_glossary_path` recommended for character + place names. Reads intake-spec if present.
- `translation-audit` — `(source, existing-target)` pair. Optionally a project glossary path. Outputs a diff report + improvement suggestions, **never a rewritten target**.

### Disambiguation examples

- *"Translate this README to Japanese"* + attaches `.md` → `translation-doc`.
- *"翻訳して"* + pastes a 3-line catchphrase + brand voice description → `translation-creative`.
- *"Translate this novel chapter to English"* + attaches `.md` with scene markers (`* * *` / `―――`) → `translation-novel`.
- *"Help me with the Chinese translation"* + no file, no domain → `translation-intake` first.
- *"Look at this `ja.po` and tell me what's wrong"* → `translation-audit` (review intent dominates over the i18n format).
- *"Translate this `ja.po`"* (no review intent) → `translation-i18n`.

## Web search trade-off note

Web search is **ON by default** across all 5 active translation skills (per spec Decision #7) for max quality — terminology lookup, parallel-corpus reference, brand-voice anchoring. Two cases warrant overriding to OFF via `--web-search=off`:

1. **Batch i18n runs (1000s of strings)** — per-miss searches multiply cost and latency dramatically. For mass i18n updates, pass `--web-search=off` and rely on the bundled glossary + project glossary; spot-check a sample with web search on a second pass.
2. **Ad copy / creative work with established brand voice** — web search may surface competitor copy that contaminates the assistant's voice register. If the brand voice is locked (e.g. via brand book or `voice_anchor` in intake-spec), `--web-search=off` keeps the output uncontaminated.

(This single paragraph absorbs the per-skill `web-search-tradeoffs.md` files that were collapsed during fresh-eyes triage — see spec Decision #15.)

## v0.3.0 verification note — M3 deterministic linter

`translation-doc` and `translation-novel` adopt a third HARD gate, **M3** (deterministic post-translation linter), in v0.3.0. M3 runs between M2 and S1 with three subrules: residual source-language characters (m3a, HARD — partial-translation detector), length-ratio sanity (m3b, SHOULD), and CJK punctuation convention (m3c, SHOULD per JLReq / CLReq). No LLM call; cheap to run. `translation-i18n` and `translation-creative` skip M3 (UI strings are too short / transcreation produces wide length-ratio swings); `translation-audit` does not re-run M3 on a downstream artifact (M3 already executed upstream). See `references/verification-gates.md` §M3 in the doc + novel skills, or the v0.3.0 plan §Decision H.

## Cross-plugin composition

`copywriting-toolkit` will **NOT** auto-invoke `translation-toolkit`, and vice versa. The two represent orthogonal quality dimensions (translation fidelity ≠ copywriting persuasion / form / ethics). If the user wants post-translation copy polish, they must explicitly chain the two:

```
translation-toolkit → produces target-language draft (with gate verdicts)
   ↓ (user explicitly requests)
copywriting-toolkit → applies its own framework / voice / ethics gates
```

Per spec line 516 + Decision #15 — composition is opt-in only; neither plugin silently invokes the other.

Other adjacent plugins:
- `domain-teams:copywriting-team` — original-language copywriting (not translation). Use when the user is writing fresh copy in the target language, not translating from a source.
- `domain-teams:docs-team` — original-language doc authoring + assessment. Use when the user is writing fresh docs, not translating existing ones.

## What this skill does NOT do

- Does **not** translate any content itself. If the user pastes source text directly into a router conversation and expects an answer, advise them which downstream skill to load and let the harness invoke it.
- Does **not** audit translations itself — that is `translation-audit`'s job.
- Does **not** invoke downstream skills via the Skill tool from within this router. The router only **describes** which specialist applies; the runtime / harness performs the actual invocation based on the user's next message.
- Does **not** decide locale pairs or translation strategy (literal vs. transcreation) — that is `translation-intake`'s job.

## Roles vocabulary (shared across the 5 active skills)

For consistency when the user asks "what does each role do":

- **WRITER** — produces the draft, preserves placeholders and protected spans.
- **CRITIC** — structured critique only, no rewrites. 4D / 5D-literary (novel) / 5D-effectiveness (creative) variants depending on skill.
- **REVISER** — consumes the critique, outputs v2.
- **BACK-TRANSLATOR** — blind retranslation v2 → source, used by gate S1.
- **JUDGE** — register / similarity verdicts, used by gates S2 / I1.
- **EXTRACTOR** *(v0.3.0)* — produces character / world-glossary JSON during the `translation-novel` whole-book pre-pass (Layer 1.5); never modifies source or translation. Cheap-model split is the typical use — pin `extractor` to a haiku-class model via the dict-form `model:` parameter.

(Roles are behavioral. Any LLM model can fill any role; the toolkit specifies behavior, not models. See spec § "Roles, not models".)

## Reference

- `../../docs/architecture.md` — high-level plugin topology, 5-layer pipeline, 4-tier glossary fallthrough.
- `../../docs/glossary-format-spec.md` — bundled glossary file format.
- `../../../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md` — full design spec (Sub-skill Responsibility Matrix + Decisions #1-#17).
- Sibling skill SKILL.md files — one per specialist (`../translation-{intake,i18n,doc,creative,novel,audit}/SKILL.md`).
