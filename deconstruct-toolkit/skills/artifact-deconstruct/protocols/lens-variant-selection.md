# Protocol: Lens Variant Selection (cultural)

For the 4 cultural-sensitive lenses (rhetoric / persuasion / genre / frame), choose `-anglo` / `-ja` / `-zh` variant based on artifact language and register.

## When this protocol applies

When `protocols/lens-selection.md` has selected one or more of:

- `lens-rhetoric`
- `lens-persuasion`
- `lens-genre`
- `lens-frame`

(NOT for `lens-semiotic` and `lens-ux` — those are not yet variant-split per v0.2.0 scope.)

## Step 1: Detect artifact primary language

Examine the artifact text. Detect the dominant language by character distribution and lexical markers:

| Signal | Indicates |
|---|---|
| ≥80% Latin script + English function words (the / and / of / is) | **English** |
| ≥40% kana (hiragana + katakana) | **Japanese** |
| ≥80% CJK ideographs without kana | **Chinese** (then disambiguate TC vs SC by character distribution: 髮 體 開 vs 发 体 开) |
| Mixed distribution | **Mixed** — go to Step 4 |

For multimodal artifacts (UI screenshots, marketing imagery): use any visible text + page lang attribute + brand context.

## Step 2: Detect cultural register (within the language)

Within the detected language, determine register:

| Register | Signals |
|---|---|
| Academic | Citations, hedging, formal tone, structured headers; modern JP 序論-本論-結論 markers; English IMRaD or CARS markers |
| Business | Marketing copy, pitch decks, sales letters, formal correspondence |
| Literary / Op-ed | Narrative or argumentative prose for general readership; JP newspaper columns; ZH 雜文 |
| Political / Public | Speech, manifesto, government communication |
| Consumer / Marketing | Landing pages, advertising, DTC e-commerce |

Register matters because some variants behave differently within a language. The most important case: **Japanese academic vs literary / business** — modern academic uses 序論-本論-結論 (Western-influenced), literary / business / op-ed uses 起承転結. The `-ja` variants ship with dual-mode treatment.

## Step 3: Select variant

Standard mapping (without complications):

| Detected language | Variant |
|---|---|
| English | `-anglo` |
| Japanese | `-ja` |
| Chinese (TC or SC) | `-zh` |

Pass the register signal to the selected variant so it can apply mode-appropriate sub-treatment (e.g. JP academic vs literary).

## Step 4: Handle complications

### Mixed-language artifact

If the artifact mixes 2+ languages (e.g., bilingual marketing copy, Japanese product page with English brand tagline):

1. Identify which language carries the **persuasive / argumentative weight**
2. Apply that variant first
3. Apply the secondary-language variant **briefly** to sections in that language
4. Report findings as "Primary register: X. Secondary register findings: …"

If both languages carry equal weight, run both variants in parallel and report divergence as analytical insight.

### Korean / Vietnamese / Thai / other languages outside plugin scope

Per [ADR-0004 §"Out of scope"](../../../docs/adr/0004-cultural-lens-variants.md), the plugin is permanently scoped at EN / JA / ZH.

For artifacts in other languages:

1. Apply `-anglo` variant as fallback
2. **Add explicit caveat to the report**: "This lens is not grounded in [LANGUAGE]'s rhetorical / persuasion / genre / frame tradition. Findings may misread culture-specific phenomena. Treat as suggestive, not definitive."
3. If the user explicitly requests deeper analysis, recommend external resources (do not fake competence)

### Translation artifacts

If the artifact is a translation (e.g., a Japanese article translated to English):

1. **Surface signal**: Apply the variant matching the **language you can read** (most often `-anglo` if the translation is into English)
2. **Underlying signal**: Note that the original was in another language; some moves / framings may have been smoothed over in translation
3. If the original is available and you read both languages, apply both variants and report divergence

### Ambiguous register within a language

If a Japanese artifact mixes academic and literary registers (e.g., a 新書 popular-academic book), apply the `-ja` variant in **both modes** and report which dominates.

## Step 5: Report variant choice in output

When generating the deconstruction report, **always state which variant was applied**:

> "Applied lens-rhetoric-ja (kishōtenketsu mode, op-ed register) to artifact at [URL] in Japanese."

This makes the analysis auditable. A reader who disagrees with the variant choice can re-run with a different variant.

## Edge cases and known gaps

| Edge case | Recommended handling |
|---|---|
| Artifact uses code-switching every sentence | Report as "non-mappable to single variant"; analyze sentence-by-sentence with appropriate variant per sentence; expensive but accurate |
| Artifact is bilingual subtitle / closed-caption | Treat the audio language as primary if knowable; otherwise treat each language separately |
| Original-language unknown (e.g., AI-translated to English) | Apply `-anglo` with caveat about translation provenance |
| Hong Kong Cantonese-influenced ZH | Use `-zh` with note that HK register has British colonial-administrative influence on 公文 genre |
| Singaporean / Malaysian Chinese | Use `-zh` with note that local register may differ from PRC / TW |

## Pitfalls

- **Picking variant from author/brand assumption** — Toyota's English landing page is `-anglo` (English-language artifact), not `-ja` (Japanese-brand). The variant is **artifact register**, not **brand origin**.
- **Treating `-anglo` as default for ambiguous cases** — falling back to `-anglo` without caveat reproduces the v0.1.0 grounding gap. Always add the "not grounded in your artifact's culture" caveat when forced to fall back.
- **Forcing one variant on multi-cultural artifact** — better to apply 2 and report divergence than to pretend one fits cleanly.
- **Skipping register detection within Japanese** — academic JP and literary JP have different canonical move structures. Without register detection, the `-ja` variant gives the wrong answer for half its potential inputs.
