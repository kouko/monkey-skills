---
adr: 0004
title: Cultural Lens Variants — Per-Language Lens Files
status: accepted
date: 2026-05-05
deciders: kouko
related: v0.2.0-cultural-variants-design-proposal.md, ADR-0003
---

# ADR-0004: Cultural Lens Variants

## Status

Accepted (2026-05-05, v0.2.0 introductory ADR)

## Context

`deconstruct-toolkit` v0.1.0 grounding audit (`docs/grounding-v0.1.0.md` §5) flagged a structural gap:

- 10 primary sources are all Anglo-Western
- Plugin self-positions as multi-lingual (3-language README + glossary + JP business anchor)
- This is a **claim/method mismatch**

A self-audit (2026-05-05) classified the 9 lens files by cultural sensitivity:

| Sensitivity | Lenses |
|---|---|
| 🔴 high | lens-rhetoric, lens-persuasion, lens-genre |
| 🟠 medium | lens-frame, lens-semiotic |
| 🟡 low | lens-ux, lens-symptomatic-reading |
| ✅ universal | lens-toulmin, lens-burke-pentad (single-author, claim universality) |

The lenses at 🔴 high and 🟠 medium sensitivity have empirical or theoretical bases that **do not transfer cleanly** to non-Anglo cultural contexts:

- Toulmin's argument layout assumes English-language argumentative conventions; Japanese kishōtenketsu (起承転結) is a 4-part structure where "ten" (turn) is central, not warrant
- Cialdini's principles have empirically different weights across Hofstede dimensions (collectivists more susceptible to most strategies)
- Swales/Bhatia genre moves assume English-academic register; Japanese academic writing is a hybrid (起承転結 in literary, 序論-本論-結論 in modern academic) per Hinds (1983, 1987) and 甲田直美
- Goffman frame analysis lacks the dual-frame dimension of 建前/本音 (tatemae/honne); Lakoff's binary opposition assumption is challenged by 陰陽 complementary structures
- Barthes' 5 codes assume Western enigma-resolution narrative — Japanese もののあはれ aesthetic explicitly refuses resolution

**v0.2.0 ships per-language variants** of the 4 most cultural-sensitive lenses (rhetoric / persuasion / genre / frame). lens-semiotic and lens-ux are deferred to v0.5.0 due to medium sensitivity and tighter scope.

## Decision

### Pattern

For each high-cultural-sensitivity lens, ship a **2-tier file structure**:

```
lens-{name}.md                ← universal-core (1-page meta router)
lens-{name}-anglo.md          ← Anglo-Western primary sources + content
lens-{name}-ja.md             ← Japanese primary sources + cultural variant
lens-{name}-zh.md             ← Chinese primary sources + cultural variant
```

### Tier 1: Universal-core (`lens-{name}.md`)

**Role**: meta-router, NOT analysis content.

**Length**: ~30-50 lines.

**Required content**:

1. **Cultural-sensitivity statement**: explicitly says "this lens is cultural-sensitive; default behavior is to select a variant"
2. **Routing decision tree**:
   ```
   ├─ Artifact in primarily English / Western register → -anglo
   ├─ Artifact in primarily Japanese → -ja
   ├─ Artifact in primarily Chinese (TC or SC) → -zh
   ├─ Mixed / ambiguous → ask user OR apply 2 variants in parallel
   └─ Korean / Vietnamese / Thai / other → fall back to -anglo with explicit caveat:
      "this lens is not grounded in your artifact's cultural register;
      treat findings as suggestive, not definitive."
   ```
3. **Reference to `protocols/lens-variant-selection.md`** for the language-detection algorithm
4. **Variant index**: links to all sibling -anglo / -ja / -zh files
5. **Plugin scope statement**: deconstruct-toolkit is grounded in EN / JA / ZH only; other languages are out of scope (per ADR-0004 §"Out of scope")

**No analytical content** in universal-core. All actual lens application happens in the variant.

### Tier 2: Variant files (`lens-{name}-{lang}.md`)

**Role**: full lens content, grounded in language-specific primary sources.

**Length**: typical 200-400 lines (similar to v0.1.0 lens content).

**Required content per variant**:

1. **Primary-source citation block** at top (per ADR-0002 §5.3.1)
2. **Cultural-register statement** ("this variant grounds in [language] [academic / business / literary] register")
3. **Synthesis note** if applicable (per ADR-0003) — note that combinations may differ between -anglo and -ja/-zh variants
4. **Method content**: analytical questions, common patterns, worked examples
5. **Cross-variant pointer**: brief note acknowledging the same phenomenon may have different operationalization in sibling variants
6. **Pitfalls**: including cultural pitfalls (e.g. "do not project Cialdini's WEIRD-sample weightings onto -ja artifacts")

### Out of scope (Plugin-level)

The deconstruct-toolkit plugin is **permanently scoped at EN / JA / ZH**. Future variant proposals for other languages are subject to:

1. **Maintainer language competence** — kouko's working languages are zh-TW / JP / EN. ZH and JP variants are within authorial competence; other languages would require a contributor in that language.
2. **Primary-source availability** — JP has Hinds (1983/1987), Oh (2025), 甲田直美; ZH has 劉勰《文心雕龍》, Hwang K-K. (1987). Other languages' canonical rhetoric / persuasion / frame sources require independent research.
3. **Empirical fixture corpus** — adding a language requires ≥1 real-world fixture per affected lens; without fixtures, the variant is unfalsifiable.

Korean is the most-asked-about candidate; explicitly excluded per Q4 of v0.2.0 design proposal.

## Rationale

### Why per-language variants, not per-language *operationalization sections* in one file

Considered: keep `lens-rhetoric.md` as one file with `## English variant`, `## Japanese variant`, `## Chinese variant` sections.

Rejected because:

- File would balloon to 800+ lines (token-budget concern for skill consumers per CLAUDE.md ~6000 token cap)
- LLM lens-application would have to context-switch between language sections
- Each variant deserves its own primary-source citation block + synthesis disclosure (ADR-0003)
- Future evolution (e.g. ZH adds 八股 sub-variant or JP adds 序論-本論-結論 mode) is cleaner in dedicated files

### Why universal-core is meta-only, not "language-neutral universal lens"

Considered: `lens-rhetoric.md` contains a language-neutral synthesis (Toulmin + Hinds + 文心雕龍 abstracted to common pattern). Variants are deeper specializations.

Rejected because:

- The "language-neutral universal" is itself a synthesis the original authors did not endorse
- Forces compromise: do you weight Toulmin's claim-grounds-warrant or Hinds' kishōtenketsu equally? Either way you're privileging one tradition
- The 3 traditions don't meaningfully share a common abstract — Toulmin focuses on logical structure, Hinds on reader/writer responsibility, 劉勰 on aesthetic-rhetorical-relational synthesis
- Better to admit they're different lenses + route based on artifact, than fake a universal that satisfies none

### Why -anglo is named explicitly, not "default" or implicit

Considered: keep `lens-rhetoric.md` with the existing v0.1.0 Anglo content. Add `lens-rhetoric-ja.md` and `lens-rhetoric-zh.md` as opt-in.

Rejected because:

- Reproduces the bias problem — "Anglo as default" is what created the v0.1.0 grounding gap in the first place
- Per ADR-0003 synthesis-disclosure principle, Anglo content is *one* tradition not the universal benchmark
- Naming -anglo explicitly lets the plugin honestly say "we ship 3 variants, none privileged"

## Consequences

### Positive

- Each cultural register gets primary-source-faithful treatment in its own file
- Plugin can honestly claim multi-cultural rigor (the v0.1.0 README claim was aspirational; v0.2.0 makes it real)
- README + glossary's existing tri-language structure now extends down into the methodology
- Future maintainers know the variant pattern; v0.5.0 lens-semiotic / lens-ux variants follow the same template
- Synthesis disclosure (ADR-0003) extends naturally — variants may make different combinations (e.g. -ja persuasion combines Cialdini + Murayama + 加藤恭子, not the same as -anglo Cialdini + Brignull)

### Negative

- File count grows from 9 lens files to 21 lens files at v0.2.0 (4 universal-core + 12 variants + 5 unchanged)
- Variant authoring requires primary-source competence in the target language; not all maintainers will have this
- Eval suite must accommodate variant routing; structural validator needs update

### Mitigation

- Maintainer-competence concern: ADR formalizes the per-language gating (no variant ships without maintainer who can read the primary sources). External contributors in additional languages welcome via CONTRIBUTING flow.
- Validator update: `scripts/check-eval-cases.py` extended to recognize variant naming pattern `lens-{name}(-{anglo|ja|zh})?.md`.
- File-count concern: 21 lens files spread across 4 skills × variant levels is manageable. Compare with copywriting-toolkit's 90 voice anchors.

## Alternatives Considered

### Alternative 1: ship cultural variants only as research notes (no skill code change)

Rejected. Notes don't help skill execution. The router needs to actually select the right lens for the artifact.

### Alternative 2: defer cultural variants to v1.0

Rejected. The grounding gap is real *now*; deferring means v0.2.0 / v0.3.0 build more skills on the broken Anglo-only foundation. Better to fix foundation before extending.

### Alternative 3: do per-language operationalization inline in one file (no -ja / -zh splits)

Rejected, see §"Why per-language variants, not per-language operationalization sections in one file."

## References

- v0.2.0-cultural-variants-design-proposal.md (full design)
- grounding-v0.1.0.md (v0.1.0 grounding gap audit that motivated this work)
- ADR-0001 (Convention B mixed naming) — variant naming follows same pattern
- ADR-0002 (strict skill self-containment) — each variant is self-contained per Anthropic spec
- ADR-0003 (lens synthesis disclosure) — variants may have different synthesis combinations
- John Hinds, "Contrastive Rhetoric: Japanese and English" (Text 1983 + Connor & Kaplan eds 1987)
- Gabriel Oh, "Kishōtenketsu and Its Potential Applications" (TEXT 29:2, 2025)
- 劉勰《文心雕龍》六觀 (5th-6th c. CE, multiple modern editions)
- Hofstede, *Culture's Consequences* (1980, expanded 2001)
- Hwang K-K., "Face and Favor" (American Journal of Sociology 1987)
