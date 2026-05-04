# Lens: Persuasion (universal core / language-variant router)

> **Sources**: this file is a router; primary sources live in the variants below.
> - English / Western (`lens-persuasion-anglo.md`): Cialdini 2021 + Brignull 2024
> - Japanese (`lens-persuasion-ja.md`): Cialdini 2021 + Doi 1971 (建前/本音) + Yamamoto 1977 (空気) + Hofstede JP + Orji 2016 (cross-cultural compliance); Brignull dark-pattern table re-weighted for JP register
> - Chinese (`lens-persuasion-zh.md`): Cialdini 2021 + Hu 1944 (面子/臉) + Hwang 1987 *AJS* (關係/人情) + Hofstede CN/TW; Brignull dark-pattern table re-weighted for ZH register + 3 ZH-specific dark patterns (道德綁架/話術/假關係)

> **Cultural-sensitivity flag** 🔴 **high**: This lens is culturally sensitive. Cialdini's empirical base is predominantly US-WEIRD; cross-cultural empirical work (Orji 2016, Hofstede-framed) shows **quantitative weight differences** along power-distance and individualism-collectivism axes — collectivists are MORE susceptible to most strategies, not less. **Do not apply analytical questions from this file directly** — select a language variant first.

## Why this is a router, not a content file

Persuasion mechanisms are universal in *type* (Cialdini's 7 principles appear in every culture) but differ meaningfully in *weighting* and *cultural manifestation*:

- **Anglo (Cialdini + Brignull)**: WEIRD-sample-derived weightings; Brignull dark-pattern taxonomy on Western e-commerce
- **Japanese (Cialdini × Doi × Yamamoto × Hofstede + Orji)**: high power-distance + 老舗 reverence amplifies authority (#4); collectivism amplifies social proof (#3) and unity (#7); 建前/本音 (Doi 1971) layers expression; 婉曲表現 indirect persuasion as virtue (vs Western directness); 空気 (Yamamoto 1977) collective frame-reading
- **Chinese (Cialdini × Hu × Hwang × Hofstede)**: 關係 (guanxi) restructures liking (#5); 面子 (Hu 1944 mianzi vs 臉 lian) entangles authority (#4) and reciprocity (#1); 人情 (Hwang 1987) extends reciprocity into multi-year ledger; ZH-specific dark patterns (道德綁架 / 話術 / 假關係) not in Brignull

Same principles, different weightings, different cultural-script for triggering. Per [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md), each register is given its own variant file.

## Variant selection

Choose ONE variant before applying:

| Artifact register | Variant | Cultural anchor |
|---|---|---|
| Primarily English / Western | [`lens-persuasion-anglo.md`](lens-persuasion-anglo.md) | WEIRD-sample Cialdini + Brignull deceptive design |
| Primarily Japanese | [`lens-persuasion-ja.md`](lens-persuasion-ja.md) | Cialdini + Doi 1971 (建前/本音) + Yamamoto 1977 (空気) + Hofstede JP + Orji 2016 + JP Brignull table |
| Primarily Chinese (TC or SC) | [`lens-persuasion-zh.md`](lens-persuasion-zh.md) | Cialdini + Hu 1944 (面子/臉) + Hwang 1987 (關係/人情) + Hofstede CN/TW + ZH-specific dark patterns |
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
