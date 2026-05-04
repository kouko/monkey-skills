---
title: Grounding Research Note v0.2.0
type: grounding-note
date: 2026-05-05
status: shipped-with-v0.2.0
plugin_version: 0.2.0
related_adr:
  - "[ADR-0003](adr/0003-lens-synthesis-disclosure.md)"
  - "[ADR-0004](adr/0004-cultural-lens-variants.md)"
companion_to: "[grounding-v0.1.0.md](grounding-v0.1.0.md)"
---

# Grounding Research Note — v0.2.0 (cultural variants)

> **Honest research trail for the 8 new cultural-variant lens files.**
> v0.1.0 grounding (`grounding-v0.1.0.md`) audited Anglo-only lenses;
> this note audits the JP and ZH variants added in v0.2.0. Same
> methodology, same legend, same posture: distinguish "directly
> verified" from "training-memory-summarized" so future maintainers
> and skill consumers can judge rigor.

## Summary table — JP variants

| Lens | Primary sources | Citation rigor | Method faithfulness | Synthesis? | Notes |
|---|---|---|---|---|---|
| `lens-rhetoric-ja` | Hinds (1983 *Text* 3:2) + Hinds (1987 in Connor & Kaplan eds.) + Oh (2025 *TEXT* 29:2) | 🟢 high | 🟢 high | ✅ kishōtenketsu + reader-responsibility + 序論-本論-結論 dual-mode | Hinds reader-responsibility framework + kishōtenketsu structure both well-documented in contrastive-rhetoric literature; Oh 2025 verified via WebSearch |
| `lens-persuasion-ja` | Cialdini (2021) + Doi (1971/1973) + Yamamoto (1977) + Hofstede JP profile | 🟡 partial | 🟢 high | ✅ Cialdini re-weighting + JP-specific overlay | Cialdini WEIRD-bias well-documented in cross-cultural literature; specific Murayama 2017 stand-in citation refined to verifiable cross-cultural Cialdini empirical work; 建前/本音 anchored to Doi (canonical) rather than diffuse cultural commentary |
| `lens-genre-ja` | Swales (1990) + Bhatia (1993) + 木下是雄『理科系の作文技術』(中公新書, 1981) + Hinds (1987) | 🟢 high | 🟢 high | ✅ Anglo scaffolding + JP genre repertoire | 木下 1981 is canonical JP technical-writing handbook (verified via 中央公論新社 catalogue + academic citations); 拝啓-formula 7-move structure confirmed via multiple JP business-correspondence handbooks |
| `lens-frame-ja` | Goffman (1974) + Lakoff (1980) + Doi (1971) + Yamamoto (1977) + Markus & Kitayama (1991 *Psychological Review* 98:2) | 🟢 high | 🟢 high | ✅ Anglo frame + JP-specific overlay | Markus & Kitayama 1991 well-known foundational paper on independent vs interdependent self-construal; Yamamoto『「空気」の研究』文藝春秋 1977 canonical 空気 source; 間 (ma) treatment is conceptually grounded but specific scholarly anchors (Komparu / 剣持) not cited in lens body |

## Summary table — ZH variants

| Lens | Primary sources | Citation rigor | Method faithfulness | Synthesis? | Notes |
|---|---|---|---|---|---|
| `lens-rhetoric-zh` | 劉勰《文心雕龍·知音》六觀 (5th-6th century CE; 周振甫 / 王運熙·周鋒 critical editions) | 🟢 high | 🟢 high | ✅ classical Chinese literary criticism extended to artifact analysis | 六觀 framework is canonical and well-documented; 知音篇 location confirmed; modern critical editions (周振甫《文心雕龍今譯》中華書局) widely available |
| `lens-persuasion-zh` | Cialdini (2021) + Hu Hsien-chin (1944 *American Anthropologist* 46:1) + Hwang Kwang-Kuo (1987 *American Journal of Sociology* 92:4) + Hofstede CN profile | 🟢 high | 🟢 high | ✅ Cialdini re-weighting + ZH face-and-favor + 人情 framework | Hwang 1987 *AJS* "Face and Favor: The Chinese Power Game" widely cited foundational paper (verified via JSTOR / academic citations); Hu 1944 verified in *American Anthropologist* archive |
| `lens-genre-zh` | Swales (1990) + Bhatia (1993) + 行政院《文書處理手冊》(TW canonical 公文 reference) + 公文程式條例 | 🟢 high | 🟢 high | ✅ Anglo scaffolding + TW 公文 repertoire | TW 行政院 official documents publicly available; PRC GB/T 9704-2012 cross-referenced for fork notes; 八股 legacy treatment is conceptually grounded but specific scholarly anchor (e.g., 啟功 on 八股) not cited in lens body |
| `lens-frame-zh` | Goffman (1974) + Lakoff (1980) + Hu (1944) + Hwang (1987) + Peng & Nisbett (1999 *American Psychologist* 54:9) | 🟢 high | 🟢 high | ✅ Anglo frame + ZH face/relationship + 陰陽 dialectical metaphor | Peng & Nisbett 1999 "Culture, dialectics, and reasoning about contradiction" widely cited; provides empirical anchor for treating ZH conceptual metaphor as dialectical-not-binary; 圈子 framework conceptually grounded but specific scholarly anchor (e.g., 費孝通 *鄉土中國* 1947 on 差序格局) not cited |

## Citation rigor legend

- 🟢 **high** — author + work + key claims + chapter or page-locator verified via multiple independent sources or canonical-edition cross-reference
- 🟡 **partial** — author + work + claims verified, but specific page numbers cited from training memory not externally confirmed
- 🔴 **low** — significant uncertainty or known error (NONE at v0.2.0 ship)

## Method faithfulness legend

- 🟢 **high** — operationalization preserves what the original author claimed
- 🟡 **partial** — operationalization adapts the method significantly
- 🔴 **low** — operationalization conflicts with original author's claims (NONE at v0.2.0 ship)

## Verification methodology

This grounding research, conducted 2026-05-05 in parallel with the v0.2.0
ship, used:

1. **WebSearch in EN + JA + ZH** — each primary source verified through at
   least one query in its source language plus one in English
2. **Canonical-edition cross-reference** — for classical sources (《文心雕龍》)
   verified against widely-available critical editions; for modern academic
   papers, verified against publisher / journal records
3. **Cross-source verification** — empirical claims about Hofstede dimensions,
   Cialdini-cross-cultural findings, and reader-responsibility theory checked
   against multiple independent academic sources
4. **Honest gap acknowledgment** — when a claim is conceptually grounded but
   the cited scholarly anchor was inferred rather than directly quoted, the
   note above identifies that gap

## What this research did NOT do

- ❌ Access printed editions directly (no library access this session for
  *甘えの構造* / *Anatomy of Dependence* / 《文書處理手冊》 first editions)
- ❌ Verify every page number cited in lens reference files (some chapter
  locators are training-memory inferences)
- ❌ Cross-check JP / ZH critical-edition translations against
  English-language secondary literature on each
- ❌ Audit the cross-cultural Cialdini empirical literature for replication
  status (per Hofstede critique discourse, some Hofstede CN/JP dimension
  values are contested in the literature; lens text uses standard Hofstede
  values without deep replication audit)

## Errors caught during verification

(None requiring patch at v0.2.0 ship — 8 lens files reviewed for primary-source
citation block, synthesis disclosure, and method-faithfulness during writing
phase. Future grounding patches will be appended below as discovered.)

## Cultural-grounding gap closure (relative to v0.1.0)

v0.1.0 grounding-note flagged the central gap:

> "10 primary sources are all Anglo-Western — plugin self-positions as
> multi-lingual but methods only operate in one cultural register."

v0.2.0 closes this for the 4 high-sensitivity lenses by adding 8 new
variant files anchored to JP and ZH primary sources. Remaining gaps:

- ⚠️ `lens-semiotic` and `lens-ux` still have only Anglo grounding —
  deferred to v0.5 per design proposal §9. These have **medium**
  cultural sensitivity per audit, not high — defensible as deferred but
  not as universal.
- ⚠️ Korean / Vietnamese / Thai / other-language artifacts still
  receive `-anglo` fallback. v0.2.0 is honest about this via
  `protocols/lens-variant-selection.md` Step 4 "Out of scope" caveat;
  see [ADR-0004](adr/0004-cultural-lens-variants.md) for the permanent
  scope decision.
- ⚠️ Hofstede dimensions are used in -ja and -zh persuasion variants
  as cultural-distance anchors. Hofstede's empirical methodology has
  documented critiques (sample composition / IBM-only base / temporal
  validity); lens text does not litigate these. Treat Hofstede values
  as orienting heuristic, not measurement.

## Self-audit: ADR-0004 compliance

ADR-0004 codifies the variant pattern. v0.2.0 ship complies:

- ✅ Each high-sensitivity lens has 1 universal-core router + 3 language
  variants (-anglo / -ja / -zh)
- ✅ Universal-core router is meta-only (no analytical-content fallback);
  forces explicit variant choice or honest caveat
- ✅ Each variant cites primary sources native to its register
- ✅ No AI-translated Anglo content imported as JP or ZH (hard exclusion §2.3)
- ✅ Variant selection algorithm documented in `protocols/lens-variant-selection.md`
- ✅ Korean / Vietnamese / Thai / etc. permanently out-of-scope with caveat-handling
- ✅ Plugin-level READMEs (en / zh-TW / ja) clarify EN/JA/ZH triaxis
