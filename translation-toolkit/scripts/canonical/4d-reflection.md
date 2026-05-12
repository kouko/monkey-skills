# 4D Reflection — Accuracy / Fluency / Style / Terminology

**Status**: canonical reference (Single Source of Truth in `scripts/canonical/`; functional copies in each active skill's `references/`)
**Cross-refs**: [`core-loop.md`](core-loop.md), [`5d-effectiveness.md`](5d-effectiveness.md), [`orthogonal-axes.md`](orthogonal-axes.md), [`verification-gates.md`](verification-gates.md)

---

## Purpose

Defines the four critique axes used by the REFLECT role of the core loop. The output is a structured JSON object — one array per axis, each entry an `{issue, suggestion}` pair. Empty arrays are valid and expected when the draft is clean on that axis.

The critic produces critique only. **The critic does NOT rewrite** — rewrites are the IMPROVE role's job ([`core-loop.md`](core-loop.md) §4).

In transcreation mode, a 5th axis (Effectiveness) is added — see [`5d-effectiveness.md`](5d-effectiveness.md). In all other modes (literal / faithful / localized — see [`orthogonal-axes.md`](orthogonal-axes.md)), the 4 axes below apply.

---

## Axis 1 — Accuracy

**Definition**: semantic faithfulness; no addition / omission / distortion of source meaning.

**Concerns** (non-exhaustive — the critic should consider all of these per chunk):

- **Dropped clauses** — entire phrases or sentences from the source missing in the target
- **Hallucinated detail** — claims, examples, or qualifiers that appear in the target but have no source basis
- **Mistranslated negations** — "not X" rendered as "X" (or vice versa); double-negation collapse errors
- **Factual drift** — names, dates, places, figures changed (e.g., "東京" rendered as "Tokyo, Japan" when source said only "東京"; or worse, source "1995" rendered as "1985")
- **Mistranslated numbers / proper nouns** — units (km vs miles), currencies, names of people / organizations / products
- **Quantifier drift** — "all" rendered as "many", "some" rendered as "few", "always" rendered as "often"
- **Modal drift** — "must" rendered as "should", "may" rendered as "will"
- **Placeholder integrity** — `⟦P:NN⟧` tokens missing or duplicated (also caught by M1 gate, but flag here so IMPROVE can fix without waiting for M1)

**Mode sensitivity**: in `literal` mode, weight Accuracy strongly (surface fidelity > nuance); in `localized` and `transcreation` modes, expected adaptations (idioms, cultural references) are not Accuracy violations — they are Style / Effectiveness choices.

---

## Axis 2 — Fluency

**Definition**: naturalness in the target language — the translation should read as if originally written in the target.

**Concerns**:

- **Awkward word order** — source-language word order leaking into target (e.g., English SVO order forced onto Japanese SOV; topic-comment structure dropped in zh-TW)
- **Calque** — word-for-word borrowed structure that no native speaker would produce ("make a decision" → 「決定を作る」 instead of 「決定する」)
- **Redundant pronouns** — Japanese / Chinese targets where pronouns are normally dropped but appear because the source had them ("彼は彼の本を彼の机に置いた")
- **Particle / article drift** — Japanese particle (は / が / を / に) misuse; English article (a / an / the) misuse; zh-TW 的 / 之 / 地 / 得 confusion
- **Run-on or fragmented sentences** — target sentence-length distribution differs sharply from source for no reason (one source sentence becomes five fragments, or five short sentences become one run-on)
- **Punctuation mismatch** — half-width / full-width inconsistency; quote style (「」 vs ""); list bullet style; sentence-ending marks (。/. /！)
- **Tense / aspect drift** — Japanese タ形 / 〜ている misuse; Chinese 了 / 過 misuse; English progressive / perfect misuse

---

## Axis 3 — Style

**Definition**: register / rhythm / rhetoric matches the source AND the intended mode (see [`orthogonal-axes.md`](orthogonal-axes.md) for mode and register definitions).

**Concerns**:

- **Register drift** — formal source rendered as casual target (or vice versa); source uses 敬語 / 謙譲語 but target uses plain form
- **Vinay-Darbelnet strategy mismatch** — wrong choice among the 7 procedures for the given source / mode pairing (see Strategy reference below)
- **Tone divergence** — source is wry / sardonic but target reads earnest; source is warm but target reads clinical
- **Sentence-length pattern divergence** — source rhythm (e.g., short-short-long pattern for emphasis) flattened in target
- **Rhetorical-device loss** — parallelism, anaphora, alliteration, rhetorical questions present in source, absent in target
- **Honorific system handling** — Japanese honorific axis (敬語 / 丁寧語 / タメ語) collapsed to single English politeness; English politeness markers ("kindly", "please") not adapted to target's honorific system
- **Markedness drift** — neutral source rendered as marked target (or vice versa); e.g., a generic English noun rendered with an unnecessarily learned 漢語 in Japanese

### Vinay-Darbelnet 7 strategies (style-choice reference)

The 1958 Vinay-Darbelnet taxonomy gives the critic vocabulary for style choices. The critic flags **mismatches** — cases where the wrong strategy was chosen for the source / mode combination. The IMPROVE role applies the corrective strategy.

| # | Strategy | Description | Typical use |
|---|---|---|---|
| 1 | Borrowing | Keep source word as-is | Brand names, untranslatable cultural terms (御朱印 / 紅包) |
| 2 | Calque | Literal phrase-by-phrase loan | "skyscraper" → 摩天楼 / 摩天大樓 (now naturalized) |
| 3 | Literal translation | Word-for-word, structure preserved | Closely related languages, simple declarative sentences |
| 4 | Transposition | Change part of speech | English noun → Japanese verb ("the failure of X" → "Xが失敗したこと") |
| 5 | Modulation | Change point of view | "It is not difficult" → "簡単だ" (negation flip) |
| 6 | Equivalence | Different form, same function | Idioms, proverbs ("It's raining cats and dogs" → 「土砂降り」) |
| 7 | Adaptation | Cultural substitution | "baseball" → "野球" with cultural-context note; ad copy cultural references |

**Mode → strategy bias** (heuristic, not strict):
- `literal` mode favors strategies 1–3
- `faithful` mode favors strategies 1–4
- `localized` mode opens strategies 4–6
- `transcreation` mode admits all 7, with 6–7 dominant

---

## Axis 4 — Terminology

**Definition**: glossary compliance + domain conventions.

**Concerns**:

- **Ignored project glossary** — a term has an L1 (project glossary) entry for the active domain but the target uses a different rendering; this is also enforced by M2 gate ([`verification-gates.md`](verification-gates.md))
- **Inconsistent term within document** — same source term rendered two different ways across chunks (one of the things cross-chunk windowing aims to prevent; the critic catches surviving cases)
- **Wrong-domain term selection** — `key` rendered as 鍵 in a `tech.crypto` context where 暗号鍵 is required; `銀行` rendered as "bank (finance)" in a `tech.data` context that meant "data bank"
- **Unstandardized abbreviations** — TLA / acronym handling: keep / explain / localize choice not consistent across chunks; expansion missing on first use; expansion repeated on every use (depending on register)
- **Bundled glossary not respected** — L2 entry exists but target uses an alternative; allowed only if the alternative is documented in audit trail and consistent within the document
- **Notes ignored** — glossary entry says `⚠️ false friend, NOT 衛生紙` but target uses the false-friend rendering anyway

**Audit-trail link**: every terminology decision (which tier supplied the term, whether the critic flagged a deviation) is recorded in audit trail per [`audit-trail-spec.md`](audit-trail-spec.md) §`glossary_resolution` and §`gate_verdicts.M2`.

---

## Output Format

The REFLECT role outputs a single JSON object. **Empty arrays are valid** and indicate "no concerns on this axis" — they MUST be emitted (do not omit the key).

### 4D form (literal / faithful / localized modes)

```json
{
  "accuracy": [
    {"issue": "draft renders 'must' as 'should' in chunk 2 sentence 3",
     "suggestion": "use 'must' / 必須 / 必要があります"}
  ],
  "fluency": [],
  "style": [
    {"issue": "敬語 register dropped in last paragraph (タメ語 used)",
     "suggestion": "restore です/ます form"}
  ],
  "terminology": [
    {"issue": "'key' rendered 鍵 in a tech.crypto context",
     "suggestion": "use 暗号鍵 per glossary"}
  ]
}
```

### 5D form (transcreation mode)

```json
{
  "accuracy":      [...],
  "fluency":       [...],
  "style":         [...],
  "terminology":   [...],
  "effectiveness": [...]
}
```

See [`5d-effectiveness.md`](5d-effectiveness.md) for the Effectiveness axis specification.

---

## Critic discipline

- **No rewrites**. Critique only. If the critic catches itself starting to rewrite, stop and convert the rewrite into a `suggestion` field.
- **Be specific**. "Awkward phrasing" is useless. "Sentence 3 has English SVO order; Japanese SOV would read more naturally" is actionable.
- **Be silent when correct**. If a draft is clean on an axis, emit `[]`. Do not invent issues to fill space.
- **Cite location** when possible — chunk index, sentence number, or quoted source span — so IMPROVE can target precisely.
- **Single critique per issue**. If the same issue manifests in 5 places, raise it once with all locations rather than 5 nearly identical entries.

---

## Novel-mode 5D literary variant (v0.3.0+)

`translation-novel` defaults to a 5-axis literary critic that adds **Literariness** as a fifth axis distinct from the 4-axis reflect documented here. The literary axis covers:

- **Rhythm** — sentence-cadence / breath-grouping fidelity
- **Euphony** — sound-pattern preservation (alliteration / mora pattern / tonal pacing) where the target language admits a comparable effect
- **Archaism** — appropriate level of period-specific vocabulary / honorific register for the source's period and tone
- **Register-shift fidelity** — narrator-vs-dialogue / formal-vs-casual shifts within the same character

Distinct from creative-mode 5D `Effectiveness` ([`5d-effectiveness.md`](5d-effectiveness.md)), which targets persuasion / CTA landing. Novel-mode 5D targets literary craft.

The 4D reflect (this document) remains available via `intake_spec.reflect_axes='4d'` when the chapter is colloquial-only or when the caller has reason to skip literary judgment.

See [`prompts/reflect-5d-literary.md`](prompts/reflect-5d-literary.md) for the canonical prompt body. See plan v0.3.0 §Decision B for the rationale.
