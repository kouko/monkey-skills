# Lens: Persuasion (universal core / language-variant router)

> **Sources**: this file is a router; primary sources live in the variants below.
> - English / Western (`lens-persuasion-anglo.md`): Cialdini (2021) + Brignull (2024)
> - Japanese (`lens-persuasion-ja.md`): Cialdini × Hofstede × Murayama cross-cultural research + 加藤恭子 / 建前-本音 / 婉曲表現
> - Chinese (`lens-persuasion-zh.md`): Cialdini × Hofstede × Hwang K-K. (1987) face-and-favor + 關係 (guanxi) + 面子 (mianzi)

> **Cultural-sensitivity flag** 🔴 **high**: This lens is culturally sensitive. Cialdini's empirical base is predominantly US-WEIRD; cross-cultural meta-analyses (Murayama, Hofstede-framed) show **quantitative weight differences** along power-distance and individualism-collectivism axes — collectivists are MORE susceptible to most strategies, not less. **Do not apply analytical questions from this file directly** — select a language variant first.

## Why this is a router, not a content file

Persuasion mechanisms are universal in *type* (Cialdini's 7 principles appear in every culture) but differ meaningfully in *weighting* and *cultural manifestation*:

- **Anglo (Cialdini + Brignull)**: WEIRD-sample-derived weightings; Brignull dark-pattern taxonomy on Western e-commerce
- **Japanese (Cialdini × Hofstede × 加藤恭子)**: high power-distance amplifies authority (#4); collectivism amplifies social proof (#3) and unity (#7); 建前/本音 affects how principles get expressed; 婉曲表現 indirect persuasion as virtue (vs Western directness)
- **Chinese (Cialdini × Hofstede × Hwang K-K. mianzi)**: 關係 (guanxi) extends liking (#5); 面子 (face-work) entangles authority (#4) and reciprocity (#1); collectivist social proof (#3) similar to JP

Same principles, different weightings, different cultural-script for triggering. Per [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md), each register is given its own variant file.

## Variant selection

Choose ONE variant before applying:

| Artifact register | Variant | Cultural anchor |
|---|---|---|
| Primarily English / Western | [`lens-persuasion-anglo.md`](lens-persuasion-anglo.md) | WEIRD-sample Cialdini + Brignull deceptive design |
| Primarily Japanese | `lens-persuasion-ja.md` (shipping later in v0.2.0) | Murayama cross-cultural + Hofstede JP + 建前/本音 + 婉曲表現 |
| Primarily Chinese (TC or SC) | `lens-persuasion-zh.md` (shipping later in v0.2.0) | Hwang K-K. mianzi + 關係 (guanxi) + Hofstede CN |
| Mixed / ambiguous | Ask user OR apply 2 variants in parallel | — |
| Korean / Vietnamese / Thai / other | Fall back to `-anglo` with caveat | (see ADR-0004 §"Out of scope") |

See [`protocols/lens-variant-selection.md`](../protocols/lens-variant-selection.md) for the language-detection algorithm.

## Plugin scope

`deconstruct-toolkit` ships persuasion variants for **EN / JA / ZH only**. This is a permanent scope decision per [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md).

## Ethical position verdict (lens-wide rule)

**Regardless of variant**, every detected persuasion mechanism gets one of four ethical positions:

| Position | Meaning |
|---|---|
| 🟢 Transparent | Principle used + user can see and reject |
| 🟡 Gray zone | Principle used + user is unaware |
| 🔴 Manipulation | Creates urgency / false belief |
| ⚫ Dark pattern | Actively deceives, harms user |

This 4-position taxonomy is **cross-cultural**. What differs across variants is **what triggers warrant which position** in the local cultural-script.

## See also

- [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md) — cultural-lens-variant pattern
- [`protocols/lens-variant-selection.md`](../protocols/lens-variant-selection.md) — full routing algorithm
- Sister lenses also routed by language: `lens-rhetoric.md` / `lens-genre.md` / `lens-frame.md`
