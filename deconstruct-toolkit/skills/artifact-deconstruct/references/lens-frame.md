# Lens: Frame (universal core / language-variant router)

> **Sources**: this file is a router; primary sources live in the variants below.
> - English / Western (`lens-frame-anglo.md`): Goffman (1974) + Lakoff (1980)
> - Japanese (`lens-frame-ja.md`): Goffman + Lakoff + 建前-本音 + 空気 (kūki) + 間 (ma) + JP-specific conceptual metaphors
> - Chinese (`lens-frame-zh.md`): Goffman + Lakoff + Hwang K-K. (1987) face-and-favor + 關係 (guanxi) + 陰陽 complementary structure

> **Cultural-sensitivity flag** 🟠 **medium**: This lens is culturally sensitive. Goffman's frame analysis was developed on Western daily-life samples; Lakoff's conceptual metaphor structure is claimed universal but specific metaphors differ by language. East Asian cultures have distinct frame phenomena (建前/本音 / 給面子) absent from Goffman, and binary-opposition assumptions (Lakoff) are challenged by complementary structures (陰陽). **Do not apply analytical questions from this file directly** — select a language variant first.

## Why this is a router, not a content file

Frame analysis (social and cognitive) intersects culture in two ways:

1. **Specific frames are culture-bound** — 建前/本音 (tatemae/honne dual frame), 給面子 (mianzi face-work), 関係 / 關係 (guanxi relational frame) are absent or weak in Western samples
2. **Binary opposition assumption** — Lakoff's structural-metaphor analysis presumes binary opposition (us/them, more/less, up/down). Daoist 陰陽 is **complementary**, not oppositional, requiring different operationalization

Variants:

- **Anglo (Goffman + Lakoff)**: Western frame analysis + Western metaphor source domains (war / journey / family / construction)
- **Japanese (+ 建前/本音 + 空気を読む + 間 ma)**: dual-frame layer absent from Goffman; reading-the-air as frame-detection skill; ma (negative space / pause) as frame element; JP-specific metaphors (心 heart-mind, 道 way)
- **Chinese (+ 面子 mianzi + 關係 guanxi + 陰陽 complementary)**: face-work as identity-frame; relational frame as primary social grammar; 陰陽 challenges Lakoff binary assumption

Per [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md), each register is given its own variant file.

## Variant selection

Choose ONE variant before applying:

| Artifact register | Variant | Cultural anchor |
|---|---|---|
| Primarily English / Western | [`lens-frame-anglo.md`](lens-frame-anglo.md) | Goffman (1974) + Lakoff (1980) |
| Primarily Japanese | `lens-frame-ja.md` (shipping later in v0.2.0) | Goffman + Lakoff + 建前/本音 + 空気 + 間 + JP conceptual metaphors |
| Primarily Chinese (TC or SC) | `lens-frame-zh.md` (shipping later in v0.2.0) | Goffman + Lakoff + Hwang K-K. mianzi + 關係 + 陰陽 complementary structure |
| Mixed / ambiguous | Ask user OR apply 2 variants in parallel | — |
| Korean / Vietnamese / Thai / other | Fall back to `-anglo` with caveat | (see ADR-0004 §"Out of scope") |

See [`protocols/lens-variant-selection.md`](../protocols/lens-variant-selection.md) for the language-detection algorithm.

## Plugin scope

`deconstruct-toolkit` ships frame variants for **EN / JA / ZH only**. This is a permanent scope decision per [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md).

## See also

- [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md) — cultural-lens-variant pattern
- [`protocols/lens-variant-selection.md`](../protocols/lens-variant-selection.md) — full routing algorithm
- Sister lenses also routed by language: `lens-rhetoric.md` / `lens-persuasion.md` / `lens-genre.md`
