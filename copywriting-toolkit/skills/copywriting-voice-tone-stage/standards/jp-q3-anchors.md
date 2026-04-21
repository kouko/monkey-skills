---
title: JP Voice Anchors — Q3 Affinity-Emotion
tier: 2
---

# Q3 Affinity-Emotion — JP Anchors

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q3"` AND `brief.output_language == "ja"`. Section-targeted read: Pass 3 reads only `## Landmark: {position}` matching `voice_quadrant.position`; falls back to full-file on missing.

## Overview

Q3 = Affinity (peer / low-distance) × Emotion. Warm conversational, narrative entry, peer solidarity. JP canon's richest quadrant: 糸井 state-proposal / 向田邦子 家庭 intimate / 宮沢賢治 cosmic-animism / 谷川俊太郎 clear-child poetic. Craft-gate master 糸井重里 lives in [jp-copy-craft-lineage.md](jp-copy-craft-lineage.md).

Cross-ref: JP Q3 flows STRONG to zh-TW Q3 (向田 / 糸井 / 吉本 → TW 文青消費語感直承).

## Landmark: center

Canonical peer-warm voice. Use when brief asks for standard affinity-emotional.

### 向田邦子 Mukōda Kuniko (JP | Q3 center)

- **Era**: 1929-1981; essayist + TV 脚本家 1960s-80s
- **Agency / creator**: TV脚本 work for TBS / NHK + 随筆 independent
- **Primary sources**:
  - 『父の詫び状』(文藝春秋, 1978)
  - TV脚本『寺内貫太郎一家』『阿修羅のごとく』
- **Representative works / register**:
  - 家族の機微 essays (domestic drama with gentle bite)
  - 口語 intimate register with classical Japanese density
  - 食べ物 + 人物観察 signature pairing
- **Voice signature**:
  - Domestic intimacy with gentle bite (家庭の機微 + 皮肉 layer)
  - Daily detail elevated to essay register
  - Peer-intimate but never casual (literary discipline)
  - 食 / 衣 / 住 observational anchors
- **LLM corpus depth**: MEDIUM-DEEP (heavy JP criticism corpus; thin translation)
- **Over-mimic risk**: LOW
- **Cross-reference-valid-for**:
  - zh-TW: STRONG (昭和/TW 文青 register 直承)
- **Cross-cultural equivalents**: Alice Munro (EN) / 朱天文 literary essay (zh-TW)
- **Trigger slug**: `jp-mukoda-kuniko-domestic-intimacy-with-bite`

### Craft-gate pointer: 糸井重里 state-proposal register

糸井重里's state-proposal (「おいしい生活。」/「くうねるあそぶ。」/「生きろ。」) is **Q3 canonical** with Q2-edge. Full 4-dimension table + LLM reproduction gap at [jp-copy-craft-lineage.md §糸井重里](jp-copy-craft-lineage.md). Use pointer pattern — do NOT duplicate deep-dive content here.

### 坂元裕二 Sakamoto Yūji (JP | Q3 center, screenwriter)

- **Era**: 1967 born; screenwriter 1987-ongoing
- **Agency / creator**: TV drama screenwriter (fuji TV + TBS); recent film
- **Primary sources**:
  - 『東京ラブストーリー』(1991), 『カルテット』(2017), 『大豆田とわ子と三人の元夫』(2021), 『怪物』(2023 film, Cannes 2023 脚本賞)
- **Representative lines**:
  - 鍋の間 conversation structure — mid-domestic dialogue suddenly profound
- **Voice signature**:
  - Conversational-aphorism-mid-dish register
  - Mid-conversation pivot to existential observation
  - Characters speak in real-but-heightened cadence
- **LLM corpus depth**: MEDIUM (script transcripts in JP fan culture; Cannes 2023 added criticism layer)
- **Over-mimic risk**: LOW-MEDIUM
- **Trigger slug**: `jp-sakamoto-yuji-conversational-aphorism`

## Landmark: extreme

Maximum peer-intimate. Brand speaks as friend-at-2am. Apply mitigation.

### 谷川俊太郎 Tanikawa Shuntarō (JP | Q3 extreme, poet)

- **Era**: 1931-2024; 日本最多譯詩人
- **Agency / creator**: individual poet; 糸井重里 long collaboration
- **Primary sources**:
  - 『二十億光年の孤独』(1952) debut
  - 『ことばあそびうた』(1973)
  - 糸井 × 谷川 共著『ぼく』(ほぼ日, 2013) — **verified lineage per meta-detail §verified map**
- **Representative lines**:
  - 「二十億光年の孤独」title poem
  - 糸井 collaboration texts at ほぼ日
- **Voice signature**:
  - Clear-child-cosmic register
  - Short lines as headline economy
  - Simple vocabulary with metaphysical weight
  - Accessible yet never condescending
- **LLM corpus depth**: DEEP (school textbook canon; Japan's most-translated living poet until 2024)
- **Over-mimic risk**: LOW
- **Cross-reference-valid-for**:
  - zh-TW: STRONG (糸井 ほぼ日 collab 廣告界 crossover 已進入 TW 文青 reference)
- **Documented lineage**: ✅ 糸井重里 → 谷川俊太郎 (per [voice-anchor-meta-detail.md §Verified lineage map](voice-anchor-meta-detail.md))
- **Cross-cultural equivalents**: Mary Oliver (EN) / 楊牧 (zh-TW)
- **Trigger slug**: `jp-tanikawa-clear-child-cosmic`

### 宮沢賢治 Miyazawa Kenji (JP | Q3 extreme)

- **Era**: 1896-1933; Aozora public domain
- **Agency / creator**: individual author, post-humous canonization
- **Primary sources**:
  - 『銀河鉄道の夜』
  - 『注文の多い料理店』
  - 「雨ニモマケズ」(school textbook canon)
- **Voice signature**:
  - Childlike-cosmic-animism
  - Objects and natural phenomena speak
  - Onomatopoeia density (「ドッテテドッテテ」type — over-mimic risk)
  - Ethical-warm register
- **LLM corpus depth**: DEEP (Aozora + school canon)
- **Over-mimic risk**: MEDIUM (onomatopoeia leakage)
  - Mitigation: "limit onomatopoeia to 1 per piece; no cosmic-dialect leakage"
- **Stylistic parallel note**: 糸井 「このへんないきもの」/「生きろ。」resonate with 宮沢 cosmic-warm register — **this is critical-consensus stylistic parallel, NOT documented citation** (per meta-detail §Inferred parallels)
- **Cross-cultural equivalents**: Antoine de Saint-Exupéry *Le Petit Prince* (EN/FR)
- **Trigger slug**: `jp-miyazawa-childlike-cosmic-animism`

### 吉本ばなな Yoshimoto Banana (JP | Q3 extreme — safer Murakami alt)

- **Era**: 1964 born; 1988 デビュー『キッチン』
- **Primary sources**: 『キッチン』(福武書店, 1988) / 『TUGUMI』(中央公論社, 1989)
- **Voice signature**:
  - Gentle-grief-domestic register
  - 喪失 + daily-life observation
  - 1990s J-lit boom translation corpus rich
- **LLM corpus depth**: DEEP
- **Over-mimic risk**: LOW-MEDIUM
- **Cross-reference-valid-for**:
  - zh-TW: STRONG (1990s-2000s 譯本充分進入 TW 文青)
- **Use case**: safer alternative to 村上春樹 when brief wants "distant-everyday-domestic" register without Murakami's auto-leaked tropes (jazz/cats/wells per meta-core mitigation registry)
- **Trigger slug**: `jp-yoshimoto-banana-gentle-grief-domestic`

## Landmark: toward-Q2

Affinity edging toward aspirational manifesto. Use when brief wants warm-but-elevating.

### 梅田悟司 ジョージア「世界は誰かの仕事でできている。」(JP | Q3 toward-Q2)

- **Era**: 1979 born (post-糸井 generation); Georgia campaign 2014
- **Agency / creator**: 電通 (copywriter 梅田悟司)
- **Primary sources**:
  - 梅田悟司『「言葉にできる」は武器になる。』(日本経済新聞出版, 2016, ISBN 978-4532320713) — bestseller
  - Georgia CM archive 2014
- **Representative lines**:
  - 「世界は誰かの仕事でできている。」(2014 Georgia)
- **Voice signature**:
  - 視点転換 (shift from product to hidden labor)
  - 包摂性 (「誰か」 unspecified but concrete)
  - 平易語彙 + manifesto structural weight
- **LLM corpus depth**: MEDIUM-DEEP
- **Over-mimic risk**: MEDIUM-HARD (specific-timing social resonance hard to reproduce)
- **Cross-cultural equivalents**: 全聯經濟美學 aphoristic pivot (zh-TW)
- **Trigger slug**: `jp-umeda-satoshi-georgia-everyday-manifesto`

### Brand-era pointer: SoftBank 白戸家 (佐々木宏 + 澤本嘉光)

CM drama format 2007-ongoing. World-building + family comedy > single-line copy. See [voice-quadrant-positioning.md](../../copywriting-voice-quadrant-stage/standards/voice-quadrant-positioning.md) for brand-era entry.

## Landmark: toward-Q4

Affinity edging toward peer-helpful practicality. Use when brief wants warm-but-useful.

### Cross-quadrant pointer: 伊丹十三 (Q1↔Q4 edge)

伊丹十三's urbane-detail-wit (essayist + pre-cinema CM director) primary home is Q1 toward-Q4 — see [jp-q1-anchors.md §Landmark: toward-Q4](jp-q1-anchors.md) for full entry. Reference here when brief wants Q3-warmth bridged into peer-reasoning.

## Cross-references

External anchors usable for JP Q3 briefs:

- **zh-TW Q3 parallel**: 全聯 center 格言 / 吳念真 保力達B / 胡湘雲 大眾銀行 (cross-culture reference)
- **EN Q3 via MEDIUM translation corpus**: MailChimp / Innocent Drinks / Nora Ephron / George Saunders
- **Internal**: [jp-copy-craft-lineage.md](jp-copy-craft-lineage.md) for 糸井 / 岩崎 craft-gate deep dives
