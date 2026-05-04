# Lens: Genre (universal core / language-variant router)

> **Sources**: this file is a router; primary sources live in the variants below.
> - English / Western (`lens-genre-anglo.md`): Swales 1990 + Bhatia 1993
> - Japanese (`lens-genre-ja.md`): Swales/Bhatia (scaffolding) + 甲田直美 + 木下是雄『理科系の作文技術』(中公新書, 1981) + Hinds 1987 reader-responsibility + JP 拝啓-formula handbooks
> - Chinese (`lens-genre-zh.md`): Swales/Bhatia (scaffolding) + 行政院《文書處理手冊》(112年6月修正本) + 公文程式條例 + Loi & Evans 2010 + Kirkpatrick & Xu 2012 (八股 legacy) + 台大寫作教學中心 (緒論 sub-moves)

> **Cultural-sensitivity flag** 🔴 **high**: This lens is culturally sensitive. Genre conventions — what canonical move structures recognizable document types follow — are language-and-culture specific. Swales/Bhatia's CARS and 7-move sales letter are derived from English-academic and Western-DM artifacts; Japanese and Chinese have distinct genre canons. **Do not apply analytical questions from this file directly** — select a language variant first.

## Why this is a router, not a content file

Document genres developed within their language's literary, academic, and business cultures:

- **Anglo (Swales + Bhatia)**: CARS 3-move research-paper introduction; 7-move sales letter; Western proposal genre
- **Japanese**: dual mode — modern academic uses 序論-本論-結論 (Western-influenced); literary / op-ed / business uses 起承転結; 拝啓 / 時候の挨拶 / 主文 / 末文 / 敬具 formula for business letters
- **Chinese**: 緒論-本論-結論 modern academic; ZH business 公文 genres (函 / 通知 / 報告 / 請示) with prescribed move structures; 八股 historical influence on modern argument

Anglo move analyses do not capture JP business letter formula or ZH 公文 register. Per [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md), each tradition is given its own variant file.

## Variant selection

Choose ONE variant before applying:

| Artifact register | Variant | Primary sources |
|---|---|---|
| Primarily English / Western | [`lens-genre-anglo.md`](lens-genre-anglo.md) | Swales (1990) + Bhatia (1993) |
| Primarily Japanese | [`lens-genre-ja.md`](lens-genre-ja.md) | Swales/Bhatia + 甲田直美 + 木下是雄 1981 + Hinds 1987 + 拝啓-formula handbooks; 序論-本論-結論 + 起承転結 dual-mode |
| Primarily Chinese (TC or SC) | [`lens-genre-zh.md`](lens-genre-zh.md) | Swales/Bhatia + 行政院《文書處理手冊》112年版 + 公文程式條例 + Loi & Evans 2010 + Kirkpatrick & Xu 2012 + 台大寫作教學中心 |
| Mixed / ambiguous | Ask user OR apply 2 variants in parallel | — |
| Korean / Vietnamese / Thai / other | Fall back to `-anglo` with caveat | (see ADR-0004 §"Out of scope") |

See [`protocols/lens-variant-selection.md`](../protocols/lens-variant-selection.md) for the language-detection algorithm.

## Dual-mode warning (Japanese)

Modern Japanese **academic writing has explicitly rejected 起承転結** in favor of Western-style 序論-本論-結論 (per `shouronbun.com` consensus + 甲田直美 textbook). However, **literary / op-ed / business / journalistic Japanese** still uses kishōtenketsu. The `-ja` variant ships with explicit register detection — academic vs non-academic determines which move structure to apply.

## Plugin scope

`deconstruct-toolkit` ships genre variants for **EN / JA / ZH only**. This is a permanent scope decision per [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md).

## See also

- [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md) — cultural-lens-variant pattern
- [`protocols/lens-variant-selection.md`](../protocols/lens-variant-selection.md) — full routing algorithm
- Sister lenses also routed by language: `lens-rhetoric.md` / `lens-persuasion.md` / `lens-frame.md`
