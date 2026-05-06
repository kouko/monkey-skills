# Core Loop — DRAFT → REFLECT → IMPROVE

**Status**: canonical reference (Single Source of Truth in `scripts/canonical/`; functional copies in each active skill's `references/`)
**Cross-refs**: [`4d-reflection.md`](4d-reflection.md), [`5d-effectiveness.md`](5d-effectiveness.md), [`orthogonal-axes.md`](orthogonal-axes.md), [`verification-gates.md`](verification-gates.md), [`audit-trail-spec.md`](audit-trail-spec.md), [`protect-pass-spec.md`](protect-pass-spec.md)
**Prompt files** (referenced below): [`prompt-draft.md`](prompt-draft.md), [`prompt-reflect-4d.md`](prompt-reflect-4d.md), [`prompt-reflect-5d.md`](prompt-reflect-5d.md), [`prompt-improve.md`](prompt-improve.md)

> The prompt files live at `scripts/canonical/prompts/<name>.md` in the SoT layer and are FLATTENED to `<skill>/references/prompt-<name>.md` by `scripts/distribute.py` (Anthropic flat-folder convention; skill subfolders cannot nest).

---

## 1. Overview

The **3-step `translate → reflect → improve` core** originates with [andrewyng/translation-agent](https://github.com/andrewyng/translation-agent) (TA, 2024). TA's contribution is twofold:

1. The minimal three-role decomposition — a **writer** drafts, a **critic** reflects, a **reviser** improves — gives the LLM stage-specific cognitive scope, which empirically beats single-pass translation on long-form text.
2. The `<TRANSLATE_THIS>...</TRANSLATE_THIS>` cross-chunk windowing pattern — every chunk's prompt re-emits the entire document, with **only the active chunk wrapped** — provides cross-chunk consistency without isolating chunks.

translation-toolkit adopts both contributions verbatim and adds:
- structured 4D / 5D critique JSON (vs TA's free-form critique) — see [`4d-reflection.md`](4d-reflection.md)
- explicit role contracts (input → output specification per role)
- placeholder-token preservation as a hard contract (`⟦P:NN⟧`)
- mode-conditional 5th axis for transcreation (Effectiveness; see [`5d-effectiveness.md`](5d-effectiveness.md))

### Execution context

- The DRAFT, REFLECT, and IMPROVE calls run in the **main agent context** (sequential, three calls per chunk per pass).
- The S1 back-translation gate is dispatched to a **subagent** to keep the back-translation isolated from the main translation context (see [`verification-gates.md`](verification-gates.md) and spec Decision #16).

This document specifies the role contracts. Verification of the loop's output happens in Layer 4 ([`verification-gates.md`](verification-gates.md)).

---

## 2. DRAFT — Writer Role

### Input contract

- **source chunk**: the active chunk to translate (BCP-47 `source_locale`)
- **surrounding context**: every other chunk in the source document, all visible in the same prompt
- **active chunk wrapping**: the active chunk is wrapped in `<TRANSLATE_THIS>...</TRANSLATE_THIS>`; other chunks appear unwrapped as context only
- **intake context**: mode / register / strategy / source_locale / target_locale / domain (see [`orthogonal-axes.md`](orthogonal-axes.md))
- **glossary slice**: only the glossary terms whose source forms appear in the active chunk (not the entire glossary — see Glossary injection strategy below)
- **placeholder map**: token IDs `⟦P:NN⟧` present in the active chunk and a description of what each masks (variable / inline code / URL / etc.)

### Output contract

- **target-language translation of the wrapped chunk only** — surrounding context must NOT be translated. The writer outputs a single text block in `target_locale`.
- **placeholder tokens preserved**: every `⟦P:NN⟧` from the source MUST appear in the output exactly once, with the same ID, in semantically appropriate position. No new placeholders, no dropped placeholders.
- **no commentary**: just the translation. No "here is the translation:" prefix, no trailing notes.

### Prompt template

The canonical writer prompt is **[`prompt-draft.md`](prompt-draft.md)** (functional copy in `<skill>/references/prompt-draft.md`; SoT in `scripts/canonical/prompts/draft.md`). It declares its required inputs in YAML frontmatter and exposes Mustache-style placeholders (`{{source_lang}}`, `{{target_lang}}`, `{{mode}}`, `{{register}}`, `{{strategy}}`, `{{domain}}`, `{{glossary_terms}}`, `{{document_context_with_translate_this_marker}}`) for skill-side templating.

### Pseudo-prompt sketch (illustrative — actual rendering uses `prompt-draft.md`)

```
You are translating from {source_locale} to {target_locale}.
Mode: {mode}. Register: {register}. Strategy: {strategy}. Domain: {domain}.

Below is the source document. Translate ONLY the chunk wrapped in
<TRANSLATE_THIS>...</TRANSLATE_THIS>. Use the surrounding context for
consistency, but do not translate it.

Preserve every ⟦P:NN⟧ token exactly as-is — same count, same IDs.

Glossary (only terms relevant to this chunk):
- {source_term_1} → {target_term_1}    [domain: {domain}, source: {tier}]
- ...

<DOCUMENT>
{chunk_0}
{chunk_1}
<TRANSLATE_THIS>
{chunk_active}
</TRANSLATE_THIS>
{chunk_3}
...
</DOCUMENT>

Output only the translation of the wrapped chunk.
```

---

## 3. REFLECT — Critic Role

### Input contract

- **source chunk**: same active chunk used in DRAFT
- **draft v1**: the writer's output for that chunk
- **intake context**: mode / register / strategy / source_locale / target_locale / domain
- **intent** (transcreation mode only): the persuasion / CTA / behavioural target the source aims to land. Sourced from the intake-spec `intent` field (see `translation-intake/SKILL.md` once D2 lands). Required by the Effectiveness axis in `prompt-reflect-5d.md`; not used by the 4D prompt.
- **glossary slice**: same slice supplied to DRAFT (so the critic can verify glossary compliance)
- **untranslatability flags** (if any): from Layer 2 source analysis

### Output contract

- **structured JSON critique** — one array per axis. Empty array `[]` if no concerns.
- **4D in default modes** (literal / faithful / localized) — Accuracy, Fluency, Style, Terminology. See [`4d-reflection.md`](4d-reflection.md).
- **5D in transcreation mode** — adds Effectiveness as the 5th axis. See [`5d-effectiveness.md`](5d-effectiveness.md).
- **NO rewrite**. The critic produces critique only; producing a rewrite is a role violation. IMPROVE owns the rewrite.

### Prompt templates

- **4D critic prompt** (literal / faithful / localized modes): **[`prompt-reflect-4d.md`](prompt-reflect-4d.md)** — declares `axes: [accuracy, fluency, style, terminology]` and `applies_to: [translation-i18n, translation-doc, translation-creative (faithful mode), translation-audit]`.
- **5D critic prompt** (transcreation mode only): **[`prompt-reflect-5d.md`](prompt-reflect-5d.md)** — adds an `effectiveness` axis and is scoped to `applies_to: [translation-creative (transcreation mode)]`.

The skill chooses between the 4D and 5D prompt files based on the active mode (see §6 — Mode → Reflection Axes).

### Output schema (4D form)

```json
{
  "accuracy":    [{"issue": "...", "suggestion": "..."}, ...],
  "fluency":     [{"issue": "...", "suggestion": "..."}, ...],
  "style":       [{"issue": "...", "suggestion": "..."}, ...],
  "terminology": [{"issue": "...", "suggestion": "..."}, ...]
}
```

In transcreation mode, add `"effectiveness": [...]` as a 5th key.

---

## 4. IMPROVE — Reviser Role

### Input contract

- **source chunk**: same active chunk
- **draft v1**: the writer's output
- **REFLECT critique**: the structured JSON from the critic
- **intake context**: mode / register / strategy / source_locale / target_locale / domain
- **glossary slice**: same slice as before

### Output contract

- **draft v2** — a revised translation that incorporates the critique
- **placeholder tokens preserved** — same count and IDs as source, identical to the DRAFT contract
- **NO new reasoning beyond critique**. The reviser does not introduce critique items the critic did not raise. If the reviser disagrees with a critique item, leave that item unaddressed (and surface it in audit trail) rather than overriding it; structural disagreement should bubble up to a re-run of REFLECT, not be silently buried in IMPROVE.
- **no commentary** — output is the v2 translation only

### Prompt template

The canonical reviser prompt is **[`prompt-improve.md`](prompt-improve.md)**. It declares `inputs: [draft_v1, critique_json]` and `output: revised_translation`.

---

## 5. Cross-chunk Windowing

TA's windowing pattern is preserved exactly. For an N-chunk document:

- **One LLM call per chunk per role** (so 3N calls total for the core loop, before verification)
- **Each call's prompt re-emits the whole document**, but only the active chunk is wrapped in `<TRANSLATE_THIS>`
- The model sees what came before and what comes after, providing **cross-chunk consistency** (pronoun resolution, term reuse, register continuity) without forcing each chunk to be translated in isolation

This is more token-expensive than chunked-and-isolated translation but produces measurably more coherent output on long documents. Token cost grows quadratically with document length × number of chunks; the chunking threshold (next section) is calibrated to keep typical documents within budget.

---

## 6. Chunking

- **Tokenizer**: `tiktoken` (GPT family BPE; widely available across runtimes)
- **Threshold**: 2000 tokens per chunk (TA convention)
- **Boundary**: prefer paragraph / sentence boundaries; never split inside a placeholder token, code block, or HTML / markdown structural element

If the document is below the threshold, it is a single chunk and the windowing degenerates to a normal prompt (no surrounding context exists).

---

## 7. Placeholder Preservation

Hard requirement, enforced as M1 gate ([`verification-gates.md`](verification-gates.md)):

```
count(target ⟦P:*⟧) == count(source ⟦P:*⟧)
{IDs in target} == {IDs in source}   # set equality
```

Every role (DRAFT and IMPROVE) outputs translations that preserve the placeholder set exactly. The critic checks this in REFLECT (under Accuracy if a placeholder is dropped, under Fluency if mis-positioned). The M1 gate hard-checks this on the v2 output before the placeholder map is applied to restore real values.

Placeholders are introduced in Layer 2 protect-pass and removed in Layer 5 restore-pass; the core loop never sees the unmasked values, which is what makes the loop format-agnostic.

---

## 8. Glossary Injection Strategy

Only glossary terms whose **source forms appear in the active chunk** are injected into the role prompts. Per chunk, recompute the relevant slice. Rationale:

- Avoids context bloat from the full glossary (~10K+ entries)
- Avoids irrelevant-term contamination (the model overusing or hallucinating terms that are not actually in the source)
- Each injected entry includes its tier (L1 project / L2 bundled / L3 web / L4 LLM-fallback) and source for the audit trail

The lookup is performed per chunk via `lib/glossary.py`'s `lookup()` against every candidate term in the source chunk; only matched entries flow into `{{glossary_terms}}` of the writer / critic / reviser prompts.

See [`audit-trail-spec.md`](audit-trail-spec.md) for how glossary resolutions are recorded.

---

## 9. Mode → Reflection Axes

The reflection axis count is mode-dependent (modes are defined in [`orthogonal-axes.md`](orthogonal-axes.md)):

| Mode            | Reflection prompt              | Axes |
| --------------- | ------------------------------ | ---- |
| `literal`       | [`prompt-reflect-4d.md`](prompt-reflect-4d.md) | 4D — Accuracy, Fluency, Style, Terminology |
| `faithful`      | [`prompt-reflect-4d.md`](prompt-reflect-4d.md) | 4D |
| `localized`     | [`prompt-reflect-4d.md`](prompt-reflect-4d.md) | 4D |
| `transcreation` | [`prompt-reflect-5d.md`](prompt-reflect-5d.md) | 5D — adds Effectiveness |

Skills route per their declared modes:

- `translation-i18n`, `translation-doc`, `translation-audit` → 4D only.
- `translation-creative` → 4D in `faithful` mode, 5D in `transcreation` mode.

The axis-count switch happens at prompt-selection time (i.e., the skill picks `prompt-reflect-4d.md` or `prompt-reflect-5d.md` before issuing the REFLECT call); the writer and reviser prompts are mode-independent.

---

## 10. Output Handling

For an N-chunk document the loop produces:

1. **Per-chunk artefacts** — `draft_v1`, `critique_json`, `draft_v2` for each chunk (3 LLM calls per chunk per pass).
2. **Concatenation** — `draft_v2` chunks are concatenated **in source order** to form the final translated document.
3. **Placeholder restoration** — the M1 gate (see [`verification-gates.md`](verification-gates.md)) confirms the placeholder set on the concatenated v2 matches the source, then Layer 5 restore-pass swaps `⟦P:NN⟧` tokens back to their masked originals. The core loop itself never emits restored output.
4. **Audit trail** — every `(chunk_index, role, prompt_inputs, output)` triple is appended to the audit log. Critique JSON is preserved verbatim. See [`audit-trail-spec.md`](audit-trail-spec.md).

The concatenation is whitespace-respecting: chunk boundaries chosen by the chunker (paragraph / sentence) determine the separators; the loop does not insert or strip whitespace at chunk seams.
