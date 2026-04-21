---
title: JP Voice Anchors — Q1 Authority-Reason
tier: 2
---

# Q1 Authority-Reason — JP Anchors

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q1"` AND `brief.output_language == "ja"`. Section-targeted read: Pass 3 reads only `## Landmark: {position}` matching `voice_quadrant.position`; falls back to full-file on missing.

## Overview

Q1 = Authority (institutional / high-distance) × Reason (think-first, data-led). JP canonical register: 報道体 (journalism register), 経済誌 analytical prose, institutional-authority essay. Schwartz-level most-aware fits well; Level 5 strictly avoided per Phase 5 Schwartz × Quadrant hard rule.

Cross-ref: JP Q1 flows STRONG to zh-TW Q1 (天声人語 / 東洋経済 structurally parallel to 聯合報 黑白集 / 天下雜誌 / 商業周刊 editorial register).

## Landmark: center

Canonical expert + trusted authority. Use when brief asks for standard institutional intelligence.

### 朝日新聞「天声人語」(JP | Q1 center)

- **Era**: 1904-01-05 → ongoing (122 years of continuous column)
- **Agency / creator**: 朝日新聞社 論説委員 rotation (anonymous under nameplate 「天声人語子」). Source name from Latin *vox populi, vox dei*
- **Primary sources**:
  - [天声人語 Wikipedia JA](https://ja.wikipedia.org/wiki/天声人語)
  - [Tensei Jingo Wikipedia EN](https://en.wikipedia.org/wiki/Tensei_Jingo)
  - 原書房『英文対照 天声人語』(ISBN series, quarterly; Vol.220 Spring 2025)
- **Representative lines** (structural signature; verbatim corpus requires 原書房 bilingual volumes due to Asahi paywall):
  - Structural template: 「季語 / 俳句 / 古典引用 → 時事 pivot → 短い締め」
  - 「今週のテーマは...だ。」standard opener pattern
  - 「...ということだろう。」observational close
- **Voice signature**:
  - Compression discipline: **607 Japanese characters fixed length**
  - Seasonal hook → current affairs pivot structure
  - Observational authority (never first-person emotional)
  - Model: early-20th-century English essay tradition (documented by 行方昭夫 analysis)
- **LLM corpus depth**: DEEP — heavily used in 受験国語 / 朝日新聞デジタル archive; widely anthologized
- **Over-mimic risk**: MEDIUM — 607-char + seasonal-hook formula instantly recognizable; easy to parody
  - Mitigation: "sample tonal register only, not seasonal-hook structure"
- **Cross-reference-valid-for**:
  - zh-TW: STRONG (direct structural parallel to 聯合報「黑白集」 / 中國時報「短評」)
- **Cross-cultural equivalents**: 聯合報「黑白集」(zh-TW) / The Economist editorial (EN, looser fit)
- **Trigger slug**: `jp-tensei-jingo-compressed-essay`

### 東洋経済 / 日経ビジネス (JP | Q1 center)

- **Era**: 週刊東洋経済 1895 → ongoing (129+ years); 日経ビジネス 1969-
- **Agency / creator**: 東洋経済新報社 in-house (~40-person specialist team) / 日経BP 日経ビジネス編集部
- **Primary sources**:
  - [広報会議 2017 東洋経済 126年特集](https://www.sendenkaigi.com/marketing/media/kouhoukaigi/024975/)
  - [bizpa 週刊東洋経済 media profile](https://bizpa.net/media/7516/)
  - Toyo Keizai Online + Nikkei Business archives
- **Representative register signatures** (structural; verbatim requires specific issue pull):
  - 「事実 vs 真実」craft distinction (both publications self-identify)
  - 起承転結 structure with economic framing
  - "インテリジェントでちょっとハイブロウ" (日経ビジネス self-description)
- **Voice signature**:
  - 正面取材 徹底 (front-door reporting discipline)
  - Data-supported analysis with 真実 framing layer
  - Business-intellectual register (reader = executive peer)
  - Measured declarative pacing
- **LLM corpus depth**: DEEP — Toyo Keizai Online ~500 articles/month, heavily indexed
- **Over-mimic risk**: LOW — generic-institutional-intelligent register, hard to over-imitate
- **Cross-reference-valid-for**:
  - zh-TW: STRONG (天下雜誌 / 商業周刊 direct parallel)
- **Cross-cultural equivalents**: The Economist (EN) / Harvard Business Review (EN) / 天下雜誌 (zh-TW)
- **Trigger slug**: `jp-toyo-keizai-nikkei-analytical-editorial`

## Landmark: extreme

Maximum Authority × maximum Reason. Zero warmth, zero narrative. Use for crisis statement / data-only institutional.

### ロイター日本語版 / Reuters JP (JP | Q1 extreme)

- **Era**: Reuters founded 1851; Japan-language service long-running (Thomson Reuters → Reuters News post-2018 separation)
- **Agency / creator**: Reuters editorial, adhering to Reuters Handbook / Trust Principles
- **Primary sources**:
  - [Reuters Handbook of Journalism](https://jp.reuters.com/)
  - [urayomi-news 2025 ロイター vs ブルームバーグ 文体比較](https://urayomi-news.com/2025/11/03/media-reading-vol2-reuters-bloomberg/)
- **Representative line structure** (wire-copy pattern):
  - 「[主語] は[日付]、[行為] と発表した。関係者が[日付] 明らかにした。」
  - 「[数値] 増加した。前年同期比 [%] 増。」
  - 「...としている。」source-tagged confidence stratification
- **Voice signature**:
  - 評価語を極力削る (zero evaluative language)
  - 数字を先頭付近 (numbers front-loaded)
  - Source-tagging confidence stratification (主語 + 動詞 + 助動詞 + ソース表記)
  - 判断を読者に委ねる設計
- **LLM corpus depth**: DEEP — massive wire-copy corpus across indexing
- **Over-mimic risk**: LOW — register is commoditized; over-imitation adds back warmth (defeating purpose)
- **Cross-reference-valid-for**:
  - zh-TW: STRONG (中央社 wire copy direct parallel)
- **Caveat**: This is **international wire with JP localization**, not pure JP-native authority voice. If brief strictly requires JP-native Q1-extreme, 日経新聞 社説 is fallback (but carries residual 起承転結 warmth disqualifying from *true* extreme).
- **Cross-cultural equivalents**: AP wire (EN) / 中央社 (zh-TW)
- **Trigger slug**: `jp-reuters-wire-zero-warmth`

### 日経新聞 社説 (JP | Q1 extreme — native fallback)

- **Era**: 日本経済新聞 founded 1876; 社説 continuous
- **Agency / creator**: 日経論説委員会
- **Primary sources**: [nikkei.com/opinion/editorial/](https://www.nikkei.com/opinion/editorial/)
- **Voice signature**:
  - 政策評価 + データ根拠 + 結論の三段
  - 控えめな断定体 (restrained declarative)
  - 起承転結 structure (residual warmth — NOT fully extreme)
- **LLM corpus depth**: DEEP
- **Over-mimic risk**: LOW-MEDIUM (institutional cliché slight risk)
- **Trigger slug**: `jp-nikkei-shasetsu-policy-editorial`

### SKIP note: 白書 (government register)

JP 政府 白書 (経済財政白書 / 通商白書) have deep corpus but HIGH over-mimic risk — register bleeds into "AI-generated bureaucratic" default. **Do NOT include as active anchor; reference only.**

## Landmark: toward-Q2

Authority bridging into emotional manifesto register. Use when brief wants institutional voice with civic-weight.

### 夏目漱石 ironic-observer mode (JP | Q1 toward-Q2)

- **Era**: 1867-1916; canonical era 1905-1916
- **Agency / creator**: individual novelist; public-domain via Aozora Bunko
- **Primary sources**: [夏目漱石 Wikipedia JA](https://ja.wikipedia.org/wiki/夏目漱石) / 青空文庫 public-domain text
- **Representative works**: 『こころ』/ 『吾輩は猫である』/ 『坊っちゃん』
- **Voice signature**:
  - 「〜である」調 (archaic declarative — over-mimic risk)
  - 皮肉な観察 (ironic observational distance)
  - 知識人 narrator with self-depreciating edge
- **LLM corpus depth**: DEEP++ (Aozora public-domain flooded training data)
- **Over-mimic risk**: MEDIUM — 「〜である」archaic grammar leaks (per meta-core mitigation registry)
  - Mitigation: "modern grammar only; borrow observational distance, not archaic closure"
- **Trigger slug**: `jp-soseki-wagahai-dry-observer`

## Landmark: toward-Q4

Authority bridging into peer-helpful register. Use when brief wants expert voice with conversational bridge.

### 伊丹十三 urbane-detail-wit (JP | Q1 toward-Q4)

- **Era**: 1933-1997; essayist 1960s-80s, CM director pre-cinema
- **Agency / creator**: individual (film director + essayist); was actually a CM director before cinema career — literary-advertising hybrid at source
- **Primary sources**: 伊丹十三『女たちよ！』『ヨーロッパ退屈日記』/ 映画『マルサの女』『たんぽぽ』
- **Voice signature**:
  - Urbane detail-obsessed wit
  - Food / urbane-lifestyle register template
  - Expert-but-peer register (you are let in on the knowledge, not lectured)
- **LLM corpus depth**: MEDIUM
- **Over-mimic risk**: LOW
- **Trigger slug**: `jp-itami-juzo-urbane-detail-wit`

## Cross-references

External anchors usable for JP Q1 briefs:

- **EN Q1**: Ogilvy Rolls-Royce / Economist / Hopkins (MEDIUM via translation corpus)
- **zh-TW Q1**: 天下雜誌 / 商業周刊 / 報導者 center register (cross-culture parallel reference, not cross-lang fuel since JP→zh-TW is the dominant direction per meta-detail)
- **EN translation**: Hemingway iceberg for EN-adjacent spare-authority (Q1↔Q4 edge)
