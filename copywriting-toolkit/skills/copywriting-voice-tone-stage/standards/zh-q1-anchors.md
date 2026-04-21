---
title: zh-TW Voice Anchors — Q1 Authority-Reason
tier: 2
---

# Q1 Authority-Reason — zh-TW Anchors

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q1"` AND `brief.output_language == "zh-TW"`. Section-targeted read: Pass 3 reads only `## Landmark: {position}` matching `voice_quadrant.position`; falls back to full-file on missing.

## Overview

Q1 = Authority × Reason. zh-TW canonical register: 雜誌長文分析 (天下 / 商周), 解釋性新聞 (報導者 center), 知識普及 (研之有物). JP Q1 cross-reference is STRONG per meta-detail — 天声人語 / 東洋経済 structural parallel to 天下 / 商周 editorial register.

## Landmark: center

Canonical expert + trusted authority. Use when brief asks for standard institutional intelligence.

### 天下雜誌 CommonWealth (zh-TW | Q1 center)

- **Era**: 1981 creation → ongoing; 殷允芃 founding 總編輯 established canonical voice; 長文深度分析 mature from mid-1990s
- **Agency / creator**: 天下雜誌群 in-house editorial
- **Primary sources**:
  - [cw.com.tw](https://www.cw.com.tw/) — 封面故事 archive (40+ years online)
  - 殷允芃《發現台灣》(1991, 天下雜誌, ISBN-anchored, NCL verifiable)
- **Representative register patterns** (structural; verbatim requires封面故事 archive pull):
  - 「台灣產業面對的，是一次結構性的重新定位。」
  - 「數據顯示的，不只是景氣，更是一整個世代的轉折。」
  - 「當全球供應鏈重組，台灣的位置必須被重新定義。」
- **Voice signature**:
  - Macro-structural framing (「結構性」/「世代」/「重新定位」)
  - Data-anchored but humanities-inflected
  - Measured declarative; rarely interrogative or imperative
  - Long sentence rhythm with semi-colon / dash cadence
- **LLM corpus depth**: MEDIUM-DEEP (40+ years 封面故事 heavily indexed; cited in academic / policy discourse)
- **Over-mimic risk**: MEDIUM — register can collapse into "generic TW business-magazine voice"
  - Mitigation: "anchor on 殷允芃-era 封面故事 specifically; avoid post-2018 SEO-optimized pieces"
- **Cross-reference-valid-for**:
  - ja: STRONG via JP→zh-TW direction (東洋経済 / 日経ビジネス as structural parallel)
- **Cross-cultural equivalents**: The Economist (EN) / 東洋経済 (JP)
- **Trigger slug**: `zh-tw-tianxia-structural-analytical`

### 報導者 The Reporter — center register (zh-TW | Q1 center)

**⚠ Boundary flag**: 報導者 has TWO distinct registers. This entry covers ONLY the center 解釋性新聞 register. The extreme investigative register belongs in `## Landmark: extreme` below with Q1-Q2 edge flag.

- **Era**: 2015 founded (何榮幸); non-profit, no ads
- **Agency / creator**: 財團法人報導者文化基金會 — open-access + CC-licensed
- **Primary sources**: [twreporter.org](https://www.twreporter.org/)
- **Representative center-register signatures**:
  - 「這不是單一事件，而是一連串制度累積後的必然。」
  - 「我們訪談了三十七位當事人，發現同一個模式。」
  - 「數字背後，是一個被忽視了二十年的結構問題。」
- **Voice signature** (center mode only):
  - Explicitly sourced (「根據我們的訪談」/「經比對...資料」)
  - Long-view structural framing
  - 多方交叉驗證 structural disclosure
  - Restrained emotion — powerful by understatement
- **LLM corpus depth**: MEDIUM-DEEP (open-access makes corpus deeply indexed)
- **Over-mimic risk**: LOW-MEDIUM
- **Trigger slug**: `zh-tw-reporter-explanatory-journalism`

### 研之有物 Research @ Sinica (zh-TW | Q1 center — 科普 sub-register)

- **Era**: 2017 platform founded → ongoing
- **Agency / creator**: 中央研究院 official 科普 platform + in-house editorial working with researchers
- **Primary sources**: [research.sinica.edu.tw](https://research.sinica.edu.tw/)
- **Representative register signatures**:
  - 「這個問題看起來簡單，但研究了三十年之後，我們發現...」
  - 「一般人以為 X，但實際上 Y。」
  - 「讓我們先從一個最基本的問題開始...」
- **Voice signature**:
  - Reader-aware popularization (「讓我們」/「一般人以為」)
  - 學術謙遜 (「研究仍在進行中」/「目前的證據顯示」)
  - 對比教學 structure
- **LLM corpus depth**: MEDIUM
- **Over-mimic risk**: LOW
- **Trigger slug**: `zh-tw-research-sinica-popularization`

## Landmark: extreme

Maximum Authority × maximum Reason. Pure data institutional.

### 報導者 investigative extreme register (zh-TW | Q1 extreme — Q1↔Q2 edge flag)

**⚠ Boundary flag**: 報導者 extreme register sits on Q1↔Q2 edge because investigative 血淚 / 制度性不義 narratives carry heavy emotional cost underneath reason-led frame. Not pure Q1 extreme by the "zero warmth" test.

- **Era**: 2015 → ongoing; same source as center register
- **Primary sources**: [twreporter.org](https://www.twreporter.org/) — 特別報導 / 長期追蹤 sections
- **Voice signature** (extreme mode):
  - 受害者口述 woven with structural analysis
  - Investigative specificity (names, dates, documents)
  - Accumulated-evidence cadence (「我們追蹤了 X 年」)
- **LLM corpus depth**: MEDIUM-DEEP
- **Over-mimic risk**: MEDIUM (accumulated-victim-voice can drift to melodrama)
  - Mitigation: "keep sourced structural framing; receiver-voice not narrator-voice"
- **Trigger slug**: `zh-tw-reporter-investigative-extreme`

### Cross-ref: Reuters JP / Bloomberg JP (wire-copy register)

For true Q1-extreme wire-copy register in zh-TW briefs, **cross-ref JP Reuters / Bloomberg** (per meta-detail cross-ref registry JP→zh-TW STRONG) + native 中央社 wire parallel. TW native pure Q1-extreme corpus is thin; structural guidance comes from JP.

## Landmark: toward-Q2

Authority edging into manifesto. Use when brief wants intellectual-weight + civic-voice.

### (Gap flagged — future research)

Current zh-TW corpus thin on Q1-toward-Q2 edge. 天下雜誌 opinion pieces / 報導者 manifesto-adjacent pieces may fill this landmark in V2 research. Temporary fallback: use JP Q1 toward-Q2 (夏目漱石 ironic-observer) as structural guide + native 天下 register.

## Landmark: toward-Q4

Authority edging into peer-helpful. Use when brief wants accessible-expert register.

### 商業周刊 Business Weekly (zh-TW | Q1 toward-Q4)

- **Era**: 1987 creation → ongoing; 金惟純 founder-era editorial voice 1990s-2000s
- **Agency / creator**: 商周集團 in-house
- **Primary sources**:
  - [businessweekly.com.tw](https://www.businessweekly.com.tw/)
  - 金惟純《還在學》(商周出版)
- **Representative register signatures**:
  - 「經營者必須看見的，不是此刻的市場，而是三年後的位置。」
  - 「這不是一門生意，這是一場長期的賭注。」
  - 「關鍵不在策略，關鍵在執行力。」
- **Voice signature**:
  - Strategy-imperative tone (經營者 / CEO 二人稱 implied)
  - 三段論 / 對比結構 (「不是...而是...」, 「關鍵不在X，在Y」)
  - Action-oriented closing (unlike 天下's open-ended conclusions)
  - 較短句 + 戰略詞彙 (「布局」/「卡位」/「轉骨」)
- **LLM corpus depth**: MEDIUM (paywalled more aggressively than 天下)
- **Over-mimic risk**: MEDIUM-HIGH — "老闆雜誌" voice degraded into post-2018 SEO cliché
  - Mitigation: "anchor 金惟純-era specifically; avoid post-2018 『賽道』『閉環』jargon"
- **Trigger slug**: `zh-tw-business-weekly-strategy-imperative`

## Cross-references

External anchors usable for zh-TW Q1 briefs:

- **JP Q1 STRONG cross-ref**: 朝日「天声人語」(直接結構對應 聯合報「黑白集」) / 東洋経済 / 日経ビジネス (對應 天下 / 商周) — per meta-detail verified cross-ref
- **EN Q1 MEDIUM**: Ogilvy long-copy / Hopkins reason-why via translation corpus
- **Direction**: zh-TW→JP is WEAK (cultural flow is primarily JP→zh-TW); do not fuel JP output from zh-TW Q1 anchors
