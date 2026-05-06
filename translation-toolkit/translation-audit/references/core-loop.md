# Core Loop — DRAFT → REFLECT → IMPROVE

**Status**: canonical reference (Single Source of Truth in `scripts/canonical/`; functional copies in each active skill's `references/`)
**Cross-refs**: [`4d-reflection.md`](4d-reflection.md), [`5d-effectiveness.md`](5d-effectiveness.md), [`orthogonal-axes.md`](orthogonal-axes.md), [`verification-gates.md`](verification-gates.md), [`audit-trail-spec.md`](audit-trail-spec.md)

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

### Pseudo-prompt sketch

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
- **glossary slice**: same slice supplied to DRAFT (so the critic can verify glossary compliance)
- **untranslatability flags** (if any): from Layer 2 source analysis

### Output contract

- **structured JSON critique** — one array per axis. Empty array `[]` if no concerns.
- **4D in default modes** (literal / faithful / localized) — Accuracy, Fluency, Style, Terminology. See [`4d-reflection.md`](4d-reflection.md).
- **5D in transcreation mode** — adds Effectiveness as the 5th axis. See [`5d-effectiveness.md`](5d-effectiveness.md).
- **NO rewrite**. The critic produces critique only; producing a rewrite is a role violation. IMPROVE owns the rewrite.

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

See [`audit-trail-spec.md`](audit-trail-spec.md) for how glossary resolutions are recorded.
