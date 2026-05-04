# Lens: Rhetoric (universal core / language-variant router)

> **Sources**: this file is a router; primary sources live in the variants below.
> - English / Western (`lens-rhetoric-anglo.md`): Toulmin (1958) + Burke (1945)
> - Japanese (`lens-rhetoric-ja.md`): Hinds (1983, 1987) + Oh (2025)
> - Chinese (`lens-rhetoric-zh.md`): 劉勰《文心雕龍》六觀

> **Cultural-sensitivity flag** 🔴 **high**: This lens is culturally sensitive. The methods and primary sources that ground it differ meaningfully across English, Japanese, and Chinese contexts. **Do not apply analytical questions from this file directly** — select a language variant first.

## Why this is a router, not a content file

Rhetoric — the structure of persuasive and argumentative texts — is the most cultural-sensitive lens in `deconstruct-toolkit`. The Anglo / Japanese / Chinese rhetorical traditions developed independently and resolved different problems:

- **Anglo (Toulmin + Burke)**: explicit claim-grounds-warrant chain; argument coherence; pentadic motive analysis
- **Japanese (Hinds + kishōtenketsu)**: reader-responsible language; 起承転結 4-part with "ten" (turn) as central; modern academic shifted to 序論-本論-結論 hybrid
- **Chinese (劉勰 文心雕龍 六觀)**: 位體 / 置辭 / 通變 / 奇正 / 事義 / 宮商 — aesthetic-rhetorical-relational synthesis; 1500-year canon

A "universal rhetoric lens" that synthesized all three would silently privilege one tradition (most likely Anglo, given training-data bias). Per [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md), each tradition is given its own variant file.

## Variant selection

Choose ONE variant before applying:

| Artifact register | Variant | Primary sources |
|---|---|---|
| Primarily English / Western | [`lens-rhetoric-anglo.md`](lens-rhetoric-anglo.md) | Toulmin (1958) + Burke (1945) |
| Primarily Japanese | `lens-rhetoric-ja.md` (shipping later in v0.2.0) | Hinds (1983, 1987) + Oh (2025) |
| Primarily Chinese (TC or SC) | `lens-rhetoric-zh.md` (shipping later in v0.2.0) | 劉勰《文心雕龍》六觀 |
| Mixed / ambiguous | Ask user OR apply 2 variants in parallel and report divergence | — |
| Korean / Vietnamese / Thai / other | Fall back to `-anglo` with explicit caveat: "this lens is not grounded in your artifact's cultural register; treat findings as suggestive, not definitive." | (see ADR-0004 §"Out of scope") |

See [`protocols/lens-variant-selection.md`](../protocols/lens-variant-selection.md) for the language-detection algorithm.

## Plugin scope

`deconstruct-toolkit` ships rhetoric variants for **EN / JA / ZH only**. This is a permanent scope decision per [ADR-0004 §"Out of scope"](../../../docs/adr/0004-cultural-lens-variants.md). Variants for other languages require maintainer competence in the target language's primary sources + a fixture corpus.

## See also

- [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md) — cultural-lens-variant pattern
- [`protocols/lens-variant-selection.md`](../protocols/lens-variant-selection.md) — full routing algorithm
- Sister lenses also routed by language: `lens-persuasion.md` / `lens-genre.md` / `lens-frame.md`
